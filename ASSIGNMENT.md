# Technical Assignment

Implement a production-minded pipeline that:
- Ingests multi-format data (JSON, CSV, XML, API, dynamic web)
- Normalizes to a canonical model
- Deduplicates (keep latest by `last_updated`)
- Validates quality rules
- Loads Silver & Gold tables to a DB
- Uses Medallion layers (Bronze → Silver → Gold)
- orchestrated via Prefect
- Uses PySpark for heavy transforms

> All code stubs are provided under `pipeline/` and `orchestration/`. Replace `pass` / `NotImplementedError` with working implementations.
