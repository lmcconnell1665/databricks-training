# Databricks notebook source
# MAGIC %md
# MAGIC # 03 · Setting Up Lakehouse Federation
# MAGIC
# MAGIC **CMA Databricks Training — Redshift Federation & Unity Catalog**
# MAGIC
# MAGIC Lakehouse Federation lets you **query external databases directly from Databricks —
# MAGIC without moving or copying data**. The external source is exposed as a *foreign catalog*
# MAGIC in Unity Catalog and governed with the same access controls as native tables.
# MAGIC
# MAGIC > ⚠️ **Note:** the `CREATE CONNECTION` / `CREATE FOREIGN CATALOG` cells require a real
# MAGIC > Redshift endpoint and `CREATE CONNECTION` privilege on the metastore, so they are written
# MAGIC > as **`%md` reference SQL** (won't auto-run). The discovery cells at the bottom *do* run
# MAGIC > and show how to inspect connections/catalogs once they exist.

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
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - Unity Catalog–enabled workspace
# MAGIC - Runtime **13.3 LTS+** (Standard/Dedicated access mode), or SQL Warehouse Pro/Serverless **v2023.40+**
# MAGIC - Network connectivity from compute to Redshift
# MAGIC - `CREATE CONNECTION` privilege on the metastore

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 0 (Best Practice): Store credentials as Databricks secrets
# MAGIC **Never** put plaintext passwords in SQL. Create a secret scope and store the Redshift
# MAGIC user/password, then reference them with the `secret()` function.
# MAGIC
# MAGIC ```bash
# MAGIC # Databricks CLI (run from your laptop, not the notebook)
# MAGIC databricks secrets create-scope cma-secrets
# MAGIC databricks secrets put-secret cma-secrets redshift-user
# MAGIC databricks secrets put-secret cma-secrets redshift-pw
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Create the connection
# MAGIC A connection stores the host + credentials once and can back many foreign catalogs.
# MAGIC
# MAGIC ```sql
# MAGIC CREATE CONNECTION redshift_cma TYPE redshift
# MAGIC OPTIONS (
# MAGIC   host '<hostname>',
# MAGIC   port '5439',
# MAGIC   user secret('cma-secrets', 'redshift-user'),
# MAGIC   password secret('cma-secrets', 'redshift-pw')
# MAGIC );
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Create the foreign catalog
# MAGIC This mirrors a Redshift database into Unity Catalog. Its schemas/tables then appear
# MAGIC under the three-level namespace just like native data.
# MAGIC
# MAGIC ```sql
# MAGIC CREATE FOREIGN CATALOG redshift_catalog
# MAGIC USING CONNECTION redshift_cma
# MAGIC OPTIONS (database 'mydb');
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Query federated data like a native table
# MAGIC Filters such as `state = 'TN'` are **pushed down** to Redshift, so only matching rows come back.
# MAGIC
# MAGIC ```sql
# MAGIC SELECT *
# MAGIC FROM redshift_catalog.public.customers
# MAGIC WHERE state = 'TN'
# MAGIC LIMIT 100;
# MAGIC ```

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

# MAGIC %sql
# MAGIC -- Foreign catalogs surface here with connection metadata
# MAGIC SELECT catalog_name, connection_name, catalog_owner, comment
# MAGIC FROM system.information_schema.catalogs
# MAGIC WHERE connection_name IS NOT NULL;

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
