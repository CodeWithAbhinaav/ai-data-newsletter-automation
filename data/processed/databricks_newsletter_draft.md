# AI & Data Weekly

*A curated update on AI, data engineering, analytics, and data platforms.*

**Reporting period:** From 2026-10-12T00:00:00+05:30
**Source feed:** Databricks Release Notes
**Stories selected:** 10

---

## In This Issue

- **AI & Agents** (3)
- **Data Engineering & SQL** (3)
- **BI & Analytics** (1)
- **ML & Data Science** (1)
- **Security & Governance** (2)

---

## AI & Agents

### 1. [Databricks AI Runtime SDK replaces serverless_gpu](https://docs.databricks.com/aws/en/release-notes/product/2026/october#databricks-ai-runtime-sdk-replaces-serverless_gpu)

**Priority:** Medium (6/10)
**Published:** 2026-10-13T05:30:00+05:30

Starting in GPU environment version 6, the Databricks AI Runtime SDK ( databricks-sdk-air ) replaces the deprecated serverless_gpu package. It provides the @distributed and ray_init APIs and the databricks.air.data utilities under the databricks.air namespace. The gpus and gpu_type arguments are renamed to num_accelerators and accelerator_type . The old names still work in databricks.air but emit a FutureWarning , and support will end in version 7. Serverless GPU environment version 6 includes both packages. Version 6 is the last version that includes serverless_gpu . Versions 5 and below continue to use it. See Migrate from serverless_gpu .

**Original source:** [Read the release note](https://docs.databricks.com/aws/en/release-notes/product/2026/october#databricks-ai-runtime-sdk-replaces-serverless_gpu)

**Editorial status:** Pending human review

---

### 2. [File upload in Genie One and Genie Agents is now generally available](https://docs.databricks.com/aws/en/ai-bi/release-notes/2026#file-upload-in-genie-one-and-genie-agents-is-now-generally-available)

**Priority:** Medium (5/10)
**Published:** 2026-10-16T05:30:00+05:30

File upload in Genie One and Genie Agents is now generally available, so workspace admins no longer need to turn on a preview. Upload files to a conversation and analyze them in natural language alongside your other data. For supported file types and limits, see Upload a file and Upload a file to a Genie Agent . File upload in Genie One isn't supported for users who have only consumer access .

**Original source:** [Read the release note](https://docs.databricks.com/aws/en/ai-bi/release-notes/2026#file-upload-in-genie-one-and-genie-agents-is-now-generally-available)

**Editorial status:** Pending human review

---

### 3. [Consumer access to query Unity Gateway services is generally available](https://docs.databricks.com/aws/en/release-notes/unity-gateway#consumer-access-to-query-unity-gateway-services-is-generally-available)

**Priority:** Medium (5/10)
**Published:** 2026-10-15T05:30:00+05:30

Users with the consumer access entitlement no longer need an account admin to enable the "Consumer access to Unity Gateway" preview to query the model services and model provider services shared with them, or to use Unity Gateway coding agent features. See Consumer access capabilities . This change can increase model traffic from consumer access users, including traffic to external providers. To control this traffic, account admins can set budgets and rate limits, or disable direct model access, for consumer access users. See Manage budgets for Unity Gateway , Apply rate limits to model and MCP services , and Manage entitlements .

**Original source:** [Read the release note](https://docs.databricks.com/aws/en/release-notes/unity-gateway#consumer-access-to-query-unity-gateway-services-is-generally-available)

**Editorial status:** Pending human review

---

## Data Engineering & SQL

### 4. [MySQL integrated CDC pipeline is now generally available](https://docs.databricks.com/aws/en/release-notes/product/2026/october#mysql-integrated-cdc-pipeline-is-now-generally-available)

**Priority:** Medium (5/10)
**Published:** 2026-10-15T05:30:00+05:30

The integrated CDC pipeline for MySQL is now generally available. An integrated CDC pipeline ingests change data from MySQL into Databricks using a single pipeline, combining extraction and application into one pipeline update. Unlike the standard gateway-based architecture, an integrated CDC pipeline requires no separate ingestion gateway. See Create an integrated CDC pipeline for MySQL .

**Original source:** [Read the release note](https://docs.databricks.com/aws/en/release-notes/product/2026/october#mysql-integrated-cdc-pipeline-is-now-generally-available)

**Editorial status:** Pending human review

---

### 5. [Parameters for Lakeflow pipelines are now generally available](https://docs.databricks.com/aws/en/release-notes/product/2026/october#parameters-for-lakeflow-pipelines-are-now-generally-available)

**Priority:** Medium (5/10)
**Published:** 2026-10-12T05:30:00+05:30

Pipeline parameters are now generally available. Parameterize Lakeflow pipeline SQL source code with key-value pairs so a single pipeline can run against different catalogs, schemas, or tables without editing the source. Define parameter defaults in pipeline settings, override them when you start an update, and reference them in SQL with named parameter syntax. See Use parameters with pipelines .

**Original source:** [Read the release note](https://docs.databricks.com/aws/en/release-notes/product/2026/october#parameters-for-lakeflow-pipelines-are-now-generally-available)

**Editorial status:** Pending human review

---

### 6. [Lakebase Search supports Chinese, Japanese, and Korean full-text search](https://docs.databricks.com/aws/en/release-notes/lakebase#lakebase-search-supports-chinese-japanese-and-korean-full-text-search)

**Priority:** Low (3/10)
**Published:** 2026-10-15T05:30:00+05:30

The lakebase_tokenizer extension now supports keyword search over Chinese, Japanese, and Korean (CJK) text. These languages don't separate words with spaces, so native PostgreSQL full-text search can't split them into useful search terms. The new tokenizer_morph template uses morphological analysis with bundled language dictionaries to segment CJK text into words: Built-in configurations : installing the extension creates tokenizer_chinese , tokenizer_japanese , and tokenizer_korean . Use them directly with to_tsvector without creating a dictionary. Compound handling : choose a mode that keeps compound words whole, splits them into finer-grained terms, or emits both, depending on the language. Language-aware filtering : drop Japanese particles and function words, convert Japanese terms to their base form, and filter Korean particles and endings, so matches focus on meaningful terms. Like tokenizer_wholeword , it produces standard tsvector values that work with GIN (generalized inverted index) indexes and the lakebase_text lakebase_bm25 index for BM25 (best match 25) ranking. CJK support ships in lakebase_tokenizer 0.2.0. If you already use the extension, run ALTER EXTENSION lakebase_tokenizer UPDATE . Your existing configurations and indexes don't need to change. See lakebase_tokenizer .

**Original source:** [Read the release note](https://docs.databricks.com/aws/en/release-notes/lakebase#lakebase-search-supports-chinese-japanese-and-korean-full-text-search)

**Editorial status:** Pending human review

---

## BI & Analytics

### 7. [ADBC driver for Power BI is now generally available](https://docs.databricks.com/aws/en/release-notes/product/2026/october#adbc-driver-for-power-bi-is-now-generally-available)

**Priority:** Medium (5/10)
**Published:** 2026-10-15T05:30:00+05:30

The Arrow Database Connectivity (ADBC) driver for the Databricks connector for Power BI is now generally available. ADBC is the default driver for new connections in Power BI Desktop and the Power BI service. See Configure ADBC or ODBC driver for Power BI .

**Original source:** [Read the release note](https://docs.databricks.com/aws/en/release-notes/product/2026/october#adbc-driver-for-power-bi-is-now-generally-available)

**Editorial status:** Pending human review

---

## ML & Data Science

### 8. [Feature Views are now generally available](https://docs.databricks.com/aws/en/release-notes/product/2026/october#feature-views-are-now-generally-available)

**Priority:** Medium (4/10)
**Published:** 2026-10-12T05:30:00+05:30

Feature Views are now generally available for batch, streaming, and request-time data. They will be enabled for compliance security profile workspaces in mid-November 2026. See Feature Views .

**Original source:** [Read the release note](https://docs.databricks.com/aws/en/release-notes/product/2026/october#feature-views-are-now-generally-available)

**Editorial status:** Pending human review

---

## Security & Governance

### 9. [Private connectivity from serverless compute to AWS-managed resources is now generally available](https://docs.databricks.com/aws/en/release-notes/product/2026/october#private-connectivity-from-serverless-compute-to-aws-managed-resources-is-now-generally-available)

**Priority:** Medium (4/10)
**Published:** 2026-10-12T05:30:00+05:30

AWS Private Link from Databricks serverless compute to AWS-managed resources, such as S3 buckets, previously in Public Preview, is now generally available. Your data traffic remains entirely within the AWS network and never traverses the public internet. See Configure private connectivity to AWS-managed resources .

**Original source:** [Read the release note](https://docs.databricks.com/aws/en/release-notes/product/2026/october#private-connectivity-from-serverless-compute-to-aws-managed-resources-is-now-generally-available)

**Editorial status:** Pending human review

---

### 10. [Context-based ingress policies for inbound private connectivity are now generally available](https://docs.databricks.com/aws/en/release-notes/product/2026/october#context-based-ingress-policies-for-inbound-private-connectivity-are-now-generally-available)

**Priority:** Medium (4/10)
**Published:** 2026-10-12T05:30:00+05:30

Context-based ingress policies for inbound Private Link are now generally available. Control which registered VPC endpoints can reach your workspaces, and combine endpoint rules with identity and request type conditions in the same policy. If Context-Based Ingress: Workspace Private Access Policies isn't already enabled for your account, an account admin can enable it from the account console Previews page. See Configure private access policy .

**Original source:** [Read the release note](https://docs.databricks.com/aws/en/release-notes/product/2026/october#context-based-ingress-policies-for-inbound-private-connectivity-are-now-generally-available)

**Editorial status:** Pending human review

---

## Editorial Review Checklist

- [ ] Verify each story against its original source.
- [ ] Confirm publication dates and reporting period.
- [ ] Check that each summary accurately reflects the source.
- [ ] Confirm technical names, release status, and migration details.
- [ ] Remove stories that are repetitive or not useful to readers.
- [ ] Review all priority scores; they are automated estimates.
- [ ] Add an introduction and closing note before publication.

---

*Draft generated automatically. Stories have not been independently fact-checked. Review before distributing.*
