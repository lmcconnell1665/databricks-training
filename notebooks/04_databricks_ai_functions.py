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
