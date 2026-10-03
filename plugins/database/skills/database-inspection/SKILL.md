---
name: database-inspection
description: "Inspect SQLite schemas and bounded read-only query results; use installed native clients for other engines."
---

# Database Inspection

Determine the database engine and explicit target before using SQL. For local SQLite, use [the read-only helper](scripts/sqlite_read.py): `python sqlite_read.py DATABASE inspect` or `python sqlite_read.py DATABASE query --sql "SELECT ..."`. It opens an existing file in mode=ro, enables query_only and authorizer enforcement, limits row/value/output size and query time. It does not create a database, enable extensions, or execute multiple statements. SQL errors, timeout and truncation are explicit. Read [the engine guide](references/workflow.md) for PostgreSQL/MySQL; do not treat the SQLite helper as a universal connector.
