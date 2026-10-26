
import feedparser

FEED_URL = "https://docs.databricks.com/aws/en/feed.xml"

feed = feedparser.parse(FEED_URL)

print("Databricks RSS Feed Test")
print("-" * 30)
print("Feed title:", feed.feed.get("title", "Not available"))
print("Articles found:", len(feed.entries))

for article in feed.entries[:5]:
    print("\nTitle:", article.get("title", "Not available"))
    print("Published:", article.get("published", article.get("updated", "Date not available")))
    print("Link:", article.get("link", "Not available"))
