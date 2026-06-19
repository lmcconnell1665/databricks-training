# CMA Databricks Training — Demo Notebooks

Hands-on demo notebooks for the LBMC Databricks Training & Enablement deck. Each notebook
is small and self-contained, and uses **Databricks sample data** (`samples.nyctaxi.trips`,
inline `VALUES`, and the built-in foundation models) so it runs with minimal setup.

## Notebooks

| # | Notebook | Covers | Runs as-is? |
|---|----------|--------|-------------|
| 01 | `01_notebook_development_standards.py` | Version control, modular code, pytest testing, widgets & Lakeflow Jobs | ✅ |
| 02 | `02_delta_lake_and_compute.py` | Delta format, ACID, time travel, OPTIMIZE/ZORDER, liquid clustering, compute tips | ✅ (needs write access to a catalog/schema) |
| 03 | `03_lakehouse_federation.py` | Redshift federation: connection, foreign catalog, type mappings, secrets | 🔶 SQL examples are reference (need a real Redshift); discovery cells run |
| 04 | `04_databricks_ai_functions.py` | `ai_*` functions + `ai_query` / `ai_parse_document` | ✅ (needs Serverless/Pro SQL warehouse, Runtime 15.4 LTS+) |
| 05 | `05_unity_catalog_governance.py` | Three-level namespace, managed tables, COMMENT, least-privilege GRANT, views | ✅ (GRANT cells need a real group) |

## Supporting files (used by notebook 01)

- `lib/transformations.py` — reusable business logic (the "modular code" standard).
- `tests/test_transformations.py` — `pytest` unit tests for that module.

Run the tests locally or in a notebook/Job step:

```bash
cd notebooks
python -m pytest tests -q
```

## How to use these in Databricks

1. Clone this repo into **Workspace → Repos** (Git integration).
2. Open a notebook — the `.py` files import as Databricks notebooks (cells split on
   `# COMMAND ----------`, with `# MAGIC %md` / `%sql` rendering as markdown / SQL).
3. Attach to **Serverless** or a Unity Catalog–enabled cluster (Runtime **15.4 LTS+** for the
   AI Functions notebook).
4. Set the widget values at the top of notebooks 02 and 05 to a catalog/schema you can write to.

## Format note

Notebooks are stored in **Databricks source (`.py`) format** rather than `.ipynb` so they are
clean to diff and review in Git — directly demonstrating the version-control standard from the deck.
