# Build mode

Use this mode to implement a concrete requirement, plan, feature, or product change. Known bugs, failing behavior, and review findings belong to `fix`; persistent finding-zero objectives belong to `converge`. Local file edits within the stated scope are authorized; external mutations are not implied.

Build is an execution workflow, not a review workflow. Implement, test, build, and exercise the requested behavior, but do not invoke `review`, launch review personas, run a master recheck, or add a finding-zero gate. Subagents in this mode are implementers or validators, not reviewers.

## Modes

- `<cyh-flow> build <source>` executes the concrete implementation scope with the maximum useful subagent concurrency, but stops at the first material unexpected problem instead of diagnosing, repairing, or continuing past it autonomously. It does not create a Goal or issue ledger.
- `<cyh-flow> build auto <source>` executes the same kind of implementation scope and parallel task graph, but creates a Goal using the host mapping in the canonical Skill, uses the coordinator's best evidence-grounded judgment to make in-scope decisions, records every intermediate problem and automatic decision in a local ledger for later human review, and keeps resolving problems or running unaffected dependency-ready work without pausing between safe steps. The `auto` invocation itself delegates these in-scope decisions and continuation; it does not authorize external mutations.

Treat only the explicit first argument `auto` after `build` as auto mode. Do not infer auto mode merely because the request is large, asks for speed, or contains several tasks. Top-level `<cyh-flow> auto` is a separate full-pipeline mode whose reference explicitly enters this build-auto phase before convergence; it is not an inferred alias for `<cyh-flow> build auto`.

## Before editing

1. Read the complete source of truth named by the user and verify it is concrete enough to implement. Resolve missing facts from the repository when possible.
2. Inspect branch, HEAD, working-tree changes, submodules, and relevant generated artifacts. Preserve unrelated user work.
3. Confirm the intended repositories and deployment surfaces. If multiple repositories are involved, keep their changes and validation evidence distinct.
4. Reuse existing project patterns, clients, components, types, migrations, and test helpers. Avoid speculative abstractions and unrelated cleanup.

Do not use destructive Git operations as an implementation shortcut. Do not modify production data or configuration unless explicitly authorized.

Both modes require a concrete objective and acceptance source. In default mode, an ambiguity or implementation-readiness gap is the first problem and stops execution. In auto mode, the user delegates in-scope decision-making to the coordinator: choose among viable behaviors, defaults, implementation trade-offs, task ordering, and safe repairs using the stated objective, source of truth, repository evidence, established patterns, compatibility, risk, and validation cost. Record the decision and rationale, clearly label it as AI-made rather than user-approved, then continue. Do not silently switch to `plan`, invent requirements outside the Goal, enlarge scope, or treat auto as permission for external, destructive, irreversible, or otherwise separately authorized action.

## Decompose and dispatch

In both default and auto mode, map tasks and dependencies before implementation, then split every independent bounded unit that can safely run in parallel. Both modes must use the maximum useful subagent concurrency available and dispatch the next dependency-ready unit as soon as capacity opens. Keep the coordinator focused on dependency management and integration, plus Goal state and the issue ledger in auto mode, while workers perform implementation or validation.

Give each worker an exact objective, acceptance criteria, repository and file ownership, write boundary, relevant dependencies, validation responsibility, and required return format. A worker must return changed paths, checks run, outcome, every problem it encountered, and every decision or decision point, including problems it resolved and bounded choices it made. The coordinator owns cross-task decisions and the human-review record. Workers must not create or update the Goal, write the shared ledger, commit, push, create or edit a PR, deploy, message people, or spawn review agents.

Maximize parallelism only across non-conflicting work:

- Assign disjoint files or modules to concurrent writers. Give a shared file, generated artifact, migration chain, lockfile, schema, or other ordering-sensitive surface one writer at a time.
- Use read-only investigation or validation tasks when implementation cannot be divided safely. Do not manufacture tiny agents whose coordination cost exceeds the work.
- Do not run commands concurrently when they mutate the same dependencies, cache, simulator, database, browser target, build output, or external environment.
- When a worker exposes a material unexpected problem or decision point, default mode stops dispatching new work and reports it; allow already-running safe tasks to finish only to preserve coherent state and collect their results. In auto mode, the coordinator records the problem, makes and records an evidence-grounded in-scope decision, adds any bounded follow-up task with dependencies, and continues resolving it or dispatching unaffected ready work. The coordinator inspects and integrates every worker result; successful process exit alone is not acceptance evidence.

This is execution parallelism only. Do not assign a worker to code review, adversarial review, style critique, optimality review, or master adjudication as part of build.

## Auto Goal and local decision ledger

At the start of auto mode, establish one Goal whose objective names the source of truth, repositories, intended outcome, and executable completion gate, using the active host's capability mapping. Do not set a token budget unless the user explicitly supplied one. Resume an existing unfinished Goal only when it is the same build objective; if an unrelated unfinished Goal prevents creation, stop and ask the user rather than replacing it. On Claude Code, do not claim that the Skill programmatically activated `/goal`: use it only when the user has activated it, mirror live work in Task tools when available, and always persist the resume cursor in the ledger.

Create or resume one repository-local Markdown ledger before dispatching implementation. It is both the issue history and the automatic-decision review queue. Follow an existing project convention when one exists; otherwise use `.cyh-flow/build/<stable-goal-slug>.md` in the coordinating repository. Reuse the same stable path for later auto invocations of the same Goal. Keep the ledger local and unstaged unless the user explicitly asks to deliver it; do not add ignore rules as a side effect. For work spanning repositories, keep one coordinating ledger and name the repository in every task, problem, and decision record.

The coordinator is the sole writer for this ledger. Record:

- the Goal objective, source of truth, scope, non-goals, starting revisions, repositories, and completion gate;
- the dependency graph, task owner, state, changed paths, validation evidence, and resume cursor;
- every intermediate problem before attempting or accepting its resolution, including ambiguity, baseline failure, implementation error, test or build failure, agent failure or conflict, unavailable evidence, security or data risk, missing permission, and skipped work;
- for each problem, a stable ID, discovery time, task and agent, concrete evidence and impact, current status, resolution or required decision, and affected validation that must be rerun.
- every automatic decision under a stable decision ID linked to its problem or task, including the question or trigger, options considered, selected option, evidence and rationale, affected scope and files, compatibility and risk, reversibility, validation performed, and human-review status: `pending`, `accepted`, `rejected`, or `superseded`.

Keep a prominent summary of decisions whose human-review status is `pending` so a person can audit them without reconstructing the run. Do not mark an AI-made decision `accepted` on the human's behalf. Append later human outcomes and any resulting follow-up instead of rewriting history.

Do not store secrets, credentials, personal data, or unbounded raw logs. Record concise evidence and a safe pointer instead. Resolved problems and superseded decisions remain in the ledger; never delete them to make the run appear clean. On every continuation or context recovery, read the Goal and ledger first, verify the current repository state, and resume from the recorded dependency-ready tasks rather than repeating completed work.

## Implement and verify

1. Implement the optimal coherent solution for the agreed behavior and repository constraints. Compare viable reuse, standard-library, native-platform, installed-dependency, direct-code, and new-abstraction options; prefer less code only when correctness, clarity, maintainability, testability, performance, and compatibility remain equal.
2. Add or update tests when the project normally tests that behavior or the regression risk warrants them.
3. Run focused checks for each task, then broader integration checks after affected dependency waves in proportion to risk and repository norms. Inspect enough evidence to identify and distinguish an unexpected failure from the baseline. Default mode stops at that problem without starting autonomous diagnosis or repair; auto mode writes it to the ledger first, then continues diagnosis, repair, or unaffected work.
4. Exercise the real user flow when UI, device, browser, deployment, or external integration behavior is part of acceptance and the required access is available.
5. Check the final changed-file set and acceptance coverage for unintended files, generated noise, secrets, scope creep, and incomplete tasks. This is execution hygiene, not code review; do not switch to or simulate review mode.

A successful typecheck, build, HTTP response, CI job, deployment, or screenshot proves only its own evidence lane. Do not claim full completion when business behavior or another platform remains unverified.

A material unexpected problem includes an ambiguity that changes behavior, an unexpected baseline state, implementation or integration error, failing test or build, worker failure or write conflict, missing required evidence, security or data risk, unavailable environment, or missing permission. In default mode, stop scheduling and modifying at the first such problem, preserve the current state, and report it to the user. Do not reinterpret routine planned steps or a deliberately failing test used by the repository's normal workflow as problems unless they become unexpected or block progress.

Auto mode does not stop merely because an intermediate problem or in-scope decision occurs and does not wait for review. Record the problem, make and record the best evidence-grounded decision, preserve its rationale, attempt safe in-scope resolution, and keep unaffected tasks moving until the objective is complete. Stop only when the choice would change the Goal's objective or authorized scope, requires new authority or external mutation, is destructive or not safely reversible, depends on an unavailable required environment with no other ready work, or requires resolution of an unrelated active Goal; record that blocker first and preserve the Goal as incomplete according to the host Goal rules.

## GitHub and delivery

Commit, push, create or edit a PR, post a message, or deploy only when the user explicitly asks for that action.

When commit or push is authorized:

- Re-read status, diff, branch, remote, and relevant live refs immediately before acting.
- Include only scoped files; exclude `.codegraph/`, caches, credentials, logs, build output, screenshots, and unrelated user artifacts unless they are intentional deliverables.
- Run the checks that are safe and proportionate. If the user asks to ship before a long check finishes, push the validated scoped change and state exactly what remains unverified.
- Use a normal push unless history rewriting was explicitly authorized and its lease target was verified.
- After pushing, verify the remote branch SHA and report the exact URL when one exists.

Never merge a PR.

## Completion

For default mode, if no material problem occurs, complete the full requested implementation scope and report the changes, validation, and delivery state. If a problem occurs, report completed and in-flight work, the first problem and its evidence, current file state, checks already run, and all known unfinished work, then stop without autonomously repairing or continuing past it.

For auto mode, mark the Goal complete only when all dependency tasks are finished, worker results were inspected and integrated, required implementation and validation evidence passes, and the ledger has no unresolved in-scope problem that defeats the objective. Automatic decisions may remain `pending` for later human review unless the user explicitly made human acceptance part of the Goal gate; pending means “executed but not human-approved,” never implicit acceptance. Report the Goal result, ledger path, tasks and agents used, changes, validation, all unresolved or non-blocking problems, every automatic decision and its human-review status, delivery state, and remaining business acceptance.

Do not quietly continue into unrelated tasks, and never claim that build included code review.
