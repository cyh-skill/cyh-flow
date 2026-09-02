# Fix mode

Use this mode for one bounded repair of a known bug, failing behavior, or supported review finding. `fix` authorizes scoped local edits and proportionate validation, but it does not create a persistent Goal or promise to keep discovering and repairing issues until a finding-zero gate. Use `converge` for that persistent objective.

## Resolve the repair target

Identify the exact failure, expected behavior, source of truth, repository, scope, non-goals, and starting state. For a review finding, independently verify its trigger, reachability, and impact before patching it. For a reported failure, reproduce it when safe or establish a trustworthy causal explanation from code, tests, logs, or runtime evidence.

Trace far enough through callers, state transitions, error paths, contracts, platform variants, and sibling consumers to repair the root cause without silently broadening into unrelated cleanup. Preserve unrelated user changes and separate pre-existing failures from failures introduced by the repair.

If the requested target is not concrete enough to repair responsibly, perform safe investigation and ask only for the decision that blocks progress. Do not guess product behavior or turn an ambiguous report into an open-ended convergence loop.

## Parallel diagnosis

Decompose every independent diagnostic and validation surface and use the maximum useful subagent concurrency. Useful read-only lanes include reproducing the failure, tracing ownership and callers, checking contracts and platform variants, locating regression coverage, and analyzing safe logs or runtime evidence. Give each worker one falsifiable question and require evidence, affected paths, uncertainties, and a repair direction rather than a generic summary.

Keep exactly one repair writer, either the coordinator or one explicitly designated subagent. All other agents remain read-only against the shared repository; mutating checks run through the writer or in isolated non-conflicting environments. The writer verifies and integrates every result before editing, and no agent may expand this bounded repair into review or convergence unless the user selected that evidence or objective.

## Repair and validate

Use one writer. Implement the smallest coherent root-cause repair that satisfies the real contract and repository conventions; fewer lines are only a tiebreaker between equally correct and verifiable solutions. Add or strengthen a regression test when the project normally tests the behavior or the defect could recur.

The user may name the validation evidence for this repair, such as a focused test, four-lens review, simulator scenario, browser journey, runtime check, or performance measurement. Treat that request as authoritative and do not substitute an easier lane. If four-lens review is selected, load [review.md](review.md) and apply its frozen-target protocol. If no lane is specified, select and disclose checks proportionate to the changed behavior and risk.

Run the user-selected validation after the change. Do not automatically add routine unit, type, lint, build, review, browser, or device lanes when the user selected a narrower check; an extra diagnostic may run only when needed to understand or repair that flow and does not become a completion requirement without user acceptance. Browser automation uses the installed `cyh-browser-skill` through the active host mapping; simulator or device work uses established project tooling and official or vendor-maintained capabilities when available. Testing an external or production environment, writing test data, running impactful scans or load tests, and changing remote state require separate authorization.

Inspect the final diff for unintended files, generated noise, secrets, debug residue, incomplete callers, and unvalidated behavior. Report remaining findings or blocked evidence honestly. A one-shot `fix` may include several edits and checks needed to close the same root cause, but it must not silently expand into indefinite rounds or a general cleanup campaign.

## Handoff

If the user asks to keep inspecting, testing, repairing, and rechecking until supported findings reach zero, switch to `converge`, read [converge.md](converge.md), and create the Goal there. Do not claim convergence from a single repair pass.

Commit, push, PR changes, deployment, production writes, and messages to other people remain separate explicit actions. Never merge a PR.
