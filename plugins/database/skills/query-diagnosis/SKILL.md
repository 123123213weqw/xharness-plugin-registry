---
name: query-diagnosis
description: "Explain SQL plans and identify measured query bottlenecks without silently executing writes."
---

# Query Diagnosis

Read [the engine guide](../database-inspection/references/workflow.md). Capture engine/version, schema/indexes, representative data scale and the actual plan. SQLite: `sqlite_read.py DATABASE explain --sql "SELECT ..."` uses EXPLAIN QUERY PLAN. For PostgreSQL/MySQL use the installed client and a least-privilege account/transaction. Plain EXPLAIN is the default; EXPLAIN ANALYZE executes the query and is not a harmless text inspection. Propose indexes/rewrites, verify equivalence, and compare measurements only on an authorized fixture or selected environment. Do not claim faster execution from the plan alone.
