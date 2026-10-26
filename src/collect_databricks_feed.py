
import json
import feedparser
from datetime import datetime, timezone
from pathlib import Path

# Locate the project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Official Databricks RSS feed
FEED_URL = "https://docs.databricks.com/aws/en/feed.xml"

# Output file
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "databricks_feed.json"


def collect_feed():
    print("Collecting Databricks release notes...")

    feed = feedparser.parse(FEED_URL)

    # Basic validation
    if feed.get("bozo", 0):
        raise RuntimeError("The feed could not be parsed reliably.")

    if not feed.entries:
        raise RuntimeError("The feed returned no articles.")

    articles = []

    for entry in feed.entries:
        article = {
            "title": entry.get("title", "").strip(),
            "link": entry.get("link", ""),
            "published": entry.get(
                "published",
                entry.get("updated", "")
            ),
            "summary": entry.get(
                "summary",
                entry.get("description", "")
            ),
        }

        articles.append(article)

    # Save the collected data
    dataset = {
        "source": "Databricks Release Notes",
        "feed_url": FEED_URL,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "total_articles": len(articles),
        "articles": articles,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            dataset,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"Articles collected: {len(articles)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    collect_feed()
