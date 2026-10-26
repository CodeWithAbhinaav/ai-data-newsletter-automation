
import json
import re
import html
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "databricks_articles_2026-10-12_to_2026-10-18.json"
)

DECISIONS_FILE = (
    PROJECT_ROOT / "config" / "duplicate_decisions.json"
)

CLEANED_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "databricks_articles_cleaned.json"
)

DUPLICATE_LOG_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "databricks_duplicates_removed.json"
)

REVIEW_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "databricks_duplicates_review.json"
)


def normalize_text(value):
    """Normalize text so formatting differences don't affect comparison."""
    text = html.unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().casefold()


def get_published_date(article):
    return (
        article.get("published_at_ist")
        or article.get("published", "")
    )


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def clean_articles():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    if not DECISIONS_FILE.exists():
        raise FileNotFoundError(
            f"Duplicate decisions file not found: {DECISIONS_FILE}"
        )

    dataset = load_json(INPUT_FILE)
    decisions_data = load_json(DECISIONS_FILE)

    articles = dataset.get("articles", [])

    # Load decisions that have already been reviewed by a human.
    decisions = {}

    for decision in decisions_data.get("reviewed_decisions", []):
        key = (
            normalize_text(decision.get("title", "")),
            decision.get("published_at_ist", "")
        )
        decisions[key] = decision.get("keep_link", "")

    # Find records with the same title, summary, and publication date.
    groups = defaultdict(list)

    for index, article in enumerate(articles):
        title = normalize_text(article.get("title", ""))
        summary = normalize_text(article.get("summary", ""))
        published = get_published_date(article)

        if title and summary and published:
            key = (title, summary, published)
            groups[key].append((index, article))

    removed_articles = []
    review_groups = []
    kept_indexes = set()
    group_number = 1

    for matches in groups.values():
        if len(matches) == 1:
            kept_indexes.add(matches[0][0])
            continue

        first_article = matches[0][1]

        decision_key = (
            normalize_text(first_article.get("title", "")),
            get_published_date(first_article)
        )

        preferred_link = decisions.get(decision_key, "")

        # A known decision is usable only if its preferred link
        # actually appears in this matching group.
        preferred_matches = [
            (index, article)
            for index, article in matches
            if article.get("link", "") == preferred_link
        ]

        if preferred_link and len(preferred_matches) == 1:
            kept_index, kept_article = preferred_matches[0]
            kept_indexes.add(kept_index)

            for index, article in matches:
                if index != kept_index:
                    removed = article.copy()
                    removed["duplicate_of"] = kept_article.get("link", "")
                    removed["removal_reason"] = (
                        "Duplicate matched a previously reviewed decision."
                    )
                    removed_articles.append(removed)

        else:
            # Unknown or ambiguous groups require manual review.
            group_id = f"NEW-{group_number:03d}"
            review_articles = []

            for index, article in matches:
                flagged = article.copy()
                flagged["duplicate_group"] = group_id
                flagged["review_reason"] = (
                    "Matching title, summary, and date, but no "
                    "matching approved decision was found."
                )
                review_articles.append(flagged)

            review_groups.append({
                "duplicate_group": group_id,
                "number_of_entries": len(review_articles),
                "articles": review_articles
            })

            group_number += 1

    # Keep all unique records and the approved record from each group.
    cleaned_articles = [
        article
        for index, article in enumerate(articles)
        if index in kept_indexes
    ]

    cleaned_data = {
        "source": dataset.get("source", "Unknown"),
        "reporting_period": dataset.get("reporting_period", {}),
        "total_input_articles": len(articles),
        "articles_removed_as_reviewed_duplicates": len(removed_articles),
        "articles_needing_manual_review": sum(
            group["number_of_entries"] for group in review_groups
        ),
        "articles_ready_for_next_step": len(cleaned_articles),
        "articles": cleaned_articles
    }

    duplicate_log = {
        "source": dataset.get("source", "Unknown"),
        "removed_count": len(removed_articles),
        "removed_articles": removed_articles
    }

    review_data = {
        "source": dataset.get("source", "Unknown"),
        "unresolved_group_count": len(review_groups),
        "groups": review_groups
    }

    save_json(CLEANED_FILE, cleaned_data)
    save_json(DUPLICATE_LOG_FILE, duplicate_log)
    save_json(REVIEW_FILE, review_data)

    print("ARTICLE CLEANING SUMMARY")
    print("-" * 35)
    print("Input articles:", len(articles))
    print("Reviewed duplicates removed:", len(removed_articles))
    print(
        "Articles needing manual review:",
        sum(group["number_of_entries"] for group in review_groups)
    )
    print("Articles ready for next step:", len(cleaned_articles))
    print("Duplicate log:", DUPLICATE_LOG_FILE)
    print("Review queue:", REVIEW_FILE)
    print("Cleaned data:", CLEANED_FILE)


if __name__ == "__main__":
    clean_articles()
