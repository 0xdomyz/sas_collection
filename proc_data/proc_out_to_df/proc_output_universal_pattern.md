# PROC Output to Data: A Universal Pattern

A practical universal theory for SAS procedure output is this: every PROC has two channels.

1. A display channel sends human-readable tables to Results destinations (HTML, LISTING, PDF, and others).
2. A data channel materializes selected results as SAS datasets.

Most confusion comes from mixing these channels. Treat them as two separate pipes.

## Pipe 1: Display Output

By default, PROC steps produce display tables. In saspy, `sas.submitLST(...)` is convenient when your goal is quick inspection of printed output.

Example:

- `PROC FREQ` with `TABLES x*y / CHISQ` or `TABLES x*y / MEASURES` prints association statistics.
- These statistics are visible in output, but not automatically stored as reusable datasets unless you request them.

## Pipe 2: Dataset Output

SAS commonly provides three patterns for writing procedure output into datasets:

1. Native `OUT=` options in PROC or statement-level options.
   - Example: `PROC FREQ; TABLES a*b / OUT=work.ct; RUN;`
   - This is PROC-specific and usually yields one predefined dataset layout.
2. `ODS OUTPUT table-name=dataset`.
   - Example: `ODS OUTPUT Measures=work.freq_measures;`
   - This is the most universal pattern because many modern PROCs publish ODS table names.
3. Explicit `OUTPUT` statements (common in modeling procedures).
   - Example: `OUTPUT OUT=work._pred P=phat;`
   - This writes row-level predictions or diagnostics aligned with input observations.

## Universal Workflow

Use this sequence consistently:

1. Run the PROC once for readability.
2. Identify which output table/statistic you actually need.
3. Rerun with `ODS OUTPUT` (or native `OUT=` / `OUTPUT OUT=` when appropriate).
4. Inspect captured datasets with `PROC CONTENTS` and `PROC PRINT`.
5. Pull into Python/R only after the schema is clear.

## Simple PROC Examples

- `PROC LOGISTIC` can write predicted probabilities with `OUTPUT OUT=...` and can expose fit/stat tables through `ODS OUTPUT`.
- `PROC FREQ` can print Somers' D for a contingency table and capture the same information with `ODS OUTPUT Measures=...`.
- `PROC MEANS` can create summary datasets via `OUTPUT OUT=...`; specific report tables can still be captured through ODS.
