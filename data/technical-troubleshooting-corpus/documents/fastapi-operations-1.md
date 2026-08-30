# FastAPI Production Runbook - Volume 1

This original training corpus contains operational troubleshooting procedures for fastapi. It is designed for retrieval evaluation, not as a substitute for vendor documentation or a production change-management process.

## 422 validation error

Evidence ID: KB-FASTAPI-001

### Incident signature

The primary signal is that the API returns 422 before endpoint logic runs. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, the request body, query parameters, or content type does not match the Pydantic schema. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, inspect the structured error location and generated OpenAPI contract. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to send the correct shape or revise the schema intentionally. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring the request body, query parameters, or content type does not match the Pydantic schema to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-FASTAPI-001 should connect the reported behavior - the API returns 422 before endpoint logic runs - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you inspect the structured error location and generated OpenAPI contract. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to send the correct shape or revise the schema intentionally, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-FASTAPI-001 is to connect a precise symptom to evidence before changing production state.

## Event loop blocked

Evidence ID: KB-FASTAPI-002

### Incident signature

The primary signal is that concurrent requests stall when one endpoint performs heavy work. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, blocking I/O or CPU work runs directly inside an async endpoint. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, profile the endpoint and look for synchronous libraries or CPU-bound loops. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to use async clients for I/O and move bounded CPU work to an executor or worker. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring blocking I/O or CPU work runs directly inside an async endpoint to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-FASTAPI-002 should connect the reported behavior - concurrent requests stall when one endpoint performs heavy work - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you profile the endpoint and look for synchronous libraries or CPU-bound loops. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to use async clients for I/O and move bounded CPU work to an executor or worker, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-FASTAPI-002 is to connect a precise symptom to evidence before changing production state.

## Dependency constructed per request

Evidence ID: KB-FASTAPI-003

### Incident signature

The primary signal is that model loading happens repeatedly and latency is extreme. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, an expensive provider is created inside a dependency without caching or application lifespan state. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, log construction count and inspect dependency scope. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to initialize expensive immutable providers once using lifespan management or a safe cache. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring an expensive provider is created inside a dependency without caching or application lifespan state to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-FASTAPI-003 should connect the reported behavior - model loading happens repeatedly and latency is extreme - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you log construction count and inspect dependency scope. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to initialize expensive immutable providers once using lifespan management or a safe cache, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-FASTAPI-003 is to connect a precise symptom to evidence before changing production state.

## File upload exhausts memory

Evidence ID: KB-FASTAPI-004

### Incident signature

The primary signal is that large uploads cause worker memory spikes. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, the endpoint reads the entire UploadFile into memory at once. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, profile RSS while uploading progressively larger files. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to stream the upload in bounded chunks and enforce size limits. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring the endpoint reads the entire UploadFile into memory at once to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-FASTAPI-004 should connect the reported behavior - large uploads cause worker memory spikes - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you profile RSS while uploading progressively larger files. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to stream the upload in bounded chunks and enforce size limits, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-FASTAPI-004 is to connect a precise symptom to evidence before changing production state.
