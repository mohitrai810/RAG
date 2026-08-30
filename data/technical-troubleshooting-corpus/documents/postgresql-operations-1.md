# PostgreSQL Operations Runbook - Volume 1

This original training corpus contains operational troubleshooting procedures for postgresql. It is designed for retrieval evaluation, not as a substitute for vendor documentation or a production change-management process.

## Too many connections

Evidence ID: KB-POSTGRESQL-001

### Incident signature

The primary signal is that new sessions fail with remaining connection slots are reserved. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, application pools collectively exceed max_connections or leak checked-out sessions. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, inspect pg_stat_activity grouped by application and state. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to set bounded pools, close sessions reliably, and use PgBouncer where appropriate. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring application pools collectively exceed max_connections or leak checked-out sessions to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-POSTGRESQL-001 should connect the reported behavior - new sessions fail with remaining connection slots are reserved - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you inspect pg_stat_activity grouped by application and state. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to set bounded pools, close sessions reliably, and use PgBouncer where appropriate, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-POSTGRESQL-001 is to connect a precise symptom to evidence before changing production state.

## Idle in transaction sessions

Evidence ID: KB-POSTGRESQL-002

### Incident signature

The primary signal is that vacuum cannot reclaim tuples and idle in transaction sessions accumulate. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, clients begin transactions and wait without commit or rollback. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, inspect xact_start, state_change, query, and backend ownership. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to fix transaction boundaries and configure idle_in_transaction_session_timeout. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring clients begin transactions and wait without commit or rollback to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-POSTGRESQL-002 should connect the reported behavior - vacuum cannot reclaim tuples and idle in transaction sessions accumulate - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you inspect xact_start, state_change, query, and backend ownership. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to fix transaction boundaries and configure idle_in_transaction_session_timeout, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-POSTGRESQL-002 is to connect a precise symptom to evidence before changing production state.

## Deadlock detected

Evidence ID: KB-POSTGRESQL-003

### Incident signature

The primary signal is that one transaction is aborted with deadlock detected. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, concurrent transactions lock the same resources in inconsistent order. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, read the deadlock log and map each lock to the statements involved. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to use a consistent lock order, shorten transactions, and retry aborted transactions. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring concurrent transactions lock the same resources in inconsistent order to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-POSTGRESQL-003 should connect the reported behavior - one transaction is aborted with deadlock detected - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you read the deadlock log and map each lock to the statements involved. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to use a consistent lock order, shorten transactions, and retry aborted transactions, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-POSTGRESQL-003 is to connect a precise symptom to evidence before changing production state.

## Sequential scan after adding index

Evidence ID: KB-POSTGRESQL-004

### Incident signature

The primary signal is that EXPLAIN still shows a sequential scan. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, the predicate is not selective, statistics are stale, or the expression does not match the index. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, run EXPLAIN ANALYZE and inspect statistics, casts, and predicate shape. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to refresh statistics and create an index matching the actual predicate only when selective. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring the predicate is not selective, statistics are stale, or the expression does not match the index to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-POSTGRESQL-004 should connect the reported behavior - EXPLAIN still shows a sequential scan - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you run EXPLAIN ANALYZE and inspect statistics, casts, and predicate shape. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to refresh statistics and create an index matching the actual predicate only when selective, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-POSTGRESQL-004 is to connect a precise symptom to evidence before changing production state.
