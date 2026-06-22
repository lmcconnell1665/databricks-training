# Databricks notebook source
# MAGIC %md
# MAGIC # 02 · Delta Lake & Compute Best Practices
# MAGIC
# MAGIC **Databricks Training — Engineering Best Practices**
# MAGIC
# MAGIC Delta Lake gives you ACID transactions, time travel, and fast queries on the lakehouse.
# MAGIC This notebook walks through the practices from the deck on a small sample table:
# MAGIC
# MAGIC - All tables use **Delta** format by default
# MAGIC - **ACID** transactions for reliable writes
# MAGIC - **Time travel** for auditing & recovery
# MAGIC - **OPTIMIZE** + **ZORDER** for query speed
# MAGIC - **Liquid clustering** for automatic layout optimization
# MAGIC - Compute management notes (serverless, auto-termination, policies, pools)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup
# MAGIC Edit the widgets to point at a catalog/schema you can write to. Defaults assume a
# MAGIC `main.training` schema — change `target_catalog` if your workspace differs.

# COMMAND ----------

dbutils.widgets.text("target_catalog", "cma_training", "Target catalog")
dbutils.widgets.text("target_schema", "luke_training", "Target schema")

catalog = dbutils.widgets.get("target_catalog")
schema = dbutils.widgets.get("target_schema")
table = f"{catalog}.{schema}.taxi_trips_demo"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
print("Working table:", table)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Create a Delta table (the default format)
# MAGIC We seed a small table from the built-in `samples.nyctaxi.trips` dataset.
# MAGIC No `USING DELTA` needed — Delta is the default on Databricks.

# COMMAND ----------

(
    spark.read.table("samples.nyctaxi.trips")
    .limit(5000)
    .write.mode("overwrite")
    .saveAsTable(table)
)

spark.sql(f"DESCRIBE DETAIL {table}").select("format", "numFiles", "sizeInBytes").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. ACID transactions
# MAGIC Concurrent-safe `MERGE` / `UPDATE` / `DELETE` are built in. Here we run an `UPDATE`
# MAGIC and a `DELETE` — each is an atomic, all-or-nothing transaction.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Atomic update: flag suspicious zero-distance trips
# MAGIC UPDATE ${target_catalog}.${target_schema}.taxi_trips_demo
# MAGIC SET fare_amount = 0
# MAGIC WHERE trip_distance <= 0;
# MAGIC
# MAGIC -- Atomic delete: drop clearly invalid rows
# MAGIC DELETE FROM ${target_catalog}.${target_schema}.taxi_trips_demo
# MAGIC WHERE fare_amount < 0;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Time travel — auditing & recovery
# MAGIC Every write creates a new version. Inspect history, then query an older snapshot.

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE HISTORY ${target_catalog}.${target_schema}.taxi_trips_demo;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Read the table AS OF its very first version (before the UPDATE/DELETE above).
# MAGIC SELECT COUNT(*) AS rows_at_version_0
# MAGIC FROM ${target_catalog}.${target_schema}.taxi_trips_demo VERSION AS OF 0;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. OPTIMIZE + ZORDER — faster queries
# MAGIC `OPTIMIZE` compacts many small files into fewer large ones. `ZORDER BY` co-locates
# MAGIC related data so queries that filter on those columns scan less.

# COMMAND ----------

# MAGIC %sql
# MAGIC OPTIMIZE ${target_catalog}.${target_schema}.taxi_trips_demo
# MAGIC ZORDER BY (pickup_zip);

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Liquid clustering — automatic layout (modern alternative to ZORDER)
# MAGIC Liquid clustering lets Delta maintain data layout automatically as data evolves —
# MAGIC no manual partition choices, and clustering keys can change over time.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Create a clustered table; Delta manages the physical layout for you.
# MAGIC CREATE OR REPLACE TABLE ${target_catalog}.${target_schema}.taxi_trips_clustered
# MAGIC CLUSTER BY (pickup_zip)
# MAGIC AS SELECT * FROM ${target_catalog}.${target_schema}.taxi_trips_demo;
# MAGIC
# MAGIC -- Trigger clustering/compaction (incremental — only touches new data).
# MAGIC OPTIMIZE ${target_catalog}.${target_schema}.taxi_trips_clustered;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Compute Management Best Practices
# MAGIC
# MAGIC These are configured at the **cluster / warehouse** level, not in code, but they matter for cost & performance:
# MAGIC
# MAGIC - **Start small, scale to the workload** — don't over-provision.
# MAGIC - **Prefer serverless** compute where available (fast start, auto-scaling, less to manage).
# MAGIC - **Set auto-termination** so idle clusters stop and you avoid idle DBU charges.
# MAGIC - **Use instance pools** for faster cluster startup on repeated jobs.
# MAGIC - **Use cluster policies** to enforce standards (max nodes, allowed instance types, auto-termination).
# MAGIC
# MAGIC The cell below shows a couple of cluster settings on the current compute (where available).

# COMMAND ----------

# MAGIC %md
# MAGIC ### Cleanup (optional)
# MAGIC Uncomment to drop the demo tables when you're done.

# COMMAND ----------

spark.sql(f"DROP TABLE IF EXISTS {catalog}.{schema}.taxi_trips_demo")
spark.sql(f"DROP TABLE IF EXISTS {catalog}.{schema}.taxi_trips_clustered")
print("Done.")
