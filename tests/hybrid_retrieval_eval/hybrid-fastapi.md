# Hybrid Retrieval Edge-Case Knowledge Base: API

Synthetic operational corpus for retrieval evaluation. Each incident has a stable evidence ID.

## 422 validation error

Evidence ID: KB-HYBRID-API-001

### Incident signature

FastAPI returns HTTP `422` before the endpoint body runs.

### Most likely cause

Request data failed Pydantic validation for path, query, header, or body inputs.

### Diagnostic procedure

Inspect the response `detail`, generated OpenAPI schema, content type, and actual payload shape.

### Resolution

Correct the client payload or schema contract; do not catch the error inside endpoint business logic.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-API-001 is the combination of the incident signature and diagnostic procedure above.

## Blocking call in async route

Evidence ID: KB-HYBRID-API-002

### Incident signature

Concurrent FastAPI requests stall even though the endpoint uses `async def`.

### Most likely cause

Synchronous blocking CPU or I/O work runs directly on the event-loop thread.

### Diagnostic procedure

Profile the route and inspect blocking library calls, CPU work, and event-loop lag.

### Resolution

Use async-compatible I/O or move blocking work to an appropriate thread/process/worker.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-API-002 is the combination of the incident signature and diagnostic procedure above.

## CORS preflight failure

Evidence ID: KB-HYBRID-API-003

### Incident signature

A browser sends `OPTIONS` and blocks the real API request due to CORS.

### Most likely cause

CORS middleware does not allow the requesting origin, method, or headers.

### Diagnostic procedure

Inspect browser network details and configured `allow_origins`, `allow_methods`, and `allow_headers`.

### Resolution

Configure the smallest required CORS policy and handle credentials/origins consistently.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-API-003 is the combination of the incident signature and diagnostic procedure above.

## 413 upload too large

Evidence ID: KB-HYBRID-API-004

### Incident signature

A client receives HTTP `413 Request Entity Too Large` before a large upload reaches FastAPI.

### Most likely cause

A reverse proxy or gateway request-body limit rejects the payload upstream.

### Diagnostic procedure

Inspect proxy/gateway logs and body-size settings such as Nginx `client_max_body_size`.

### Resolution

Set an intentional upload limit across proxy and application and prefer streaming for large files.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-API-004 is the combination of the incident signature and diagnostic procedure above.

## 502 from reverse proxy

Evidence ID: KB-HYBRID-API-005

### Incident signature

Nginx returns HTTP `502 Bad Gateway` while the FastAPI container appears healthy.

### Most likely cause

The proxy cannot successfully connect to the configured upstream due to address, port, DNS, protocol, or process availability.

### Diagnostic procedure

Inspect Nginx error logs, upstream address, container networking, and direct connectivity from the proxy container.

### Resolution

Use the correct service DNS/port and add readiness-aware deployment behavior.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-API-005 is the combination of the incident signature and diagnostic procedure above.

## 504 gateway timeout

Evidence ID: KB-HYBRID-API-006

### Incident signature

A reverse proxy returns HTTP `504 Gateway Timeout` during a long generation request.

### Most likely cause

The upstream did not produce the required response within the proxy timeout window.

### Diagnostic procedure

Compare upstream processing time with proxy read timeout and inspect whether streaming emits data early.

### Resolution

Fix excessive upstream latency and align timeouts; use streaming when appropriate rather than only inflating limits.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-API-006 is the combination of the incident signature and diagnostic procedure above.

## Duplicate background work

Evidence ID: KB-HYBRID-API-007

### Incident signature

The same asynchronous job is processed twice after retries.

### Most likely cause

Delivery is at-least-once or the producer retried without an idempotency boundary.

### Diagnostic procedure

Inspect job IDs, enqueue attempts, worker acknowledgements, and durable status transitions.

### Resolution

Make job processing idempotent with a stable job/idempotency key and atomic state transitions.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-API-007 is the combination of the incident signature and diagnostic procedure above.

## Dependency pool exhaustion

Evidence ID: KB-HYBRID-API-008

### Incident signature

Requests wait before endpoint logic because a database dependency cannot obtain a connection.

### Most likely cause

The SQLAlchemy pool is exhausted by concurrency, long transactions, or leaked sessions.

### Diagnostic procedure

Measure pool checkout/wait time, active sessions, transaction duration, and pool configuration.

### Resolution

Close sessions reliably, shorten transactions, and size bounded pools from measured concurrency.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-API-008 is the combination of the incident signature and diagnostic procedure above.

## Streaming buffered by proxy

Evidence ID: KB-HYBRID-API-009

### Incident signature

FastAPI yields streaming chunks but the client receives the response all at once.

### Most likely cause

A proxy or intermediary buffers the upstream response.

### Diagnostic procedure

Inspect response headers and proxy buffering settings, and test direct versus proxied streaming.

### Resolution

Disable buffering for the streaming route where appropriate and ensure chunks are flushed.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-API-009 is the combination of the incident signature and diagnostic procedure above.

## Client disconnect generation

Evidence ID: KB-HYBRID-API-010

### Incident signature

Expensive generation continues after the HTTP client has disconnected.

### Most likely cause

The application does not propagate or check cancellation/disconnect state during long-running work.

### Diagnostic procedure

Inspect request disconnect state, provider cancellation support, and worker lifecycle.

### Resolution

Check for disconnects and cancel downstream work when safe to avoid wasted compute.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-API-010 is the combination of the incident signature and diagnostic procedure above.
