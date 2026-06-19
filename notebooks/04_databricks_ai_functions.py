# Databricks notebook source
# MAGIC %md
# MAGIC # 04 · Databricks AI Functions
# MAGIC
# MAGIC **Databricks Training — AI Functions**
# MAGIC
# MAGIC Apply AI directly to your data with **plain SQL — no ML infrastructure required**.
# MAGIC These functions are available in SQL, notebooks, Declarative Pipelines, and Workflows
# MAGIC (Public Preview, Runtime **15.4 LTS+**, on a Serverless or Pro SQL Warehouse).
# MAGIC
# MAGIC | Function | Purpose |
# MAGIC |---|---|
# MAGIC | `ai_analyze_sentiment` | Sentiment analysis |
# MAGIC | `ai_classify` | Classify text with custom labels |
# MAGIC | `ai_extract` | Entity extraction |
# MAGIC | `ai_fix_grammar` | Grammar correction |
# MAGIC | `ai_gen` | General text generation |
# MAGIC | `ai_mask` | PII masking |
# MAGIC | `ai_summarize` | Summarization |
# MAGIC | `ai_translate` | Translation |
# MAGIC | `ai_similarity` | Semantic similarity scoring |
# MAGIC | `ai_forecast` | Time-series forecasting |
# MAGIC | `ai_parse_document` | Document parsing (PDF/image → structured) |
# MAGIC | `ai_query` | Apply *any* model (foundation / custom / external) |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Built-in task functions
# MAGIC Each cell is a tiny, self-contained example using string literals so it runs immediately.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Sentiment: score customer feedback (returns 'positive' / 'negative' / 'neutral' / 'mixed')
# MAGIC SELECT
# MAGIC   review,
# MAGIC   ai_analyze_sentiment(review) AS sentiment
# MAGIC FROM VALUES
# MAGIC   ('The product launch event stream was flawless this year, loved it!'),
# MAGIC   ('Tickets were overpriced and the app kept crashing.'),
# MAGIC   ('The show started at 8pm.')
# MAGIC AS feedback(review);

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Classify: bucket support tickets into custom labels
# MAGIC SELECT
# MAGIC   ticket,
# MAGIC   ai_classify(ticket, ARRAY('billing', 'technical', 'membership', 'event')) AS category
# MAGIC FROM VALUES
# MAGIC   ('My credit card was charged twice for my membership renewal.'),
# MAGIC   ('The video player buffers constantly on my smart TV.'),
# MAGIC   ('What time do doors open for the awards show?')
# MAGIC AS tickets(ticket);

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Extract: pull named entities out of free text
# MAGIC SELECT ai_extract(
# MAGIC   'Reba McEntire performed in Nashville on November 20, 2025.',
# MAGIC   ARRAY('artist', 'city', 'date')
# MAGIC ) AS entities;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Fix grammar + mask PII
# MAGIC SELECT
# MAGIC   ai_fix_grammar('he dont has no tickets for the show') AS corrected,
# MAGIC   ai_mask(
# MAGIC     'Contact John Doe at john.doe@example.com or 615-555-0123.',
# MAGIC     ARRAY('email', 'phone', 'person')
# MAGIC   ) AS masked;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Generate + summarize + translate
# MAGIC SELECT
# MAGIC   ai_gen('Write a one-sentence welcome for new members.') AS generated,
# MAGIC   ai_summarize(
# MAGIC     'Delta Lake is an open-source storage layer that brings ACID transactions to data lakes. '
# MAGIC     || 'It enables reliable reads and writes, time travel, and scalable metadata handling.',
# MAGIC     20  -- target word count
# MAGIC   ) AS summary,
# MAGIC   ai_translate('Welcome to the data platform!', 'es') AS spanish;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Semantic similarity: how related are two phrases? (0 = unrelated, 1 = identical meaning)
# MAGIC SELECT ai_similarity('annual awards ceremony', 'yearly awards show') AS similarity;

# COMMAND ----------

# MAGIC %md
# MAGIC ## `ai_forecast` — time-series forecasting
# MAGIC Give it a table of (timestamp, value) and ask for N future periods. Here we build a
# MAGIC tiny daily series inline and forecast the next 7 days.

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH daily_sales AS (
# MAGIC   SELECT explode(sequence(DATE'2025-01-01', DATE'2025-01-21', INTERVAL 1 DAY)) AS ds
# MAGIC ),
# MAGIC series AS (
# MAGIC   SELECT ds, 100 + datediff(ds, DATE'2025-01-01') * 5 AS revenue
# MAGIC   FROM daily_sales
# MAGIC )
# MAGIC SELECT * FROM AI_FORECAST(
# MAGIC   TABLE(series),
# MAGIC   horizon => 7,
# MAGIC   time_col => 'ds',
# MAGIC   value_col => 'revenue'
# MAGIC );

# COMMAND ----------

# MAGIC %md
# MAGIC ## `ai_parse_document` — document intelligence
# MAGIC Extract structured content (text, tables as HTML, figures, bounding boxes) from PDFs/images
# MAGIC stored in a **Unity Catalog volume**. Replace the path with your own volume of documents.
# MAGIC
# MAGIC Returns: `document.pages`, `document.elements`, `metadata`, `error_status`.
# MAGIC
# MAGIC ```sql
# MAGIC SELECT
# MAGIC   path,
# MAGIC   ai_parse_document(content) AS parsed
# MAGIC FROM read_files(
# MAGIC   '/Volumes/<catalog>/<schema>/<volume>/docs/',
# MAGIC   format => 'binaryFile'
# MAGIC );
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## `ai_query` — apply any model
# MAGIC Use a pre-deployed foundation model (no endpoint setup) for arbitrary prompts.
# MAGIC
# MAGIC **Example 1 — summarize with a foundation model** (runs against literals here):

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT ai_query(
# MAGIC   'databricks-meta-llama-3-3-70b-instruct',
# MAGIC   'Summarize in one sentence: ' ||
# MAGIC   'The annual music festival is a four-day event held every June in Nashville, Tennessee.'
# MAGIC ) AS summary;

# COMMAND ----------

# MAGIC %md
# MAGIC **Example 2 — parse documents, then extract structured fields** (reference pattern; needs a volume of docs):
# MAGIC
# MAGIC ```sql
# MAGIC WITH parsed AS (
# MAGIC   SELECT path, ai_parse_document(content) AS doc
# MAGIC   FROM read_files('/Volumes/.../invoices/', format => 'binaryFile')
# MAGIC )
# MAGIC SELECT
# MAGIC   path,
# MAGIC   ai_query(
# MAGIC     'databricks-claude-sonnet-4',
# MAGIC     'Extract vendor, date, and total from: ' || to_json(doc)
# MAGIC   ) AS info
# MAGIC FROM parsed;
# MAGIC ```
# MAGIC
# MAGIC **Pre-deployed models (no endpoint setup):** Meta Llama 3.3 70B · Claude Sonnet · GPT variants ·
# MAGIC Gemini · plus custom fine-tuned models via serving endpoints.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Putting it together on real data
# MAGIC Build a small reviews table, then run sentiment + classification over it — exactly how
# MAGIC you'd enrich a production feedback table.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMP VIEW member_reviews AS
# MAGIC SELECT * FROM VALUES
# MAGIC   (1, 'Best festival ever, the lineup was incredible!'),
# MAGIC   (2, 'Renewal page threw an error three times before it worked.'),
# MAGIC   (3, 'Could you add more parking near the venue?')
# MAGIC AS r(review_id, review_text);
# MAGIC
# MAGIC SELECT
# MAGIC   review_id,
# MAGIC   review_text,
# MAGIC   ai_analyze_sentiment(review_text) AS sentiment,
# MAGIC   ai_classify(review_text, ARRAY('praise', 'bug', 'feature_request')) AS category
# MAGIC FROM member_reviews;
