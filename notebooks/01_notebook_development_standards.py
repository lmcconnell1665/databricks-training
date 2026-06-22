# Databricks notebook source
# MAGIC %md
# MAGIC # 01 · Notebook Development Standards
# MAGIC
# MAGIC **Databricks Training — Engineering Best Practices**
# MAGIC
# MAGIC | Standard | Idea |
# MAGIC |---|---|
# MAGIC | **Version Control** | Use Databricks Repos + Git. Branch for isolated work. Never commit to `main` directly. |
# MAGIC | **Modular Code** | Refactor prototypes into reusable `.py` modules; import them into notebooks. |
# MAGIC | **Testing** | Write `pytest` unit tests in `.py` files; run them before production. |
# MAGIC | **Production Jobs** | Schedule with Lakeflow Jobs against a committed repo version — not the notebook **Schedule** button. |

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Version Control
# MAGIC
# MAGIC Luke was here.
# MAGIC
# MAGIC This notebook lives in a **Databricks Repo** backed by Git. Day-to-day flow:
# MAGIC
# MAGIC 1. Clone the repo into **Workspace → Repos**.
# MAGIC 2. Create a feature branch (e.g. `feature/taxi-metrics`) — never edit `main` directly.
# MAGIC 3. Commit + push from the Repos UI, open a Pull Request, merge after review.
# MAGIC
# MAGIC The cell below prints the runtime / repo context so you can confirm where you are running.

# COMMAND ----------

#jr test
#add two lines

print("Current user       :", spark.sql("SELECT current_user()").first()[0])
print("Notebook path      :",
      dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Modular Code
# MAGIC
# MAGIC Business logic lives in `notebooks/lib/transformations.py`, **not** in notebook cells.
# MAGIC We add the repo root to `sys.path` and import it. In a Databricks Repo the repo
# MAGIC root is already importable, so this step is mostly for clarity / local runs.

# COMMAND ----------

import os
import sys

# Make the repo root importable so `from lib... import ...` works.
repo_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from lib.transformations import classify_trip, fare_per_mile  # noqa: E402

print("fare_per_mile(20.0, 5.0) =", fare_per_mile(20.0, 5.0))
print("classify_trip(25.0)      =", classify_trip(25.0))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Apply the reusable logic to sample data
# MAGIC We register the functions as Spark UDFs and run them over the built-in
# MAGIC `samples.nyctaxi.trips` dataset — orchestration here, business logic in the module.

# COMMAND ----------

from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, DoubleType

fare_per_mile_udf = udf(fare_per_mile, DoubleType())
classify_trip_udf = udf(classify_trip, StringType())

trips = spark.read.table("samples.nyctaxi.trips").limit(1000)
enriched = (
    trips
    .withColumn("fare_per_mile", fare_per_mile_udf("fare_amount", "trip_distance"))
    .withColumn("trip_class", classify_trip_udf("trip_distance"))
    .select("tpep_pickup_datetime", "trip_distance", "fare_amount", "fare_per_mile", "trip_class")
)
display(enriched)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Parameterization & Production Jobs
# MAGIC
# MAGIC Notebooks accept parameters via **widgets**, so the same notebook can be reused with
# MAGIC different inputs from a Lakeflow Job — no editing required.

# COMMAND ----------

dbutils.widgets.text("row_limit", "1000", "Rows to process")
row_limit = int(dbutils.widgets.get("row_limit"))
print(f"Processing {row_limit} rows (override this from the Job's task parameters).")

display(spark.read.table("samples.nyctaxi.trips").limit(row_limit))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Production scheduling — the right way
# MAGIC
# MAGIC ❌ **Do not** use the notebook **Schedule** button for production.
# MAGIC
# MAGIC ✅ **Do** create a **Lakeflow Job** (sidebar → *Jobs & Pipelines → Create → Job*):
# MAGIC
# MAGIC - Point the task at this notebook **at a committed Git ref** (tag or branch), not the live workspace copy.
# MAGIC - Pass `row_limit` (and other params) through the task configuration.
# MAGIC - Add the `pytest` step as an upstream task so a failing test blocks the run.
# MAGIC - Configure serverless / job compute, retries, timeouts, and email/webhook alerts.
# MAGIC
# MAGIC This keeps production runs reproducible and tied to reviewed, version-controlled code.
