
import json
import re
from datetime import datetime
from pathlib import Path


# --------------------------------------------------
# 1. FILE PATHS AND SETTINGS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "databricks_newsletter_shortlist.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "databricks_newsletter_draft.md"
)

NEWSLETTER_NAME = "AI & Data Weekly"
NEWSLETTER_SOURCE = "Databricks Release Notes"


# Keep categories in a consistent order.
CATEGORY_ORDER = [
    "AI & Agents",
    "Data Engineering & SQL",
    "BI & Analytics",
    "ML & Data Science",
    "Security & Governance",
    "Platform & Developer Tools",
    "Other",
]


# --------------------------------------------------
# 2. HELPER FUNCTIONS
# --------------------------------------------------

def clean_text(text):
    """Remove extra whitespace and basic HTML tags."""
    if not isinstance(text, str):
        return ""

    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def markdown_escape(text):
    """Escape characters that could disrupt Markdown layout."""
    text = clean_text(text)

    text = text.replace("\\", "\\\\")
    text = text.replace("[", "\\[")
    text = text.replace("]", "\\]")
    text = text.replace("|", "\\|")

    return text


def get_categories(article):
    """Return the article's assigned categories."""
    categories = article.get("categories", [])

    if isinstance(categories, list) and categories:
        return categories

    primary = article.get("primary_category")

    if primary:
        return [primary]

    return ["Other"]


def get_summary(article):
    """
    Use the existing summary from the collected data.
    Do not generate unsupported facts or claims.
    """
    summary = (
        article.get("summary_text")
        or article.get("summary")
        or ""
    )

    return clean_text(summary)


def get_reporting_period(dataset):
    """Format the reporting period when available."""
    period = dataset.get("reporting_period", {})

    if isinstance(period, dict):
        start = (
            period.get("start_date")
            or period.get("start")
        )
        end = (
            period.get("end_date")
            or period.get("end")
        )

        if start and end:
            return f"{start} to {end}"

        if start:
            return f"From {start}"

        if end:
            return f"Through {end}"

    if isinstance(period, str) and period.strip():
        return period.strip()

    return "Reporting period not specified"


def get_score(article):
    """Safely read an article's priority score."""
    try:
        return float(article.get("priority_score", 0))
    except (TypeError, ValueError):
        return 0.0


def format_score(score):
    """Display whole-number scores without decimals."""
    if score.is_integer():
        return str(int(score))

    return str(score)


def format_date(article):
    """Return the publication date when available."""
    published = (
        article.get("published_at_ist")
        or article.get("published")
        or ""
    )

    if not published:
        return "Date not available"

    return str(published)


# --------------------------------------------------
# 3. GROUP ARTICLES BY CATEGORY
# --------------------------------------------------

def group_articles(articles):
    """
    Group stories by their first assigned category.
    Articles with multiple categories appear only once.
    """
    grouped = {}

    for article in articles:
        categories = get_categories(article)
        primary_category = categories[0]

        grouped.setdefault(
            primary_category, []
        ).append(article)

    # Sort articles within each category by score.
    for category in grouped:
        grouped[category].sort(
            key=lambda article: (
                get_score(article),
                article.get("published_at_ist", ""),
            ),
            reverse=True,
        )

    return grouped


# --------------------------------------------------
# 4. BUILD THE NEWSLETTER
# --------------------------------------------------

def build_newsletter(dataset):
    """Create the complete Markdown newsletter draft."""

    articles = dataset.get("articles", [])

    if not articles:
        raise ValueError(
            "The shortlist contains no articles."
        )

    reporting_period = get_reporting_period(dataset)
    grouped_articles = group_articles(articles)

    lines = []

    # Header
    lines.append(f"# {NEWSLETTER_NAME}")
    lines.append("")
    lines.append(
        "*A curated update on AI, data engineering, "
        "analytics, and data platforms.*"
    )
    lines.append("")
    lines.append(f"**Reporting period:** {reporting_period}")
    lines.append(f"**Source feed:** {NEWSLETTER_SOURCE}")
    lines.append(f"**Stories selected:** {len(articles)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Table of contents
    lines.append("## In This Issue")
    lines.append("")

    ordered_categories = [
        category
        for category in CATEGORY_ORDER
        if category in grouped_articles
    ]

    # Include any unexpected categories after known categories.
    for category in sorted(grouped_articles):
        if category not in ordered_categories:
            ordered_categories.append(category)

    for category in ordered_categories:
        count = len(grouped_articles[category])
        lines.append(f"- **{category}** ({count})")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Article sections
    story_number = 0

    for category in ordered_categories:
        category_articles = grouped_articles[category]

        lines.append(f"## {category}")
        lines.append("")

        for article in category_articles:
            story_number += 1

            title = markdown_escape(
                article.get("title", "Untitled article")
            )

            url = (
                article.get("link")
                or article.get("url")
                or ""
            ).strip()

            summary = markdown_escape(
                get_summary(article)
            )

            priority = article.get(
                "priority", "Unrated"
            )

            score = get_score(article)
            date = markdown_escape(
                format_date(article)
            )

            lines.append(
                f"### {story_number}. [{title}]({url})"
                if url
                else f"### {story_number}. {title}"
            )
            lines.append("")

            lines.append(
                f"**Priority:** {priority} "
                f"({format_score(score)}/10)"
            )
            lines.append(f"**Published:** {date}")
            lines.append("")

            if summary:
                lines.append(summary)
            else:
                lines.append(
                    "*No summary was available in the source data. "
                    "Add a verified summary during editorial review.*"
                )

            lines.append("")

            # Preserve original source link for verification.
            if url:
                lines.append(
                    f"**Original source:** [Read the release note]({url})"
                )
                lines.append("")

            lines.append(
                "**Editorial status:** Pending human review"
            )
            lines.append("")
            lines.append("---")
            lines.append("")

    # Editorial review checklist
    lines.append("## Editorial Review Checklist")
    lines.append("")
    lines.append(
        "- [ ] Verify each story against its original source."
    )
    lines.append(
        "- [ ] Confirm publication dates and reporting period."
    )
    lines.append(
        "- [ ] Check that each summary accurately reflects the source."
    )
    lines.append(
        "- [ ] Confirm technical names, release status, and migration details."
    )
    lines.append(
        "- [ ] Remove stories that are repetitive or not useful to readers."
    )
    lines.append(
        "- [ ] Review all priority scores; they are automated estimates."
    )
    lines.append(
        "- [ ] Add an introduction and closing note before publication."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        "*Draft generated automatically. "
        "Stories have not been independently fact-checked. "
        "Review before distributing.*"
    )
    lines.append("")

    return "\n".join(lines)


# --------------------------------------------------
# 5. MAIN PROGRAM
# --------------------------------------------------

def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Newsletter shortlist not found: {INPUT_FILE}\n"
            "Run select_newsletter_articles.py first."
        )

    with INPUT_FILE.open(
        "r", encoding="utf-8"
    ) as file:
        dataset = json.load(file)

    articles = dataset.get("articles", [])

    if not articles:
        raise ValueError(
            "No articles were found in the shortlist."
        )

    newsletter = build_newsletter(dataset)

    OUTPUT_FILE.parent.mkdir(
        parents=True, exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w", encoding="utf-8"
    ) as file:
        file.write(newsletter)

    # --------------------------------------------------
    # 6. PRINT SUMMARY
    # --------------------------------------------------

    print("NEWSLETTER DRAFT GENERATED")
    print("-" * 40)
    print("Newsletter:", NEWSLETTER_NAME)
    print("Source:", NEWSLETTER_SOURCE)
    print("Articles included:", len(articles))
    print(
        "Reporting period:",
        get_reporting_period(dataset),
    )
    print("\nOutput file:")
    print(OUTPUT_FILE)
    print("\nFormat: Markdown (.md)")
    print("Editorial review required: Yes")


if __name__ == "__main__":
    main()
