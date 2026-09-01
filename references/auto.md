# Auto mode

Use top-level `$flow auto <source>` for an explicit unattended local delivery pipeline. It runs the requested implementation as `build auto` to completion, freezes the resulting target, then runs `converge` with every applicable review and test lane required until zero supported findings remain. It makes safe, reversible, in-scope decisions without routine confirmation, but never expands authorization to commit, push, create or change a PR, deploy, write production or external systems, message people, merge, or perform destructive operations.

This is a phase orchestrator, not a third implementation or review protocol. Read [build.md](build.md) for phase one, then read [converge.md](converge.md) and [review.md](review.md) only after phase one completes. Do not run build and convergence concurrently or blur their completion gates.

## Orchestration ledger and Goal sequence

Use one repository-local orchestration ledger as the durable source of phase state. Follow an existing project convention when one exists; otherwise use `.cyh-flow/auto/<stable-objective-slug>.md` in the coordinating repository. Keep it local and unstaged unless the user explicitly requests delivery, and do not add ignore rules as a side effect. The coordinator is its sole writer; subagents report evidence and never edit it.

Record the objective, source of truth, repositories, starting revisions, non-goals, authorization boundary, current phase, phase-specific Goal and ledger paths, frozen targets, derived evidence matrix, decisions, blockers, resume cursor, and final evidence. For cross-repository work, name the repository in every task and result. Do not store secrets, personal data, credentials, or unbounded logs.

The host permits only one active native Goal, so do not create a simultaneous parent Goal. Sequence exactly two phase Goals:

1. Create or resume the build Goal under the rules for explicit `$flow build auto`. Record it as `build` in the orchestration ledger and execute it until its own completion gate is satisfied. A blocked or incomplete build stops the pipeline; do not start convergence.
2. Freeze the complete post-build target, mark the build phase complete in the orchestration ledger, and only then complete the build Goal.
3. Create or resume a separate convergence Goal over that frozen target. Record it as `converge`, derive the mandatory evidence matrix below, and execute the converge repair-and-recheck loop until its own completion gate is satisfied.
4. Mark the orchestration ledger complete only after both Goals completed against the recorded targets and the final convergence evidence covers every applicable lane.

If an unrelated unfinished Goal prevents phase creation, do not replace it. Record the conflict and stop. On resume, read the orchestration ledger, the current Goal, and the phase ledger first; verify repository state before continuing from the recorded cursor. A pending human-review status on an in-scope build decision does not pause the pipeline unless the user explicitly made human acceptance a completion requirement; the convergence review must still inspect the code and behavior resulting from that decision.

## Mandatory review and test matrix

“All reviews and tests” means every lane applicable to the affected behavior and project contract, not every conceivable check in the software ecosystem. Availability does not determine applicability: execute every applicable lane that is safe and currently authorized, and block completion on any applicable lane that cannot run. Derive and record the matrix before starting convergence, with applicability, command or procedure, target, resource, side-effect risk, and reason for including or excluding each lane.

The matrix must include:

- full code review using [review.md](review.md): one frozen final target, four independent specialist reviews, and a fresh master recheck;
- every applicable established automated check discoverable from repository instructions, CI definitions, package scripts, build files, and affected-module conventions, including focused and broader unit, integration, end-to-end, type, lint, build, schema, migration, contract, or packaging checks as relevant;
- every platform or user-flow check applicable to the affected surface, such as browser journeys, API flows, simulator, emulator, device, accessibility, or runtime-log validation; execute it in an authorized safe test environment when available, otherwise keep that required lane blocked rather than reclassifying it as not applicable;
- existing security, performance, compatibility, recovery, or data-integrity checks when the changed surface or repository contract makes them applicable.

Use project instructions and impact analysis to decide applicability, and explain exclusions. Do not trigger remote CI through a push, mutate an external environment, run unsafe load, or touch production merely to satisfy the matrix; execute equivalent established local checks when possible. Browser automation must use `browser-skill:cyh-browser-skill`. Serialize checks that share a browser, simulator, device, database, dependency cache, build output, or other mutable resource.

An applicable lane that is unavailable or requires new permission remains required and blocks completion; do not silently downgrade it to optional. Separate pre-existing failures from regressions, but a baseline failure in a required lane still prevents a passing result unless the Goal contract supplies an evidence-grounded disposition that preserves the intended acceptance meaning.

## Unattended execution and repair

Within the stated objective and local authorization, resolve routine ambiguity, implementation trade-offs, test failures, reviewer findings, agent failures, and retryable tooling issues using repository evidence and the safest coherent choice. Record material decisions before relying on them, preserve their rationale and reversibility, and keep dependency-ready work moving. Do not ask for confirmation merely because a choice requires engineering judgment.

Stop only when continuing would change the objective or scope, require new authorization or an external mutation, be destructive or not safely reversible, depend on an unavailable required environment, conflict with another active Goal or shared resource that cannot be serialized, or require a material product decision that repository evidence cannot resolve safely. Record the exact blocker and keep the current phase and orchestration ledger incomplete.

During convergence, use one mutually exclusive repair writer and parallel read-only evidence workers. Every supported in-scope finding enters the finding ledger, is repaired or disposed of with evidence, and invalidates the affected evidence lanes. After the final repair, freeze a new target and rerun every invalidated required lane; build-phase test results and earlier clean reviews cannot be reused when subsequent changes may have invalidated them.

## Completion and handoff

Completion requires the build Goal to satisfy its gate, the convergence Goal to report zero supported findings within the derived mandatory matrix, every applicable lane to pass or produce no supported finding on the final frozen target, all subagent and command results to be inspected, and the final diff to contain no unintended files, secrets, generated noise, debug residue, or unexplained scope change.

Report the two phase Goals, automatic decisions, repairs, review rounds, tests and user-flow checks run, final target, evidence-backed exclusions, any blocked lane, and local versus remote delivery state. Never claim universal absence of bugs. If any required lane is blocked or incomplete, report the pipeline as incomplete even when implementation itself is finished.
