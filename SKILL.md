---
name: flow
description: Route software-development work through CYH's cross-project plan, build, review, repair, convergence, or persistent task-pool workflows with explicit authorization boundaries. Use when the user invokes $flow to plan or implement a scoped change, review read-only, repair or repeatedly recheck a problem, add bugs or small changes to a dated task pool with automatic screenshot preservation, or independently claim and process stored tasks. Do not use for general questions unrelated to software delivery.
---

# CYH Flow

Apply one consistent development workflow across repositories without hard-coding any product, organization, branch, or technology stack.

## Invocation and mode

The supported explicit forms are:

```text
$flow plan <requirement or problem>
$flow build <plan, issue, task, or requested change>
$flow build auto <implementation-ready plan, issue, or requirement>
$flow review <working tree, branch, commit, or pull request>
$flow fix <known bug, failing behavior, or review finding>
$flow converge <objective and user-selected evidence lanes>
$flow task-add <bugs, small changes, or follow-up work>
$flow task-run [task ID or all eligible tasks]
```

`$flow` invokes this skill. Codex `/` commands are host controls, not custom aliases owned by this skill. A native `/plan` or `/review` may be used alongside the corresponding mode, and the native Goal mechanism hosts `build auto` and `converge` when available; never claim that `/build`, `/fix`, `/converge`, `/task-add`, `/task-run`, or `/flow` was installed.

Use an explicit `plan`, `build`, `review`, `fix`, `converge`, `task-add`, or `task-run` argument when present. Otherwise infer the mode conservatively:

- Requests to investigate, understand, map, propose, or plan are `plan`; application code and external state stay read-only, while one canonical requirement plan that fulfills both specification and implementation-planning responsibilities is created or updated.
- Requests to implement a requirement, plan, feature, or product change are `build` and authorize scoped local file edits only. Both ordinary `build` and explicit `build auto` maximize safe multi-agent implementation and validation over the requested scope: ordinary build stops at the first material unexpected problem or decision point, while auto creates one Goal, makes evidence-grounded in-scope decisions using the coordinator's best judgment, records every problem and automatic decision in one repository-local ledger for later human review, and keeps executing without review gates.
- Requests to review, re-review, audit a diff, or inspect a PR are `review` and use four independent read-only specialist lanes followed by a fresh master recheck.
- Requests to repair a known bug, failure, or review finding once are `fix` and authorize scoped local repair plus proportionate validation.
- Requests that explicitly require a Goal, repeated inspection and repair, simulator or web acceptance loops, or continuing until supported findings reach zero are `converge` and authorize the scoped local convergence loop plus read-only subagent analysis. The user decides whether the required evidence is code review, browser testing, simulator or device testing, automated checks, runtime evidence, security or performance validation, or another named procedure; do not make review or browser testing mandatory merely because the mode is `converge`.
- Requests to analyze and store one or many bugs, small changes, chores, or follow-ups without implementing them are `task-add`; automatically preserve screenshots and image attachments supplied in the active intake batch unless the user explicitly opts out, and change only the repository-local dated task-pool Markdown and its evidence attachments.
- Requests to process stored work are `task-run`; every Agent independently claims one `pending` task by atomically changing its document status to `doing` with the Agent identity and claim time before any investigation or edit.

If the request mixes modes, preserve their boundaries and sequence them only as authorized. A plan authorizes only its canonical requirement decision document, not implementation. A review does not authorize repair. Build is execution-only and never invokes review as an implementation gate; ordinary build stops on the first material problem or decision point, while `build auto` autonomously decides and persists through in-scope intermediate problems, recording those decisions for later human review without seeking finding-zero. `fix` is one bounded repair, while `converge` may repeat inspection, local repair, and validation until its Goal gate is satisfied. `task-add` archives work but does not implement it; `task-run` authorizes scoped local work only after a successful document-backed claim. None of `build`, `fix`, `converge`, or `task-run` authorizes commit, push, PR creation, deployment, production writes, or messages to other people; those actions require explicit user intent.

Read exactly one primary mode reference before acting. Load another mode reference only when the selected primary mode explicitly names it as a user-required evidence lane; do not preload unrelated modes:

- For `plan`, read [references/plan.md](references/plan.md).
- For `build`, read [references/build.md](references/build.md).
- For `review`, read [references/review.md](references/review.md).
- For `fix`, read [references/fix.md](references/fix.md).
- For `converge`, read [references/converge.md](references/converge.md).
- For `task-add`, read [references/task-add.md](references/task-add.md).
- For `task-run`, read [references/task-run.md](references/task-run.md).

## Establish project context

Before mode-specific work:

1. Resolve the real repository or repositories in scope, including parent repositories, submodules, and worktrees. Do not assume the current directory is the target.
2. Read applicable `AGENTS.md` files and repository documentation. Project instructions override this skill where they are more specific and do not violate user or system instructions.
3. Inspect the working tree before any mutation and preserve unrelated tracked and untracked changes.
4. Prefer an applicable Skill, then MCP or built-in tools. When comparable capabilities exist, prefer official or vendor-maintained Skills, Plugins, and MCP integrations without removing personal capabilities as a side effect.
5. If `.codegraph/` exists and CodeGraph is available, prefer it for architecture, dependency, and call-path discovery. Do not modify or rebuild its index unless needed and authorized.
6. For GitHub, use the authenticated `gh` CLI by default. Re-read live PR heads, reviews, checks, and refs before relying on them.
7. For browser automation, use `browser-skill:cyh-browser-skill`. Ordinary public web research should use the normal web-search path.

If the target, authorization, or destructive scope remains materially ambiguous after safe inspection, stop and ask one concise question.

## Subagent-first decomposition

Every mode is subagent-first. Before substantial work, map dependencies and split every independent bounded unit that can safely run in parallel, then use the maximum useful subagent concurrency available and dispatch the next ready unit as soon as capacity opens. Do not keep independent work on the coordinator merely because it could perform the work itself. When a stage is genuinely atomic or has no useful independent split, execute it directly rather than creating artificial agents whose coordination cost exceeds the work.

Give every subagent an exact objective, minimum necessary context, scope and ownership, read/write and side-effect boundary, dependencies, acceptance evidence, and required return shape. Inspect and integrate every result; a completed agent or successful command is not proof that its task is accepted. Subagents inherit the selected mode's authorization and may never turn planning, review, intake, or validation into unauthorized implementation or external mutation.

Parallelism must remain conflict-free. Do not give multiple writers overlapping files, generated artifacts, migrations, lockfiles, schemas, or Git state, and do not concurrently mutate the same dependency cache, simulator, device, browser target, database, build output, or external environment. The mode reference defines its writer topology: `plan` and `task-add` use read-only analysis workers plus one document writer; `build` uses disjoint implementation and validation workers; `review` uses its fixed four specialists and fresh master; `fix` and `converge` use one repair writer plus parallel read-only investigation or evidence workers; `task-run` uses independently claiming workers whose tasks and resources do not conflict.

## Shared boundaries

- Never merge a pull request.
- Do not reset, clean, discard, overwrite, or force-push work unless the user explicitly authorizes the exact target after the loss scope is shown.
- Prefer the optimal coherent solution for the real requirement and repository constraints. Reuse established project patterns before introducing new abstractions, but treat fewer lines or files only as a tiebreaker between equally correct, clear, maintainable, and verifiable options.
- Treat live refs, PR state, CI, deployments, configuration, and production data as time-sensitive; verify them in the current run.
- Separate source inspection, local validation, CI, deployment/runtime evidence, UI or device evidence, and business acceptance. Evidence in one lane does not prove another.
- Report pre-existing failures separately from failures introduced by the requested change.
- Respond in Chinese unless the user asks for another language; prefer fluent, compact prose over excessive headings and bullet lists.
- Lead the final response with the outcome, then the important evidence, incomplete checks, and any next action requiring the user.
