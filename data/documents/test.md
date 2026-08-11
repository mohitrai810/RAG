# Redis Persistence

Redis is an in-memory data structure store that can also provide persistence.

Redis persistence allows data to survive process restarts and system failures.

## RDB Persistence

RDB persistence creates point-in-time snapshots of the Redis dataset.

A snapshot represents the state of the dataset at a particular moment.

RDB files are compact and can be useful for backups and disaster recovery.

However, because snapshots happen periodically, data written between snapshots can potentially be lost if the system fails before the next snapshot.

## AOF Persistence

AOF stands for Append Only File.

Instead of periodically saving the complete dataset, Redis records write operations.

When Redis restarts, it can reconstruct the dataset by replaying these operations.

AOF can provide stronger durability than periodic snapshots depending on the configured synchronization policy.

## Choosing Between RDB and AOF

RDB is useful when compact backups and efficient recovery are important.

AOF is useful when minimizing data loss is more important.

Redis can also use both RDB and AOF together.

The correct configuration depends on the application's durability requirements, recovery objectives, and operational constraints.