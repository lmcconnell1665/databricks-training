# Databricks notebook source
# MAGIC %md
# MAGIC # 03 · Lakehouse Federation
# MAGIC
# MAGIC **Databricks Training — Redshift Federation & Unity Catalog**
# MAGIC
# MAGIC Lakehouse Federation lets you **query external databases directly from Databricks —
# MAGIC without moving or copying data**. The external source is exposed as a *foreign catalog*
# MAGIC in Unity Catalog and governed with the same access controls as native tables.

# COMMAND ----------

# MAGIC %md
# MAGIC ## How it works
# MAGIC
# MAGIC ```
# MAGIC   Redshift            Connection             Foreign Catalog
# MAGIC   (source)    →    (stored credentials)  →  (in Unity Catalog)   →   SELECT like a native table
# MAGIC ```
# MAGIC
# MAGIC **Pushed down to Redshift:** filters, joins, aggregates, projections, sorting, string functions.
# MAGIC **Not pushed down:** window functions, queries on Redshift *external* data.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Type mappings (Redshift → Spark)
# MAGIC
# MAGIC | Redshift Type | Spark Type | Notes |
# MAGIC |---|---|---|
# MAGIC | `varchar`, `text`, `char` | `StringType` | All text types map to String |
# MAGIC | `int2`, `int4` | `IntegerType` | Standard integers |
# MAGIC | `int8` | `LongType` | Large integers |
# MAGIC | `float4` | `FloatType` | Single precision |
# MAGIC | `float8`, `double precision` | `DoubleType` | Double precision |
# MAGIC | `numeric` | `DecimalType` | Exact decimal values |
# MAGIC | `bool` | `BooleanType` | True/false |
# MAGIC | `date` | `DateType` | Date values |
# MAGIC | `timestamp`, `timestamptz` | `TimestampType` | Date + time values |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Discovery: inspect existing connections & foreign catalogs (these run)
# MAGIC Use these to confirm what federation objects already exist in your workspace.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- All connections defined in the metastore (federation + others)
# MAGIC SHOW CONNECTIONS;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Governance reminder
# MAGIC Once the foreign catalog exists, grant access with the same Unity Catalog model used
# MAGIC for native tables (covered in notebook **05 · Unity Catalog Governance Model**):
# MAGIC
# MAGIC ```sql
# MAGIC GRANT USE CATALOG ON CATALOG redshift_catalog TO `analysts`;
# MAGIC GRANT SELECT ON redshift_catalog.public.customers TO `analysts`;
# MAGIC ```

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM cma_redshift_catalog.sage_intacct.ap_bill
# MAGIC LIMIT 100
