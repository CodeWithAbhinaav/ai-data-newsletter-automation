
import json
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "databricks_feed.json"
OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "databricks_articles_2026-10-19_to_2026-10-25.json"
)

# India Standard Time (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Reporting window: Monday 19 Oct through Sunday 25 Oct
START_DATE = datetime(2026, 10, 19, 0, 0, tzinfo=IST)
END_DATE = datetime(2026, 10, 26, 0, 0, tzinfo=IST)


def parse_publication_date(date_text):
    """Convert a feed date into a timezone-aware datetime."""
    if not date_text:
        return None

    try:
        # Common RSS date format
        published_date = parsedate_to_datetime(date_text)
    except (TypeError, ValueError, OverflowError):
        try:
            # Also support ISO-format dates
            published_date = datetime.fromisoformat(
                date_text.replace("Z", "+00:00")
            )
        except (TypeError, ValueError, OverflowError):
            return None

    # Don't guess the timezone if the date has none
    if published_date.tzinfo is None:
        return None

    return published_date.astimezone(IST)


def filter_articles():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Raw data file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    articles = dataset.get("articles", [])

    selected_articles = []
    invalid_dates = 0

    for article in articles:
        date_text = article.get("published", "")
        published_at = parse_publication_date(date_text)

        if published_at is None:
            invalid_dates += 1
            continue

        if START_DATE <= published_at < END_DATE:
            filtered_article = article.copy()
            filtered_article["published_at_ist"] = (
                published_at.isoformat()
            )
            selected_articles.append(filtered_article)

    # Save the filtered dataset separately
    result = {
        "source": dataset.get("source", "Unknown"),
        "reporting_period": {
            "start": START_DATE.isoformat(),
            "end_exclusive": END_DATE.isoformat(),
            "timezone": "IST",
        },
        "total_raw_articles": len(articles),
        "articles_in_period": len(selected_articles),
        "articles_skipped_due_to_invalid_dates": invalid_dates,
        "articles": selected_articles,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

    print("WEEKLY ARTICLE FILTER")
    print("-" * 35)
    print("Raw articles:", len(articles))
    print("Reporting period: 12–18 October 2026 (IST)")
    print("Articles in period:", len(selected_articles))
    print("Invalid or missing dates:", invalid_dates)
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    filter_articles()
