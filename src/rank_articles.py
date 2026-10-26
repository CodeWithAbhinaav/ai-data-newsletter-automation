
import csv
import html
import json
import re
from pathlib import Path


# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "databricks_articles_cleaned.json"
)

OUTPUT_JSON = (
    PROJECT_ROOT / "data" / "processed"
    / "databricks_articles_ranked.json"
)

OUTPUT_CSV = (
    PROJECT_ROOT / "data" / "processed"
    / "databricks_articles_ranked.csv"
)


# --------------------------------------------------
# 2. TEXT CLEANING AND KEYWORD MATCHING
# --------------------------------------------------

def clean_html(text):
    """Convert HTML text into readable plain text."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def contains_keyword(text, keyword):
    """Match a phrase without matching it inside unrelated words."""
    pattern = (
        r"(?<!\w)"
        + re.escape(keyword.casefold())
        + r"(?!\w)"
    )
    return bool(re.search(pattern, text.casefold()))


def find_matches(text, keywords):
    """Return keywords found in the supplied text."""
    return [
        keyword
        for keyword in keywords
        if contains_keyword(text, keyword)
    ]


# --------------------------------------------------
# 3. TOPIC CLASSIFICATION
# --------------------------------------------------

TOPIC_RULES = {
    "AI & Agents": [
        "genie",
        "agent",
        "ai runtime",
        "foundation model",
        "gemini",
        "llm",
        "model serving",
        "unity gateway",
        "skills api",
        "agentic code converter",
    ],
    "Data Engineering & SQL": [
        "sql",
        "lakeflow",
        "pipeline",
        "replication",
        "cdc",
        "streaming",
        "delta table",
        "lakebase",
        "postgres",
        "mysql",
        "repartition",
        "ingestion",
    ],
    "BI & Analytics": [
        "power bi",
        "dashboard",
        "metric view",
        "pivot table",
        "analytics",
        "adbc driver",
    ],
    "Security & Governance": [
        "security",
        "compliance",
        "privilege",
        "governance",
        "private link",
        "private connectivity",
        "ingress policy",
        "governed tag",
        "clean room",
    ],
    "ML & Data Science": [
        "feature views",
        "model training",
        "fine-tune",
        "serverless gpu",
        "machine learning",
    ],
}

TOPIC_WEIGHTS = {
    "AI & Agents": 3,
    "Data Engineering & SQL": 3,
    "BI & Analytics": 3,
    "Security & Governance": 2,
    "ML & Data Science": 2,
    "Platform & Developer Tools": 1,
}


def classify_article(title, summary):
    """
    Use the title to identify the main topic.
    Summary-only matches are recorded separately.
    """
    title_text = clean_html(title).casefold()
    summary_text = clean_html(summary).casefold()

    categories = []
    evidence = {}
    secondary_categories = []

    for category, keywords in TOPIC_RULES.items():
        title_matches = find_matches(title_text, keywords)
        summary_matches = find_matches(summary_text, keywords)

        if title_matches:
            categories.append(category)
            evidence[category] = {
                "matched_in": "title",
                "title_matches": title_matches,
                "summary_matches": summary_matches,
            }

        elif summary_matches:
            # Summary mentions are secondary evidence.
            secondary_categories.append(category)
            evidence[category] = {
                "matched_in": "summary_only",
                "title_matches": [],
                "summary_matches": summary_matches,
            }

    if not categories:
        categories = ["Platform & Developer Tools"]
        evidence["Platform & Developer Tools"] = {
            "matched_in": "fallback",
            "title_matches": [],
            "summary_matches": [],
        }

    return categories, secondary_categories, evidence


# --------------------------------------------------
# 4. RELEASE MATURITY
# --------------------------------------------------

def score_release_maturity(title):
    """
    Check release maturity using the title only.
    A mention in the summary cannot earn this bonus.
    """
    title_text = clean_html(title).casefold()

    if contains_keyword(title_text, "generally available"):
        return 2, "Generally available release stated in title"

    if (
        contains_keyword(title_text, "preview")
        or contains_keyword(title_text, "beta")
    ):
        return 0, "Preview or beta release stated in title"

    return 0, "No explicit GA release signal in title"


# --------------------------------------------------
# 5. ACTION AND MIGRATION IMPACT
# --------------------------------------------------

def score_action_impact(title, summary):
    """
    Prioritize meaningful changes that may require user action.
    Ignore generic wording such as 'no longer need an admin'
    and incidental mentions of rate limits.
    """
    title_text = clean_html(title).casefold()
    summary_text = clean_html(summary).casefold()

    reasons = []
    action_score = 0

    # Strong signals in the title.
    replacement_signals = [
        "replaces",
        "deprecated",
        "deprecation",
        "migration",
        "migrate",
        "end of support",
        "support ends",
        "no longer supported",
        "removed",
        "breaking change",
    ]

    title_actions = find_matches(
        title_text, replacement_signals
    )

    if title_actions:
        action_score += 2
        reasons.append(
            "Actionable title signal: "
            + ", ".join(title_actions)
        )

    # Specific lifecycle signals in the summary.
    # These phrases are more meaningful than generic mentions
    # of 'no longer', 'required', or 'rate limits'.
    lifecycle_phrases = [
        "support will end",
        "support ends in",
        "support ends on",
        "last version that includes",
        "will no longer be supported",
        "will be removed in",
        "must migrate",
        "migration is required",
        "breaking change",
    ]

    lifecycle_matches = find_matches(
        summary_text, lifecycle_phrases
    )

    if lifecycle_matches:
        action_score += 1
        reasons.append(
            "Specific lifecycle or migration signal: "
            + ", ".join(lifecycle_matches)
        )

    action_score = min(action_score, 3)

    if not reasons:
        reasons.append("No strong action signal detected")

    return action_score, reasons


# --------------------------------------------------
# 6. SECURITY IMPACT
# --------------------------------------------------

def score_security_impact(title):
    """
    Award security points only when the title itself
    clearly describes a security-focused change.
    """
    title_text = clean_html(title).casefold()

    strong_security_signals = [
        "security vulnerability",
        "critical vulnerability",
        "security fix",
        "security update",
        "security patch",
        "vulnerability fix",
    ]

    matches = find_matches(
        title_text, strong_security_signals
    )

    if matches:
        return 2, (
            "Security-focused title: " + ", ".join(matches)
        )

    return 0, "No explicit security-impact signal in title"


# --------------------------------------------------
# 7. RANK ONE ARTICLE
# --------------------------------------------------

def rank_article(article):
    """Calculate a transparent first-pass editorial score."""

    title = article.get("title", "")
    summary = clean_html(article.get("summary", ""))

    (
        categories,
        secondary_categories,
        category_evidence,
    ) = classify_article(title, summary)

    # Use the strongest title-based topic match.
    topic_score = max(
        TOPIC_WEIGHTS[category]
        for category in categories
    )

    release_score, release_reason = (
        score_release_maturity(title)
    )

    action_score, action_reasons = score_action_impact(
        title, summary
    )

    security_score, security_reason = (
        score_security_impact(title)
    )

    # Maximum possible score:
    # Topic 3 + Release 2 + Action 3 + Security 2 = 10.
    total_score = min(
        10,
        topic_score
        + release_score
        + action_score
        + security_score,
    )

    if total_score >= 7:
        priority = "High"
    elif total_score >= 4:
        priority = "Medium"
    else:
        priority = "Low"

    reasons = [
        f"Main topic: {', '.join(categories)} "
        f"(+{topic_score})",
        f"Release maturity: {release_reason} "
        f"(+{release_score})",
    ]

    reasons.extend(
        f"{reason} (+{action_score if index == 0 else 0})"
        for index, reason in enumerate(action_reasons)
    )

    reasons.append(
        f"Security impact: {security_reason} "
        f"(+{security_score})"
    )

    ranked_article = article.copy()
    ranked_article["summary_text"] = summary
    ranked_article["categories"] = categories
    ranked_article["secondary_categories"] = (
        secondary_categories
    )
    ranked_article["category_evidence"] = category_evidence
    ranked_article["topic_score"] = topic_score
    ranked_article["release_score"] = release_score
    ranked_article["action_score"] = action_score
    ranked_article["security_score"] = security_score
    ranked_article["priority_score"] = total_score
    ranked_article["priority"] = priority
    ranked_article["ranking_reasons"] = reasons
    ranked_article["needs_human_review"] = True

    return ranked_article


# --------------------------------------------------
# 8. SAVE RANKED ARTICLES
# --------------------------------------------------

def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned data not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    articles = dataset.get("articles", [])

    ranked_articles = [
        rank_article(article)
        for article in articles
    ]

    # Highest score first, newest publication date breaks ties.
    ranked_articles.sort(
        key=lambda article: (
            article["priority_score"],
            article.get("published_at_ist", ""),
        ),
        reverse=True,
    )

    output_data = {
        "source": dataset.get("source", "Unknown"),
        "reporting_period": dataset.get(
            "reporting_period", {}
        ),
        "total_articles_ranked": len(ranked_articles),
        "scoring_note": (
            "First-pass heuristic ranking. Topic relevance is "
            "based primarily on title evidence. Release maturity "
            "is checked in the title. Action and security signals "
            "are limited to specific phrases. All articles require "
            "human review before newsletter publication."
        ),
        "scoring_weights": {
            "topic_relevance": 3,
            "release_maturity": 2,
            "action_impact": 3,
            "security_impact": 2,
            "maximum_total": 10,
        },
        "articles": ranked_articles,
    }

    OUTPUT_JSON.parent.mkdir(
        parents=True, exist_ok=True
    )

    with OUTPUT_JSON.open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(
            output_data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    csv_fields = [
        "priority_score",
        "priority",
        "title",
        "published_at_ist",
        "categories",
        "secondary_categories",
        "topic_score",
        "release_score",
        "action_score",
        "security_score",
        "category_evidence",
        "summary_text",
        "link",
        "ranking_reasons",
        "needs_human_review",
    ]

    # Close this CSV in Excel before rerunning if you get
    # a PermissionError.
    with OUTPUT_CSV.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=csv_fields,
            extrasaction="ignore",
        )
        writer.writeheader()

        for article in ranked_articles:
            row = article.copy()

            row["categories"] = ", ".join(
                row["categories"]
            )
            row["secondary_categories"] = ", ".join(
                row["secondary_categories"]
            )
            row["category_evidence"] = json.dumps(
                row["category_evidence"],
                ensure_ascii=False,
            )
            row["ranking_reasons"] = "; ".join(
                row["ranking_reasons"]
            )

            writer.writerow(row)

    # --------------------------------------------------
    # 9. PRINT SUMMARY
    # --------------------------------------------------

    print("ARTICLE RANKING SUMMARY")
    print("-" * 40)
    print("Articles ranked:", len(ranked_articles))

    for priority in ["High", "Medium", "Low"]:
        count = sum(
            article["priority"] == priority
            for article in ranked_articles
        )
        print(f"{priority} priority: {count}")

    print("\nTOP 10 ARTICLES")
    print("-" * 40)

    for number, article in enumerate(
        ranked_articles[:10], start=1
    ):
        print(
            f"{number}. [{article['priority_score']}/10] "
            f"{article.get('title', 'Untitled')}"
        )
        print(
            "   Topics:",
            ", ".join(article["categories"]),
        )
        print("   Priority:", article["priority"])
        print(
            "   Reason:",
            "; ".join(article["ranking_reasons"]),
        )

    print("\nSaved ranked JSON:", OUTPUT_JSON)
    print("Saved review CSV:", OUTPUT_CSV)


if __name__ == "__main__":
    main()
