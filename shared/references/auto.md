# Auto mode

Use top-level `<cyh-flow> auto <source>` for an explicit unattended local delivery pipeline. It runs the requested implementation as `build auto` to completion, records the resulting working target, then runs `converge` with the derived review and test matrix until zero supported findings remain. The invocation delegates safe, reversible, in-scope engineering decisions; commit, push, PR mutation, deployment, production or external writes, messages to people, merge, and destructive operations remain outside its authorization.

This mode orchestrates two sequential existing protocols: read [build.md](build.md) and complete phase one, then read [converge.md](converge.md) and [review-deep.md](review-deep.md) for phase two. Each phase keeps its own Goal and completion gate.

## Orchestration ledger and Goal sequence

Use one repository-local orchestration ledger as the durable source of phase state. Follow an existing project convention when one exists; otherwise use `.cyh-flow/auto/<stable-objective-slug>.md` in the coordinating repository. Keep it local and unstaged unless the user explicitly requests delivery, and do not add ignore rules as a side effect. The coordinator is its sole writer; subagents report evidence and never edit it.

Record the objective, source of truth, repositories, starting revisions, non-goals, authorization boundary, current phase, phase-specific Goal and ledger paths, working targets, derived evidence matrix, decisions, blockers, resume cursor, and final evidence. For cross-repository work, name the repository in every task and result. Do not store secrets, personal data, credentials, or unbounded logs.

Maintain only one active Goal under the host mapping, so do not create a simultaneous parent Goal. Codex can sequence its native Goal API; Claude Code may use one user-activated session `/goal`, Task records for the two phases, and the orchestration ledger, but must not claim two independently addressable native Goals or replace an unrelated active `/goal`. Sequence exactly two logical phase Goals:

1. Create or resume the build Goal under the rules for explicit `<cyh-flow> build auto`. Record it as `build` in the orchestration ledger and execute it until its own completion gate is satisfied. A blocked or incomplete build stops the pipeline; do not start convergence.
2. Inspect and record the complete post-build target, mark the build phase complete in the orchestration ledger, and only then complete the build Goal.
3. Create or resume a separate convergence Goal over that working target. Record it as `converge`, derive the mandatory evidence matrix below, and execute the converge repair-and-recheck loop until its own completion gate is satisfied.
4. Mark the orchestration ledger complete only after both Goals completed against the recorded targets and the final convergence evidence covers every applicable lane.

If an unrelated unfinished Goal prevents phase creation, do not replace it. Record the conflict and stop. On resume, read the orchestration ledger, the current Goal, and the phase ledger first; verify repository state before continuing from the recorded cursor. A pending human-review status on an in-scope build decision does not pause the pipeline unless the user explicitly made human acceptance a completion requirement; the convergence review must still inspect the code and behavior resulting from that decision.

## Derived review and test matrix

The matrix covers the review and automated-check lanes applicable to the affected behavior and project contract. Derive and record it before convergence, including each lane's procedure, target, resource, side-effect risk, and evidence for inclusion. Browser, simulator, device, deployment, remote-environment, and business-acceptance lanes are included when the user or an authoritative acceptance contract explicitly selects them. Availability affects execution status rather than applicability; an unavailable required lane blocks completion.

The matrix must include:

- deep code review using [review-deep.md](review-deep.md): four independent live specialist reviews and a fresh master recheck;
- every applicable established automated check discoverable from repository instructions, CI definitions, package scripts, build files, and affected-module conventions, including focused and broader unit, integration, end-to-end, type, lint, build, schema, migration, contract, or packaging checks as relevant;
- user-selected or contract-required platform and user-flow checks, such as browser journeys, API flows, simulator, emulator, device, accessibility, or runtime-log validation, executed in an authorized safe test environment;
- existing security, performance, compatibility, recovery, or data-integrity checks when the changed surface or repository contract makes them applicable.

Use project instructions and impact analysis to decide automated-check applicability and explain material exclusions. Established local checks are the default execution surface. Remote CI triggers, external-environment mutation, load testing, and production access require their own authorization. A selected browser lane uses the installed `cyh-browser-skill` through the active host mapping. Checks sharing a browser, simulator, device, database, dependency cache, build output, or other mutable resource run serially.

An applicable lane that is unavailable or requires new permission remains required and blocks completion; do not silently downgrade it to optional. Separate pre-existing failures from regressions, but a baseline failure in a required lane still prevents a passing result unless the Goal contract supplies an evidence-grounded disposition that preserves the intended acceptance meaning.

## Unattended execution and repair

Within the stated objective and local authorization, resolve routine ambiguity, implementation trade-offs, test failures, reviewer findings, agent failures, and retryable tooling issues using repository evidence and the safest coherent choice. Record material decisions before relying on them, preserve their rationale and reversibility, and keep dependency-ready work moving. Do not ask for confirmation merely because a choice requires engineering judgment.

Stop only when continuing would change the objective or scope, require new authorization or an external mutation, be destructive or not safely reversible, depend on an unavailable required environment, conflict with another active Goal or shared resource that cannot be serialized, or require a material product decision that repository evidence cannot resolve safely. Record the exact blocker and keep the current phase and orchestration ledger incomplete.

During convergence, use one mutually exclusive repair writer and parallel read-only evidence workers. Every supported in-scope finding enters the finding ledger, is repaired or disposed of with evidence, and invalidates the affected evidence lanes. After the final repair, inspect the complete current target and rerun every invalidated required lane; build-phase test results and earlier clean reviews cannot be reused when subsequent changes may have invalidated them.

## Completion and handoff

Completion requires the build Goal to satisfy its gate, the convergence Goal to report zero supported findings within the derived mandatory matrix, every applicable lane to pass or produce no supported finding in the final round, all subagent and command results to be inspected, and the final diff to contain no unintended files, secrets, generated noise, debug residue, or unexplained scope change.

Report the two phase Goals, automatic decisions, repairs, review rounds, tests and user-flow checks run, final target, evidence-backed exclusions, any blocked lane, and local versus remote delivery state. Never claim universal absence of bugs. If any required lane is blocked or incomplete, report the pipeline as incomplete even when implementation itself is finished.
