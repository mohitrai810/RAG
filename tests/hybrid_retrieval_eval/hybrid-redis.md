# Hybrid Retrieval Edge-Case Knowledge Base: REDIS

Synthetic operational corpus for retrieval evaluation. Each incident has a stable evidence ID.

## Protected mode blocks remote clients

Evidence ID: KB-HYBRID-REDIS-001

### Incident signature

Remote clients receive `DENIED Redis is running in protected mode` while localhost succeeds.

### Most likely cause

protected-mode is enabled and network binding/authentication are not configured for remote access.

### Diagnostic procedure

Inspect `CONFIG GET protected-mode`, `CONFIG GET bind`, `ACL WHOAMI`, and the client source address.

### Resolution

Configure an explicit bind address and authentication. Do not disable protected mode without equivalent access controls.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-REDIS-001 is the combination of the incident signature and diagnostic procedure above.

## CROSSSLOT in Redis Cluster

Evidence ID: KB-HYBRID-REDIS-002

### Incident signature

A multi-key command returns `CROSSSLOT Keys in request don't hash to the same slot`.

### Most likely cause

The keys map to different Redis Cluster hash slots.

### Diagnostic procedure

Run `CLUSTER KEYSLOT` for each key and inspect whether hash tags are used.

### Resolution

Use a shared hash tag such as `{user:42}:profile` and `{user:42}:sessions` when atomic multi-key operations are required.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-REDIS-002 is the combination of the incident signature and diagnostic procedure above.

## BUSY Lua script

Evidence ID: KB-HYBRID-REDIS-003

### Incident signature

Commands fail with `BUSY Redis is busy running a script` and latency rises.

### Most likely cause

A Lua script is executing too long on Redis's main execution path.

### Diagnostic procedure

Inspect `SLOWLOG`, script runtime, collection sizes, and recent `EVAL` or `EVALSHA` calls.

### Resolution

Bound script work, redesign large scans, and use `SCRIPT KILL` only when operationally safe.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-REDIS-003 is the combination of the incident signature and diagnostic procedure above.

## READONLY replica write

Evidence ID: KB-HYBRID-REDIS-004

### Incident signature

A client receives `READONLY You can't write against a read only replica`.

### Most likely cause

The client is connected to a replica, often because topology or failover information is stale.

### Diagnostic procedure

Inspect `INFO replication`, the endpoint selected by the client, and failover state.

### Resolution

Route writes to the current primary and ensure topology discovery refreshes after failover.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-REDIS-004 is the combination of the incident signature and diagnostic procedure above.

## OOM maxmemory rejection

Evidence ID: KB-HYBRID-REDIS-005

### Incident signature

Writes fail with `OOM command not allowed when used memory > 'maxmemory'`.

### Most likely cause

Redis reached `maxmemory` and the configured policy cannot evict a suitable key.

### Diagnostic procedure

Inspect `INFO memory`, `CONFIG GET maxmemory`, `CONFIG GET maxmemory-policy`, TTL coverage, and `evicted_keys`.

### Resolution

Choose an intentional eviction policy or increase measured capacity; do not blindly remove the memory limit.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-REDIS-005 is the combination of the incident signature and diagnostic procedure above.

## MOVED cluster redirect

Evidence ID: KB-HYBRID-REDIS-006

### Incident signature

A client receives responses such as `MOVED 3999 10.0.0.8:6379`.

### Most likely cause

The client contacted a node that does not own the requested hash slot.

### Diagnostic procedure

Inspect cluster topology with `CLUSTER SLOTS` or `CLUSTER SHARDS` and confirm the client is cluster-aware.

### Resolution

Use a cluster-aware client and refresh slot mappings when topology changes.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-REDIS-006 is the combination of the incident signature and diagnostic procedure above.

## AOF truncated startup

Evidence ID: KB-HYBRID-REDIS-007

### Incident signature

Redis startup reports `Bad file format reading the append only file` or a truncated AOF.

### Most likely cause

The append-only file is incomplete or corrupted after an unclean write/storage event.

### Diagnostic procedure

Preserve the AOF, inspect startup logs, filesystem health, and validate a copy with `redis-check-aof`.

### Resolution

Repair a copy with the appropriate AOF check tool only after backup, then verify dataset integrity before restoring service.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-REDIS-007 is the combination of the incident signature and diagnostic procedure above.

## CLIENT output buffer limit

Evidence ID: KB-HYBRID-REDIS-008

### Incident signature

Pub/Sub or replica clients disconnect while Redis logs mention output buffer limits.

### Most likely cause

A slow consumer accumulated more queued output than `client-output-buffer-limit` permits.

### Diagnostic procedure

Inspect `CLIENT LIST`, output buffer fields, consumer throughput, and configured client buffer limits.

### Resolution

Fix slow consumers or message volume first; tune limits only with memory impact understood.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-REDIS-008 is the combination of the incident signature and diagnostic procedure above.

## WRONGTYPE command

Evidence ID: KB-HYBRID-REDIS-009

### Incident signature

A request fails with `WRONGTYPE Operation against a key holding the wrong kind of value`.

### Most likely cause

The application used a command incompatible with the key's current Redis data type.

### Diagnostic procedure

Inspect `TYPE <key>`, the command path, key naming, and writers that can reuse the same key.

### Resolution

Separate key namespaces/types and correct the writer or command rather than deleting unknown production data.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-REDIS-009 is the combination of the incident signature and diagnostic procedure above.

## NOSCRIPT after restart

Evidence ID: KB-HYBRID-REDIS-010

### Incident signature

`EVALSHA` returns `NOSCRIPT No matching script. Please use EVAL`.

### Most likely cause

The server's script cache no longer contains the SHA, commonly after restart or failover.

### Diagnostic procedure

Confirm the target node changed/restarted and inspect application script-loading behavior.

### Resolution

On `NOSCRIPT`, safely load or execute the known script body and refresh the cached SHA per node.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-REDIS-010 is the combination of the incident signature and diagnostic procedure above.
