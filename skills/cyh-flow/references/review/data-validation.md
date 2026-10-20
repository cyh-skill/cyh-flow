# Review data validation

When a review needs data validation, proactively obtain the necessary data through database queries, API calls, logs, or real business data for focused testing and evaluation. This applies to validating business logic, boundary conditions, data consistency, and actual impact as well as investigating bugs; an unclear issue or suspected defect is not a prerequisite. Prefer observed evidence over speculative conclusions. When static analysis already provides sufficient evidence, do not add unnecessary data retrieval or checks.

Use read-only access to relevant data sources and keep focused tests within the review's existing non-mutating boundary; evaluate real business data in an approved temporary or disposable environment when execution would otherwise change state. Production access is read-only by default, and modifying production data without explicit authorization is prohibited. An API call's HTTP method alone does not establish that it is non-mutating.

Report the data source and environment, validation performed, results, and material limits without exposing credentials or sensitive raw business data. If necessary data or access is unavailable, identify the missing evidence and its effect on the conclusion rather than treating an assumption as verified.
