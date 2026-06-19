# Databricks notebook source
# MAGIC %md
# MAGIC # 05 · Unity Catalog Governance Model
# MAGIC
# MAGIC **Databricks Training — Engineering Best Practices**
# MAGIC
# MAGIC Unity Catalog is the governance layer for the lakehouse. Everything is addressed
# MAGIC through a **three-level namespace** and secured with `GRANT` statements.
# MAGIC
# MAGIC ```
# MAGIC   Catalog        >        Schema        >       Table / View
# MAGIC (production,            (sales,                (customers,
# MAGIC  staging)               marketing)              orders)
# MAGIC ```
# MAGIC
# MAGIC ```sql
# MAGIC SELECT * FROM production.sales.customers WHERE region = 'Nashville';
# MAGIC ```
# MAGIC
# MAGIC **Governance best practices:** least-privilege `GRANT`s · managed tables · document
# MAGIC everything with `COMMENT`.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup
# MAGIC Point the widgets at a catalog/schema you can create objects in.

# COMMAND ----------

dbutils.widgets.text("target_catalog", "main", "Target catalog")
dbutils.widgets.text("target_schema", "sales", "Target schema")

catalog = dbutils.widgets.get("target_catalog")
schema = dbutils.widgets.get("target_schema")
print(f"Three-level namespace target: {catalog}.{schema}.customers")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Explore the three-level namespace
# MAGIC The `SHOW` commands and `system.information_schema` let you browse the hierarchy.

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW CATALOGS;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Schemas inside the chosen catalog
# MAGIC SHOW SCHEMAS IN ${target_catalog};

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create governed objects (managed tables)
# MAGIC **Managed tables** keep Unity Catalog in charge of both metadata *and* the underlying
# MAGIC storage — the simplest thing to govern. We seed from the built-in NYC taxi sample.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE CATALOG IF NOT EXISTS ${target_catalog};
# MAGIC CREATE SCHEMA  IF NOT EXISTS ${target_catalog}.${target_schema};
# MAGIC
# MAGIC -- Managed Delta table (no LOCATION clause = managed)
# MAGIC CREATE OR REPLACE TABLE ${target_catalog}.${target_schema}.customers AS
# MAGIC SELECT
# MAGIC   pickup_zip AS zip,
# MAGIC   COUNT(*)   AS trip_count,
# MAGIC   ROUND(AVG(fare_amount), 2) AS avg_fare
# MAGIC FROM samples.nyctaxi.trips
# MAGIC GROUP BY pickup_zip;
# MAGIC
# MAGIC SELECT * FROM ${target_catalog}.${target_schema}.customers LIMIT 10;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Document everything with COMMENT
# MAGIC Comments power discovery, the Catalog Explorer UI, and AI tools like Genie. Document
# MAGIC the table and its columns.

# COMMAND ----------

# MAGIC %sql
# MAGIC COMMENT ON TABLE ${target_catalog}.${target_schema}.customers IS
# MAGIC   'Demo: per-ZIP trip counts and average fares, derived from samples.nyctaxi.trips.';
# MAGIC
# MAGIC ALTER TABLE ${target_catalog}.${target_schema}.customers
# MAGIC   ALTER COLUMN zip        COMMENT 'Pickup ZIP code (business key)';
# MAGIC ALTER TABLE ${target_catalog}.${target_schema}.customers
# MAGIC   ALTER COLUMN trip_count COMMENT 'Number of trips originating in this ZIP';
# MAGIC ALTER TABLE ${target_catalog}.${target_schema}.customers
# MAGIC   ALTER COLUMN avg_fare   COMMENT 'Average fare amount (USD) for trips from this ZIP';
# MAGIC
# MAGIC DESCRIBE TABLE EXTENDED ${target_catalog}.${target_schema}.customers;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Least-privilege access with GRANT
# MAGIC Grant the *minimum* needed. Privileges cascade with the namespace: a principal needs
# MAGIC `USE CATALOG` + `USE SCHEMA` to reach a table, then `SELECT` on the table itself.
# MAGIC
# MAGIC > Replace `` `data_analysts` `` with a real group. These run only if the group exists and
# MAGIC > you have grant authority — otherwise treat them as the reference pattern.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Traversal privileges
# MAGIC GRANT USE CATALOG ON CATALOG ${target_catalog}            TO `data_analysts`;
# MAGIC GRANT USE SCHEMA  ON SCHEMA  ${target_catalog}.${target_schema} TO `data_analysts`;
# MAGIC
# MAGIC -- Read-only access to just this table (least privilege)
# MAGIC GRANT SELECT ON TABLE ${target_catalog}.${target_schema}.customers TO `data_analysts`;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Audit who has access
# MAGIC `SHOW GRANTS` and `information_schema` make permissions reviewable.

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW GRANTS ON TABLE ${target_catalog}.${target_schema}.customers;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Views for finer-grained sharing
# MAGIC Expose a curated subset via a view and grant on the view instead of the base table —
# MAGIC a common least-privilege pattern.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW ${target_catalog}.${target_schema}.high_traffic_zips AS
# MAGIC SELECT zip, trip_count, avg_fare
# MAGIC FROM ${target_catalog}.${target_schema}.customers
# MAGIC WHERE trip_count > 100;
# MAGIC
# MAGIC COMMENT ON VIEW ${target_catalog}.${target_schema}.high_traffic_zips IS
# MAGIC   'ZIPs with more than 100 pickups — safe subset for broad sharing.';
# MAGIC
# MAGIC SELECT * FROM ${target_catalog}.${target_schema}.high_traffic_zips ORDER BY trip_count DESC LIMIT 10;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Recap
# MAGIC - **Three-level namespace:** `catalog.schema.object` for every query.
# MAGIC - **Managed tables** for the simplest governance.
# MAGIC - **`COMMENT`** on tables, columns, and views for discovery & Genie.
# MAGIC - **Least-privilege `GRANT`s**, reviewed with `SHOW GRANTS`.
# MAGIC - **Views** to share curated subsets without exposing base tables.
