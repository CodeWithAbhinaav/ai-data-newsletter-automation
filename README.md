\# AI \& Data Technology Newsletter Automation



\## Project Overview

This project automates the creation of a weekly technology newsletter using the Databricks Release Notes RSS feed.



\## Objectives

\- Collect technology updates from an RSS feed.

\- Filter articles by publication date.

\- Remove approved duplicates.

\- Rank articles using predefined rules.

\- Select a balanced newsletter shortlist.

\- Generate a Markdown draft and PDF newsletter.



\## Technology Used

\- Python

\- feedparser

\- JSON and CSV

\- Markdown

\- ReportLab

\- Windows Command Prompt



\## Workflow

1\. Collect RSS articles.

2\. Filter articles for the reporting period.

3\. Clean duplicate records using configured decisions.

4\. Rank articles using a rule-based scoring system.

5\. Select up to 10 articles, with category limits.

6\. Generate a Markdown newsletter draft.

7\. Export the newsletter to PDF.



The `src/run\_pipeline.py` script runs the seven stages in sequence.



\## Latest Recorded Results

\- 36 articles in the weekly filtering result.

\- 4 approved duplicate records removed.

\- 32 articles retained after cleaning.

\- 32 articles ranked.

\- 10 articles selected for the newsletter.

\- 10 article headings detected by the PDF generator.



Verify these results against the final pipeline run before submission.



\## Main Output Files

\- `data/processed/databricks\_newsletter.pdf`

\- `data/processed/databricks\_newsletter\_draft.md`

\- `data/processed/databricks\_newsletter\_shortlist.csv`

\- `data/processed/databricks\_articles\_ranked.csv`



\## Limitations

The ranking system uses predefined rules rather than a trained machine-learning model. Article summaries come from the feed, and human review is required before publication. The pipeline currently runs manually.



\## How to Run

From the project root, execute:



```cmd

.venv\\Scripts\\python.exe src\\run\_pipeline.py

```



