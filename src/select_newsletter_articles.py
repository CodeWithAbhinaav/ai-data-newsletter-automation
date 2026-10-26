
import csv
import json
import re
from pathlib import Path


# --------------------------------------------------
# 1. FILE PATHS AND SELECTION SETTINGS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "databricks_articles_ranked.json"
)

OUTPUT_JSON = (
    PROJECT_ROOT / "data" / "processed"
    / "databricks_newsletter_shortlist.json"
)

OUTPUT_CSV = (
    PROJECT_ROOT / "data" / "processed"
    / "databricks_newsletter_shortlist.csv"
)

MAX_ARTICLES = 10
MAX_ARTICLES_PER_CATEGORY = 3


# --------------------------------------------------
# 2. HELPER FUNCTIONS
# --------------------------------------------------

def normalize_text(text):
    """Normalize text for duplicate comparisons."""
    text = (text or "").casefold()
    return re.sub(r"\s+", " ", text).strip()


def get_primary_category(article):
    """
    Use the first category assigned by the ranking script.
    Articles without categories go into a fallback category.
    """
    categories = article.get("categories", [])

    if isinstance(categories, list) and categories:
        return categories[0]

    return "Other"


def get_article_score(article):
    """Safely read an article's ranking score."""
    try:
        return float(article.get("priority_score", 0))
    except (TypeError, ValueError):
        return 0.0


# --------------------------------------------------
# 3. SELECT NEWSLETTER ARTICLES
# --------------------------------------------------

def select_articles(articles):
    """
    Select up to 10 articles in ranking order.

    Rules:
    - Higher scores are considered first.
    - No more than 3 articles per primary category.
    - Duplicate URLs and titles are skipped.
    - Every selected article remains flagged for human review.
    """

    # Sort by score first and publication date second.
    sorted_articles = sorted(
        articles,
        key=lambda article: (
            get_article_score(article),
            article.get("published_at_ist", ""),
        ),
        reverse=True,
    )

    selected = []
    category_counts = {}
    seen_urls = set()
    seen_titles = set()

    skipped_category_limit = 0
    skipped_duplicates = 0

    for article in sorted_articles:
        if len(selected) >= MAX_ARTICLES:
            break

        title = article.get("title", "").strip()
        url = article.get("link", "").strip()

        normalized_title = normalize_text(title)
        normalized_url = normalize_text(url)

        # Skip records without a usable title or URL.
        if not title or not url:
            continue

        # Skip duplicate URLs or identical titles.
        if (
            normalized_url in seen_urls
            or normalized_title in seen_titles
        ):
            skipped_duplicates += 1
            continue

        category = get_primary_category(article)

        # Limit repetition of a single primary category.
        if (
            category_counts.get(category, 0)
            >= MAX_ARTICLES_PER_CATEGORY
        ):
            skipped_category_limit += 1
            continue

        selected_article = article.copy()

        selected_article["primary_category"] = category
        selected_article["selection_status"] = (
            "Selected for editorial review"
        )
        selected_article["needs_human_review"] = True

        selected.append(selected_article)

        seen_urls.add(normalized_url)
        seen_titles.add(normalized_title)

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    return (
        selected,
        category_counts,
        skipped_category_limit,
        skipped_duplicates,
    )


# --------------------------------------------------
# 4. SAVE SHORTLIST
# --------------------------------------------------

def save_json(
    dataset,
    selected,
    category_counts,
):
    """Save the selected articles and selection metadata."""

    output_data = {
        "source": dataset.get("source", "Unknown"),
        "reporting_period": dataset.get(
            "reporting_period", {}
        ),
        "input_article_count": len(
            dataset.get("articles", [])
        ),
        "selected_article_count": len(selected),
        "selection_settings": {
            "maximum_articles": MAX_ARTICLES,
            "maximum_articles_per_primary_category": (
                MAX_ARTICLES_PER_CATEGORY
            ),
        },
        "category_counts": category_counts,
        "editorial_note": (
            "This is an automated shortlist, not a final "
            "newsletter. Review article relevance, accuracy, "
            "timeliness, and topic diversity before publication."
        ),
        "articles": selected,
    }

    with OUTPUT_JSON.open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(
            output_data,
            file,
            indent=2,
            ensure_ascii=False,
        )


def save_csv(selected):
    """Save a spreadsheet-friendly editorial shortlist."""

    csv_fields = [
        "priority_score",
        "priority",
        "title",
        "published_at_ist",
        "primary_category",
        "categories",
        "summary_text",
        "link",
        "ranking_reasons",
        "selection_status",
        "needs_human_review",
    ]

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=csv_fields,
            extrasaction="ignore",
        )

        writer.writeheader()

        for article in selected:
            row = article.copy()

            if isinstance(row.get("categories"), list):
                row["categories"] = ", ".join(
                    row["categories"]
                )

            if isinstance(
                row.get("ranking_reasons"), list
            ):
                row["ranking_reasons"] = "; ".join(
                    row["ranking_reasons"]
                )

            writer.writerow(row)


# --------------------------------------------------
# 5. MAIN PROGRAM
# --------------------------------------------------

def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Ranked articles not found: {INPUT_FILE}\n"
            "Run rank_articles.py first."
        )

    with INPUT_FILE.open(
        "r", encoding="utf-8"
    ) as file:
        dataset = json.load(file)

    articles = dataset.get("articles", [])

    if not articles:
        raise ValueError(
            "The ranked JSON contains no articles."
        )

    (
        selected,
        category_counts,
        skipped_category_limit,
        skipped_duplicates,
    ) = select_articles(articles)

    OUTPUT_JSON.parent.mkdir(
        parents=True, exist_ok=True
    )

    save_json(
        dataset,
        selected,
        category_counts,
    )

    save_csv(selected)

    # --------------------------------------------------
    # 6. PRINT RESULTS
    # --------------------------------------------------

    print("NEWSLETTER SHORTLIST SUMMARY")
    print("-" * 40)
    print("Input articles:", len(articles))
    print("Selected articles:", len(selected))
    print(
        "Skipped due to category limits:",
        skipped_category_limit,
    )
    print(
        "Skipped duplicate records:",
        skipped_duplicates,
    )

    print("\nSELECTED ARTICLES")
    print("-" * 40)

    for number, article in enumerate(
        selected, start=1
    ):
        print(
            f"{number}. "
            f"[{article.get('priority_score', 0)}/10] "
            f"{article.get('title', 'Untitled')}"
        )
        print(
            "   Category:",
            article["primary_category"],
        )
        print(
            "   Priority:",
            article.get("priority", "Unrated"),
        )

    print("\nCATEGORY COUNTS")
    print("-" * 40)

    for category, count in sorted(
        category_counts.items()
    ):
        print(f"{category}: {count}")

    print("\nSaved JSON:", OUTPUT_JSON)
    print("Saved CSV:", OUTPUT_CSV)
    print("\nAll selected articles require human review.")


if __name__ == "__main__":
    main()
