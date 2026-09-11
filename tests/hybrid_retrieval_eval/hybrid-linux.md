# Hybrid Retrieval Edge-Case Knowledge Base: LINUX

Synthetic operational corpus for retrieval evaluation. Each incident has a stable evidence ID.

## Too many open files

Evidence ID: KB-HYBRID-LINUX-001

### Incident signature

A service fails with `Too many open files` / `EMFILE`.

### Most likely cause

The process reached its file descriptor limit due to high concurrency or leaked descriptors.

### Diagnostic procedure

Inspect `/proc/<pid>/limits`, `ulimit -n`, descriptor count, and descriptor types under `/proc/<pid>/fd`.

### Resolution

Fix descriptor leaks and set an evidence-based limit appropriate for expected concurrency.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-LINUX-001 is the combination of the incident signature and diagnostic procedure above.

## Killed process OOM

Evidence ID: KB-HYBRID-LINUX-002

### Incident signature

A Linux process disappears and kernel logs contain `Out of memory: Killed process`.

### Most likely cause

The kernel OOM killer selected the process under memory pressure.

### Diagnostic procedure

Inspect kernel logs, cgroup memory events, RSS trends, swap behavior, and memory limits.

### Resolution

Fix memory pressure/leaks and configure realistic cgroup/service limits with headroom.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-LINUX-002 is the combination of the incident signature and diagnostic procedure above.

## Address already in use

Evidence ID: KB-HYBRID-LINUX-003

### Incident signature

A server fails to bind with `EADDRINUSE` / `Address already in use`.

### Most likely cause

Another socket already owns the requested address and port, or restart timing conflicts with socket behavior.

### Diagnostic procedure

Inspect listeners using `ss -ltnp` and identify the owning process.

### Resolution

Stop/reconfigure the conflicting service or choose the correct port; do not blindly kill unrelated processes.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-LINUX-003 is the combination of the incident signature and diagnostic procedure above.

## Read-only filesystem

Evidence ID: KB-HYBRID-LINUX-004

### Incident signature

Writes fail with `Read-only file system` / `EROFS`.

### Most likely cause

The filesystem or mount is read-only, possibly intentionally or after filesystem errors.

### Diagnostic procedure

Inspect `findmnt`, mount options, kernel logs, filesystem health, and container mount configuration.

### Resolution

Determine why it became read-only before remounting; repair storage/filesystem issues safely.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-LINUX-004 is the combination of the incident signature and diagnostic procedure above.

## No space but df free

Evidence ID: KB-HYBRID-LINUX-005

### Incident signature

Writes fail with `No space left on device` while `df -h` shows free capacity.

### Most likely cause

The filesystem may have exhausted inodes rather than data blocks.

### Diagnostic procedure

Compare `df -h` with `df -i` and identify directories containing huge numbers of small files.

### Resolution

Remove/rotate confirmed-unneeded files and redesign unbounded small-file creation.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-LINUX-005 is the combination of the incident signature and diagnostic procedure above.

## DNS intermittent

Evidence ID: KB-HYBRID-LINUX-006

### Incident signature

Applications intermittently fail hostname resolution while IP connectivity works.

### Most likely cause

Resolver configuration, upstream DNS, search domains, timeouts, or packet loss is causing name-resolution failures.

### Diagnostic procedure

Inspect `/etc/resolv.conf`, `resolvectl`, `getent hosts`, DNS latency, and packet loss.

### Resolution

Repair resolver/upstream configuration and avoid hard-coding IP addresses as the permanent fix.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-LINUX-006 is the combination of the incident signature and diagnostic procedure above.

## Clock skew TLS

Evidence ID: KB-HYBRID-LINUX-007

### Incident signature

TLS/authentication requests fail intermittently with certificate-not-yet-valid or token-time errors.

### Most likely cause

System clock drift exceeds the tolerance of certificates or signed-token validation.

### Diagnostic procedure

Inspect `timedatectl`, NTP synchronization state, chrony/systemd-timesyncd metrics, and UTC timestamps.

### Resolution

Restore reliable time synchronization and alert on clock offset.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-LINUX-007 is the combination of the incident signature and diagnostic procedure above.

## Permission denied executable

Evidence ID: KB-HYBRID-LINUX-008

### Incident signature

A script exists but execution returns `Permission denied`.

### Most likely cause

Execute permission is missing, the filesystem is mounted `noexec`, or directory traversal permission is absent.

### Diagnostic procedure

Inspect `ls -l`, `namei -l`, mount options, ownership, and security policy logs.

### Resolution

Correct the specific permission or mount policy rather than applying broad `chmod 777`.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-LINUX-008 is the combination of the incident signature and diagnostic procedure above.

## Zombie processes

Evidence ID: KB-HYBRID-LINUX-009

### Incident signature

Many processes appear with state `Z` and do not disappear.

### Most likely cause

Child processes exited but their parent has not called wait/waitpid to reap them.

### Diagnostic procedure

Inspect `ps` state, PPID relationships, and the parent process's child-handling behavior.

### Resolution

Fix the parent to reap children or use a proper init/subreaper in containers.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-LINUX-009 is the combination of the incident signature and diagnostic procedure above.

## High load low CPU

Evidence ID: KB-HYBRID-LINUX-010

### Incident signature

Linux load average is high while CPU utilization is modest.

### Most likely cause

Many tasks may be blocked in uninterruptible I/O sleep, so they contribute to load without consuming CPU.

### Diagnostic procedure

Inspect `ps` task states, `vmstat`, `iostat`, storage latency, and kernel stack/wait information.

### Resolution

Resolve the underlying I/O bottleneck instead of adding CPU based only on load average.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-LINUX-010 is the combination of the incident signature and diagnostic procedure above.
