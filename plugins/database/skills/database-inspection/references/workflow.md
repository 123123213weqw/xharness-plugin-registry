# Database inspection, plans and migrations

## SQLite helper

Python 3.11+ with its sqlite3 module is required. The helper opens only an existing database using a quoted file URI and mode=ro, sets query_only, and installs an engine authorizer. It rejects DDL, data writes, ATTACH/DETACH, transactions, PRAGMA changes, extensions and multiple statements. Read-only is enforced by the engine rather than a brittle SELECT-prefix check; valid read-only WITH queries are allowed.

- `python scripts/sqlite_read.py project.sqlite inspect`
- `python scripts/sqlite_read.py project.sqlite query --sql 'SELECT id,name FROM items WHERE id = ?' --params-json '[1]' --max-rows 100`
- `python scripts/sqlite_read.py project.sqlite explain --sql 'SELECT id FROM items WHERE id = ?' --params-json '[1]'`

The script does not dump whole databases. Rows, per-value excerpts, total result bytes, SQLite value/SQL length and execution time are bounded. BLOB values have explicit base64, byte count and truncation markers. Duplicate SQL column labels are preserved in a separate columns array, not overwritten as dictionary keys. Progress-handler timeouts cannot replace the enclosing Host process deadline. Query errors stay failed, never an empty successful result. Do not put secret literals into --sql or --params-json; use an existing private query file/native client for sensitive tasks.

## PostgreSQL / MySQL

These require the user's actual installed client, authorized endpoint and account. They are not implemented by the SQLite script. Inspect engine/version and transaction behavior; use read-only roles and transactions where supported. Never print connection passwords or full DSNs. Plain EXPLAIN is a plan observation; EXPLAIN ANALYZE runs the statement and may perform writes. Missing credentials, unsupported dialects and permission failures must be reported, not reinterpreted as an empty schema.

## Changes

A migration is a separate scoped operation. Use the project's actual migration tool and a disposable seeded database. Check before/after records, constraints, locking and rollback behavior. No production mutation, volume copy or recovery action follows merely from an inspection request. Preserve existing user work. Report measured behavior separately from proposed indexes, lock risks and rollback plans.

References: [Python sqlite3](https://docs.python.org/3/library/sqlite3.html), [PostgreSQL transaction modes](https://www.postgresql.org/docs/current/sql-set-transaction.html).
