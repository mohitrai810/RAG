# Hybrid Retrieval Edge-Case Knowledge Base: DOCKER

Synthetic operational corpus for retrieval evaluation. Each incident has a stable evidence ID.

## Container exits 137

Evidence ID: KB-HYBRID-DOCKER-001

### Incident signature

A container terminates with exit code `137`.

### Most likely cause

The process received SIGKILL, commonly from an OOM kill or an explicit kill.

### Diagnostic procedure

Inspect `State.OOMKilled`, container memory metrics, host kernel logs, and configured limits.

### Resolution

Fix memory growth or batch sizing and set measured limits with headroom; distinguish OOM from manual SIGKILL.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-DOCKER-001 is the combination of the incident signature and diagnostic procedure above.

## Container exits 126

Evidence ID: KB-HYBRID-DOCKER-002

### Incident signature

A container exits with code `126` when starting its command.

### Most likely cause

The command was found but cannot be executed, commonly due to permissions or incompatible execution format.

### Diagnostic procedure

Inspect file mode, shebang/interpreter, mount options, and the configured entrypoint.

### Resolution

Make the intended executable runnable and ensure its interpreter exists in the image.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-DOCKER-002 is the combination of the incident signature and diagnostic procedure above.

## Container exits 127

Evidence ID: KB-HYBRID-DOCKER-003

### Incident signature

A container exits with code `127`.

### Most likely cause

The configured command or executable cannot be found in the container's PATH/filesystem.

### Diagnostic procedure

Inspect `ENTRYPOINT`, `CMD`, PATH, image contents, and shell form versus exec form.

### Resolution

Install/copy the executable or correct the command path.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-DOCKER-003 is the combination of the incident signature and diagnostic procedure above.

## DNS service-name failure

Evidence ID: KB-HYBRID-DOCKER-004

### Incident signature

One Compose service cannot resolve another service name.

### Most likely cause

The containers do not share the expected user-defined network or the wrong service name is used.

### Diagnostic procedure

Inspect `docker network inspect`, Compose configuration, aliases, and DNS lookup inside the container.

### Resolution

Attach services to a common network and connect using the Compose service name, not localhost.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-DOCKER-004 is the combination of the incident signature and diagnostic procedure above.

## Bind mount hides image files

Evidence ID: KB-HYBRID-DOCKER-005

### Incident signature

Files present during image build disappear when the container starts.

### Most likely cause

A bind mount overlays the image directory with the host directory.

### Diagnostic procedure

Inspect `docker inspect` mounts and compare the image filesystem without the mount.

### Resolution

Mount a narrower path or intentionally populate the host directory.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-DOCKER-005 is the combination of the incident signature and diagnostic procedure above.

## Healthcheck start period

Evidence ID: KB-HYBRID-DOCKER-006

### Incident signature

A slow-starting service becomes unhealthy before initialization finishes.

### Most likely cause

The healthcheck failure counter begins too early because startup behavior and `start_period` are mismatched.

### Diagnostic procedure

Inspect healthcheck command, interval, timeout, retries, start period, and real initialization time.

### Resolution

Use a realistic `start_period` while keeping the health probe strict after startup.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-DOCKER-006 is the combination of the incident signature and diagnostic procedure above.

## No space left build cache

Evidence ID: KB-HYBRID-DOCKER-007

### Incident signature

Docker builds fail with `no space left on device` despite small source code.

### Most likely cause

Image layers, build cache, stopped artifacts, or Docker's storage filesystem consumed available capacity.

### Diagnostic procedure

Inspect `docker system df`, filesystem usage, build cache, and large image layers.

### Resolution

Remove confirmed-unused artifacts and improve multi-stage builds; avoid indiscriminate cleanup on shared hosts.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-DOCKER-007 is the combination of the incident signature and diagnostic procedure above.

## Port binding conflict

Evidence ID: KB-HYBRID-DOCKER-008

### Incident signature

Container startup fails with `Bind for 0.0.0.0:8000 failed: port is already allocated`.

### Most likely cause

Another process or container already owns the requested host port.

### Diagnostic procedure

Inspect listening host sockets and running container port mappings.

### Resolution

Stop/reconfigure the conflicting owner or publish a different host port.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-DOCKER-008 is the combination of the incident signature and diagnostic procedure above.

## Permission denied volume

Evidence ID: KB-HYBRID-DOCKER-009

### Incident signature

An application gets permission denied when writing a named volume.

### Most likely cause

The runtime UID/GID does not have ownership or mode permissions for existing volume files.

### Diagnostic procedure

Compare numeric UID/GID inside the container with ownership of mounted files.

### Resolution

Initialize ownership deliberately and run the service as the intended non-root user.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-DOCKER-009 is the combination of the incident signature and diagnostic procedure above.

## Compose env interpolation

Evidence ID: KB-HYBRID-DOCKER-010

### Incident signature

A Compose variable unexpectedly becomes empty or takes a surprising value.

### Most likely cause

Compose-time interpolation and container runtime environment configuration were confused.

### Diagnostic procedure

Run `docker compose config`, inspect `.env` location, `env_file`, shell variables, and required-variable syntax.

### Resolution

Separate interpolation from runtime configuration and fail startup when required settings are missing.

### Retrieval traps

Do not confuse this incident with neighboring failures merely because they share terms such as error, timeout, memory, connection, or permission. Exact identifiers and observed behavior matter. The decisive evidence for KB-HYBRID-DOCKER-010 is the combination of the incident signature and diagnostic procedure above.
