# Concepts and trade-offs

**Three Vs:** Volume = amount of data; Velocity = rate of data arrival; Variety = different formats and schemas. Also consider veracity (quality) and value (business use).

**Distributed storage:** Data is partitioned across multiple nodes (e.g. HDFS or object storage). This project uses a single local filesystem; it does not configure HDFS.

**Distributed processing:** Spark schedules partition tasks across executors; `local[2]` uses two local worker threads in one JVM, not a physical multi-node cluster.

**SparkSession:** Application entrypoint for DataFrame and SQL operations. **DataFrames:** schema-based, optimized distributed collections. **Transformation:** `select`, `filter`, `join` describe computation lazily. **Action:** `count`, `show`, `write` triggers execution.

**Shuffle:** Moving data between partitions (groupBy, certain joins, windows); can be costly. **Partitioning:** Controls parallelism but too many tiny partitions create overhead.

**Quality dimensions:** completeness (required fields), uniqueness (no duplicate keys), validity (range, type, enum), consistency (cross-field/business rules), timeliness (fresh records), accuracy (agreement with trusted ground truth). Automated rules cannot guarantee actual-world accuracy.

**Data quality gate:** Raw -> rule checks -> clean Parquet / rejected JSON -> JSON metrics. Duplicate order IDs are all quarantined rather than arbitrarily keeping one; choose deduplication policy with business owners.

**UDF trade-off:** Python UDF adds serialization and execution overhead; Spark built-in SQL expressions usually optimize better. Example script illustrates both.

**Production next steps:** Configure managed cluster and object storage, check referential integrity against customers, introduce source-level SLAs, schema evolution, quarantine reason codes, orchestrate pipeline, use incremental input rather than overwrite, and monitor quality trends.

**Great Expectations (GX):** A framework for describing expectations, running validations, and saving results. Conceptual steps: create Data Context; connect Data Source and Data Asset; define Expectation Suite; run Validation and optionally Checkpoint. `pip install great_expectations` optional. See official GX Core guides for version-specific API examples.
