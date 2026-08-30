# Linux Systems Runbook - Volume 3

This original training corpus contains operational troubleshooting procedures for linux. It is designed for retrieval evaluation, not as a substitute for vendor documentation or a production change-management process.

## Inode exhaustion

Evidence ID: KB-LINUX-009

### Incident signature

The primary signal is that writes fail with no space left despite available disk blocks. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, the filesystem has exhausted inodes because of many small files. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, compare df -h with df -i and locate high file-count directories. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to remove unnecessary small files and redesign retention or filesystem layout. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring the filesystem has exhausted inodes because of many small files to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-LINUX-009 should connect the reported behavior - writes fail with no space left despite available disk blocks - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you compare df -h with df -i and locate high file-count directories. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to remove unnecessary small files and redesign retention or filesystem layout, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-LINUX-009 is to connect a precise symptom to evidence before changing production state.

## Clock drift breaks authentication

Evidence ID: KB-LINUX-010

### Incident signature

The primary signal is that tokens appear expired or not yet valid across otherwise healthy services. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, host clocks differ beyond the protocol tolerance. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, compare timedatectl and chrony tracking across nodes. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to restore time synchronization and monitor offset. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring host clocks differ beyond the protocol tolerance to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-LINUX-010 should connect the reported behavior - tokens appear expired or not yet valid across otherwise healthy services - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you compare timedatectl and chrony tracking across nodes. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to restore time synchronization and monitor offset, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-LINUX-010 is to connect a precise symptom to evidence before changing production state.

## CPU throttling in container

Evidence ID: KB-LINUX-011

### Incident signature

The primary signal is that latency rises while reported application CPU remains below a full core. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, cgroup CPU quota throttles runnable work. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, inspect cpu.stat throttled periods and quota settings. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to set measured CPU limits or reduce concurrency and CPU demand. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring cgroup CPU quota throttles runnable work to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-LINUX-011 should connect the reported behavior - latency rises while reported application CPU remains below a full core - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you inspect cpu.stat throttled periods and quota settings. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to set measured CPU limits or reduce concurrency and CPU demand, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-LINUX-011 is to connect a precise symptom to evidence before changing production state.

## Log rotation does not reclaim space

Evidence ID: KB-LINUX-012

### Incident signature

The primary signal is that a rotated log is removed but filesystem usage stays high. Treat the first report as a symptom, not as proof of the underlying cause. Capture timestamps, affected instances, recent deployments, and whether the behavior is continuous or intermittent before making changes.

### Most likely cause

In this scenario, the application keeps writing through an open descriptor to the deleted inode. Similar-looking incidents can have different causes, so do not apply the resolution until the diagnostic observations agree with this explanation.

### Diagnostic procedure

First, use lsof plus L1 to identify the handle. Preserve the original error and collect measurements from the same time window. Compare one affected instance with a healthy instance when possible. Avoid restarting immediately because a restart can destroy the state needed to distinguish configuration, capacity, and application defects.

### Resolution

The preferred corrective action is to signal the application to reopen logs or restart it safely. Apply the smallest reversible change first, verify the original symptom disappears, and then confirm normal behavior under representative load. Record the command, owner, timestamp, and observed result.

### Verification and rollback

Verification requires both recovery and stability. Repeat the failing operation, watch the relevant service and host metrics, and confirm that no neighboring error rate increases. If the change produces a regression, revert it using the recorded previous configuration rather than stacking additional speculative changes.

### Counterfactual checks

Before declaring the application keeps writing through an open descriptor to the deleted inode to be confirmed, attempt to disprove it. Check whether the same symptom occurs where the suspected condition is absent, and whether the condition exists on healthy instances. If those comparisons disagree with the hypothesis, return to evidence collection. In particular, do not confuse correlation after a deployment with causation. The decisive observation for KB-LINUX-012 should connect the reported behavior - a rotated log is removed but filesystem usage stays high - to the specific diagnostic signals listed above.

### Evidence package for escalation

If the incident cannot be resolved locally, prepare a compact escalation package. Include the UTC time window, software version, topology, sanitized configuration, the exact failing operation, and the output gathered when you use lsof plus L1 to identify the handle. Include what changed recently and which proposed causes were ruled out. Do not include passwords, tokens, customer payloads, or an unrestricted diagnostic archive. A good escalation lets another engineer test the same hypothesis without repeating discovery from the beginning.

### Operational safety notes

Avoid destructive cleanup, broad permission changes, unbounded retries, and emergency capacity changes without a rollback point. When the recommended action is to signal the application to reopen logs or restart it safely, stage it on one instance or a controlled environment when possible. Measure the relevant success signal before and after the change. If production impact requires immediate mitigation, separate the temporary mitigation from the permanent correction and create a follow-up item with an owner and deadline.

### Prevention

Add an alert for the earliest measurable precursor, document the capacity or configuration boundary, and create a regression test when the failure can be reproduced safely. The durable lesson for KB-LINUX-012 is to connect a precise symptom to evidence before changing production state.
