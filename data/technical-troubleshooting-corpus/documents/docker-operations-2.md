# Docker Operations Runbook - Volume 2

This original training corpus contains operational troubleshooting procedures for docker. It is designed for retrieval evaluation, not as a substitute for vendor documentation or a production change-management process.

## Named volume permission denied

Evidence ID: KB-DOCKER-005

### Incident signature

The primary signal is that the application cannot write to its mounted data directory. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, the container UID does not own the existing volume files. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, inspect numeric UID and GID both inside the container and on the volume. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to set correct ownership during initialization and avoid running the whole service as root. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring the container UID does not own the existing volume files to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-DOCKER-005 should connect the reported behavior - the application cannot write to its mounted data directory - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you inspect numeric UID and GID both inside the container and on the volume. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to set correct ownership during initialization and avoid running the whole service as root, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-DOCKER-005 is to connect a precise symptom to evidence before changing production state.

## Build cache ignores changed dependency

Evidence ID: KB-DOCKER-006

### Incident signature

The primary signal is that a rebuilt image still contains an old package set. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, Dockerfile layer ordering or an unexpected build context preserved a cached dependency layer. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, review Dockerfile COPY order and rebuild with plain progress output. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to copy dependency manifests before source and invalidate only the necessary layer. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring Dockerfile layer ordering or an unexpected build context preserved a cached dependency layer to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-DOCKER-006 should connect the reported behavior - a rebuilt image still contains an old package set - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you review Dockerfile COPY order and rebuild with plain progress output. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to copy dependency manifests before source and invalidate only the necessary layer, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-DOCKER-006 is to connect a precise symptom to evidence before changing production state.

## Image is unexpectedly large

Evidence ID: KB-DOCKER-007

### Incident signature

The primary signal is that a small application produces a multi-gigabyte image. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, build tools, caches, model files, or package-manager artifacts remain in final layers. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, inspect layer sizes with docker history. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to use multi-stage builds and remove caches in the same layer where they are created. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring build tools, caches, model files, or package-manager artifacts remain in final layers to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-DOCKER-007 should connect the reported behavior - a small application produces a multi-gigabyte image - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you inspect layer sizes with docker history. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to use multi-stage builds and remove caches in the same layer where they are created, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-DOCKER-007 is to connect a precise symptom to evidence before changing production state.

## Health check passes too early

Evidence ID: KB-DOCKER-008

### Incident signature

The primary signal is that dependent services start while the application is not ready. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, the check verifies process existence rather than functional readiness. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, run the health command manually during startup and inspect timing. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to check a dependency-backed readiness endpoint and configure interval, timeout, and retries. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring the check verifies process existence rather than functional readiness to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-DOCKER-008 should connect the reported behavior - dependent services start while the application is not ready - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you run the health command manually during startup and inspect timing. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to check a dependency-backed readiness endpoint and configure interval, timeout, and retries, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-DOCKER-008 is to connect a precise symptom to evidence before changing production state.
