
import feedparser
from collections import Counter

FEED_URL = "https://docs.databricks.com/aws/en/feed.xml"

feed = feedparser.parse(FEED_URL)
articles = feed.entries

print("DATABRICKS DATA QUALITY CHECK")
print("-" * 35)

# 1. Check whether the feed was parsed successfully
print("Feed parsing issue:", feed.get("bozo", 0))
print("Total entries:", len(articles))

# 2. Check for missing important fields
missing_titles = 0
missing_links = 0
missing_dates = 0

for article in articles:
    if not article.get("title"):
        missing_titles += 1

    if not article.get("link"):
        missing_links += 1

    if not article.get("published") and not article.get("updated"):
        missing_dates += 1

print("\nMISSING DATA")
print("Missing titles:", missing_titles)
print("Missing links:", missing_links)
print("Missing dates:", missing_dates)

# 3. Check duplicate links
links = [
    article.get("link")
    for article in articles
    if article.get("link")
]

duplicate_links = len(links) - len(set(links))

print("\nDUPLICATE CHECK")
print("Duplicate links:", duplicate_links)

# 4. Find titles appearing more than once
titles = [
    article.get("title", "").strip()
    for article in articles
    if article.get("title", "").strip()
]

title_counts = Counter(titles)
repeated_titles = {
    title: count
    for title, count in title_counts.items()
    if count > 1
}

print("Titles appearing more than once:", len(repeated_titles))

for title, count in list(repeated_titles.items())[:5]:
    print(f"- {title} ({count} entries)")
