# Hybrid Retrieval Edge-Case Knowledge Base: PG

Synthetic operational corpus for retrieval evaluation. Each incident has a stable evidence ID.

## Unique constraint violation

Evidence ID: KB-HYBRID-PG-001

### Incident signature

PostgreSQL returns SQLSTATE `23505` / duplicate key value violates unique constraint.

### Most likely cause

Concurrent or repeated writes attempted to create a value protected by a unique constraint.

### Diagnostic procedure

Inspect the constraint name, conflicting key, transaction path, and whether the operation should be idempotent.

### Resolution

Use the unique constraint as the concurrency boundary and apply `INSERT ... ON CONFLICT` when semantics permit.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-PG-001 is the combination of the incident signature and diagnostic procedure above.

## Serialization failure

Evidence ID: KB-HYBRID-PG-002

### Incident signature

A transaction aborts with SQLSTATE `40001` serialization_failure.

### Most likely cause

Serializable transactions formed a dependency pattern that PostgreSQL cannot safely serialize.

### Diagnostic procedure

Capture the failing transaction, isolation level, contention pattern, and retry frequency.

### Resolution

Retry the complete transaction with bounded backoff and keep transactions short.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-PG-002 is the combination of the incident signature and diagnostic procedure above.

## Lock not available

Evidence ID: KB-HYBRID-PG-003

### Incident signature

A statement returns SQLSTATE `55P03` lock_not_available.

### Most likely cause

The statement requested a lock that conflicts with an existing holder and was configured not to wait or timed out.

### Diagnostic procedure

Inspect `pg_locks`, `pg_stat_activity`, blocker PID, lock mode, and transaction age.

### Resolution

Resolve the blocker safely and reduce lock duration; schedule lock-heavy operations deliberately.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-PG-003 is the combination of the incident signature and diagnostic procedure above.

## Statement timeout

Evidence ID: KB-HYBRID-PG-004

### Incident signature

A query is canceled with `canceling statement due to statement timeout`.

### Most likely cause

Execution exceeded the configured `statement_timeout`.

### Diagnostic procedure

Check `SHOW statement_timeout`, `EXPLAIN (ANALYZE, BUFFERS)` in a safe environment, query shape, and wait events.

### Resolution

Fix the slow query or contention before raising the timeout; use workload-appropriate limits.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-PG-004 is the combination of the incident signature and diagnostic procedure above.

## Too many connections

Evidence ID: KB-HYBRID-PG-005

### Incident signature

Clients receive `remaining connection slots are reserved for non-replication superuser connections`.

### Most likely cause

Application pools or leaked sessions exhausted normal PostgreSQL connection capacity.

### Diagnostic procedure

Inspect `pg_stat_activity`, pool sizes across instances, idle sessions, and checkout duration.

### Resolution

Bound application pools, close sessions reliably, and use a pooler such as PgBouncer when appropriate.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-PG-005 is the combination of the incident signature and diagnostic procedure above.

## Recovery read-only

Evidence ID: KB-HYBRID-PG-006

### Incident signature

Writes fail with `cannot execute ... in a read-only transaction` on a standby.

### Most likely cause

The application connected to a read-only replica or a transaction was explicitly marked read only.

### Diagnostic procedure

Check `SELECT pg_is_in_recovery()`, transaction settings, endpoint routing, and failover state.

### Resolution

Send writes to the writable primary and make role-aware routing resilient to failover.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-PG-006 is the combination of the incident signature and diagnostic procedure above.

## Undefined column after deploy

Evidence ID: KB-HYBRID-PG-007

### Incident signature

A query returns SQLSTATE `42703` undefined_column immediately after deployment.

### Most likely cause

Application code expects a schema change that is absent, incomplete, or deployed in an incompatible order.

### Diagnostic procedure

Compare application version with migration version and inspect the actual table definition.

### Resolution

Use backward-compatible expand/contract migrations and ensure migrations complete before code requires new columns.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-PG-007 is the combination of the incident signature and diagnostic procedure above.

## Deadlock detected

Evidence ID: KB-HYBRID-PG-008

### Incident signature

PostgreSQL reports SQLSTATE `40P01` deadlock detected.

### Most likely cause

Concurrent transactions acquire conflicting resources in inconsistent order.

### Diagnostic procedure

Inspect PostgreSQL deadlock logs, statements, lock order, and transaction duration.

### Resolution

Acquire resources in a consistent order, shorten transactions, and retry the aborted transaction.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-PG-008 is the combination of the incident signature and diagnostic procedure above.

## Disk full during WAL

Evidence ID: KB-HYBRID-PG-009

### Incident signature

PostgreSQL reports `No space left on device` while `pg_wal` grows.

### Most likely cause

WAL cannot be recycled because storage is exhausted, archiving fails, or a replication slot retains old WAL.

### Diagnostic procedure

Inspect filesystem capacity, `pg_replication_slots`, `pg_stat_archiver`, and WAL generation rate.

### Resolution

Restore safe capacity, repair archiving, and remove only confirmed-unused slots.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-PG-009 is the combination of the incident signature and diagnostic procedure above.

## Idle transaction cleanup blocked

Evidence ID: KB-HYBRID-PG-010

### Incident signature

Vacuum cannot reclaim old row versions while a session remains `idle in transaction`.

### Most likely cause

An open transaction retains an old snapshot and prevents cleanup beyond its horizon.

### Diagnostic procedure

Inspect `pg_stat_activity` for old `xact_start`, session owner, and query path.

### Resolution

Fix transaction boundaries and consider `idle_in_transaction_session_timeout` as a guardrail.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-PG-010 is the combination of the incident signature and diagnostic procedure above.
