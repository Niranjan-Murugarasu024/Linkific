# Known Issues and Environment Notes

1. **DBFS root may be disabled.** Use a Unity Catalog Volume path for both input and output when the workspace does not allow DBFS FileStore access. Update `INPUT_PATH` and `OUTPUT_BASE_PATH` in the notebook.
2. **Compute permissions matter.** The attached Databricks compute must support Spark and Delta Lake and have permission to read/write the selected storage location.
3. **Delta optimization support varies.** The notebook first attempts `OPTIMIZE ... ZORDER BY`. If that operation is not supported, it attempts plain `OPTIMIZE`. If both fail, the reason is written to `performance_report.json`.
4. **Small workload benchmarks are noisy.** 200K rows is large enough to test the pipeline mechanics but may be too small to show meaningful improvements from every physical-layout optimization.
5. **Spark writes directory-based CSV output.** Report folders such as `batch_metrics.csv/` contain part files; they are not necessarily single CSV files.
6. **Manifest is an oracle, not pipeline input.** Keep it out of the Bronze-to-Silver classification logic. The notebook joins it only after classification.
7. **The update test is isolated.** A temporary Delta copy is updated to verify MERGE semantics; the authoritative Silver output is not modified by this test.
8. **The supplied synthetic data is not real customer data.** All names, identifiers and email addresses are deterministic placeholders using the reserved `example.test` domain.
