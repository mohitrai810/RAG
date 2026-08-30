# Redis Operations Runbook - Volume 2

This original training corpus contains operational troubleshooting procedures for redis. It is designed for retrieval evaluation, not as a substitute for vendor documentation or a production change-management process.

## Evictions despite apparent free host memory

Evidence ID: KB-REDIS-005

### Incident signature

The primary signal is that evicted_keys increases although the host still has free RAM. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, maxmemory is lower than host capacity and the configured eviction policy is active. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, inspect maxmemory, maxmemory-policy, used_memory, and evicted_keys. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to set an intentional memory limit and choose an eviction policy matching the workload. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring maxmemory is lower than host capacity and the configured eviction policy is active to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-REDIS-005 should connect the reported behavior - evicted_keys increases although the host still has free RAM - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you inspect maxmemory, maxmemory-policy, used_memory, and evicted_keys. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to set an intentional memory limit and choose an eviction policy matching the workload, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-REDIS-005 is to connect a precise symptom to evidence before changing production state.

## NOAUTH after deployment

Evidence ID: KB-REDIS-006

### Incident signature

The primary signal is that applications receive NOAUTH Authentication required after a configuration rollout. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, the server now requires ACL authentication but clients did not send credentials. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, run ACL WHOAMI with an authenticated session and inspect client connection configuration. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to configure username and password securely and rotate exposed credentials. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring the server now requires ACL authentication but clients did not send credentials to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-REDIS-006 should connect the reported behavior - applications receive NOAUTH Authentication required after a configuration rollout - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you run ACL WHOAMI with an authenticated session and inspect client connection configuration. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to configure username and password securely and rotate exposed credentials, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-REDIS-006 is to connect a precise symptom to evidence before changing production state.

## WRONGTYPE on existing key

Evidence ID: KB-REDIS-007

### Incident signature

The primary signal is that a command fails with WRONGTYPE Operation against a key holding the wrong kind of value. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, two code paths reused the same key name for different Redis data types. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, use TYPE and OBJECT ENCODING and trace every writer of the key. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to introduce namespaced keys, migrate conflicting data, and add contract tests. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring two code paths reused the same key name for different Redis data types to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-REDIS-007 should connect the reported behavior - a command fails with WRONGTYPE Operation against a key holding the wrong kind of value - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you use TYPE and OBJECT ENCODING and trace every writer of the key. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to introduce namespaced keys, migrate conflicting data, and add contract tests, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-REDIS-007 is to connect a precise symptom to evidence before changing production state.

## Blocked clients accumulate

Evidence ID: KB-REDIS-008

### Incident signature

The primary signal is that blocked_clients rises and request latency increases. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, long blocking operations or consumers waiting on empty streams hold connections. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, inspect CLIENT LIST, command names, and blocking durations. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to bound blocking timeouts, size the connection pool, and separate worker connections. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring long blocking operations or consumers waiting on empty streams hold connections to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-REDIS-008 should connect the reported behavior - blocked_clients rises and request latency increases - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you inspect CLIENT LIST, command names, and blocking durations. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to bound blocking timeouts, size the connection pool, and separate worker connections, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-REDIS-008 is to connect a precise symptom to evidence before changing production state.
