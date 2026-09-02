---
name: cyh-flow
description: Handle software-delivery work through cyh-flow with strict authorization boundaries. Use only when the user explicitly invokes $cyh-flow in Codex or /cyh-flow in Claude Code.
---

# cyh-flow

Apply one consistent development workflow across repositories without hard-coding any product, organization, branch, or technology stack.

## Invocation and mode

Codex is the priority host and invokes this Skill as `$cyh-flow`. Claude Code invokes the personal Skill as `/cyh-flow`; a marketplace/plugin install uses the canonical namespaced form `/cyh-flow:cyh-flow`. Do not promise a bare alias for the plugin form. These are host UI invocations, not shell commands. Use the matching prefix in the forms below:

Treat the active user request as the explicit invocation input. In Claude Code, appended invocation arguments are: `$ARGUMENTS`. If the current host does not expand that placeholder, use the user's request directly.

The supported explicit forms are:

```text
<cyh-flow> plan <requirement or problem>
<cyh-flow> build <plan, issue, task, or requested change>
<cyh-flow> build auto <implementation-ready plan, issue, or requirement>
<cyh-flow> auto <implementation-ready plan, issue, or requirement>
<cyh-flow> review <working tree, branch, commit, or pull request>
<cyh-flow> review deep <working tree, branch, commit, or pull request>
<cyh-flow> review auto <GitHub pull request>
<cyh-flow> fix <known bug, failing behavior, or review finding>
<cyh-flow> converge <objective and user-selected evidence lanes>
<cyh-flow> task-add <bugs, small changes, or follow-up work>
<cyh-flow> task-run [task ID or all eligible tasks]
```

Native host commands are controls, not aliases owned by this Skill. Codex `/plan` or `/review` may be used alongside the corresponding workflow. Claude Code plan permission mode is useful for read-only investigation, but `cyh-flow plan` must exit or switch from that permission mode before its sole authorized mutation: creating or updating the canonical requirement document. Claude Code's native `/review` is not an alias for `cyh-flow review`. Never claim that cyh-flow installed those controls or a standalone `/build`, `/auto`, `/fix`, `/converge`, `/task-add`, or `/task-run` command.

## Host capability mapping

Preserve the same workflow contract on both hosts while using their real capabilities:

- A `Goal` below means one outcome with an explicit completion gate. In Codex, use the native Goal API when available. In Claude Code, a user-activated `/goal` may provide the persistent across-turn loop, but it is a session-scoped prompt-based Stop hook, not the Codex create/get/update Goal API; use Claude Code Task tools for live phases and dependencies when available. When a mode defines a repository-local ledger, it is that mode's durable cross-host resume authority. `review auto` intentionally writes no repository ledger and reconstructs a lost event cursor from the live PR plus its own comment markers. If no native goal loop is active, continue within the current run and preserve whatever resume cursor that mode defines rather than claiming persistence that the host does not provide.
- A `subagent` means an isolated worker created by the host: Codex agent tools or Claude Code `Agent`. Use the maximum useful conflict-free concurrency that the selected mode actually calls for. Ordinary `review` and `review auto` use exactly one isolated reviewer; `review deep` uses four isolated specialists plus a fresh master. If concurrent workers are unavailable for deep review, run its independent lanes sequentially in fresh isolated contexts without dropping or blending a required lane.
- Addressable worker mailboxes and follow-up turns are capability-gated, not a cross-host assumption. Codex exposes them directly. Claude Code may expose `SendMessage` and shared team coordination only when the user has already enabled experimental agent teams; use them when available, but never enable that experiment as a Skill side effect. A deep review without addressable follow-up delivery finishes all four specialist lanes first, validates their compact artifact manifest, and then starts a fresh master with the target locator plus that manifest; it does not overlap the master's independent target inspection.
- Claude Code Task tools and experimental agent teams are optional orchestration facilities, not authorization. Standard `Agent` subagents are sufficient for independent lanes; never change settings, enable experimental teams, or replace an active `/goal` unless the user explicitly authorizes that host action.
- Host-specific tool names are examples of capabilities, not universal identifiers. Use the official or user-required equivalent available in the active host, preserve all side-effect boundaries, and report a required unavailable capability as blocked.

Use an explicit `plan`, `build`, `auto`, `review`, `fix`, `converge`, `task-add`, or `task-run` argument when present. Otherwise infer the mode conservatively:

- Requests to investigate, understand, map, propose, or plan are `plan`; application code and external state stay read-only, while one canonical requirement plan that fulfills both specification and implementation-planning responsibilities is created or updated.
- Requests to implement a requirement, plan, feature, or product change are `build` and authorize scoped local file edits only. Both ordinary `build` and explicit `build auto` maximize safe multi-agent implementation and validation over the requested scope: ordinary build stops at the first material unexpected problem or decision point, while auto creates one Goal, makes evidence-grounded in-scope decisions using the coordinator's best judgment, records every problem and automatic decision in one repository-local ledger for later human review, and keeps executing without review gates.
- Requests explicitly invoked as top-level `auto` are an unattended full pipeline: run the implementation as `build auto` to its completion gate, then run `converge` against the resulting target with every applicable review and test lane required, repairing and rerunning invalidated evidence until zero supported findings remain. This is the only mode that sequences build and convergence without another user turn.
- Requests to review, re-review, audit a diff, or inspect a PR are ordinary `review` and use exactly one fresh read-only reviewer applying the five-axis code-quality method in [references/review.md](references/review.md): correctness, readability and simplicity, architecture, security, and performance. Treat only the exact first argument `deep` after `review` as deep review; it uses the existing four independent specialists plus fresh master in [references/review-deep.md](references/review-deep.md). Treat only the exact first argument `auto` as unattended GitHub PR review; it repeats the ordinary single-reviewer cycle through [references/review-auto.md](references/review-auto.md), not the deep topology. Every review remains read-only, uses authenticated `gh` plus one deterministic raw preparation pass for GitHub PRs, runs only candidate-specific focused non-mutating checks, and never freezes or locks the target. A completed direct-URL review of somebody else's PR retains the bounded automatic ordinary-comment exception defined by the selected review reference. Review never approves, requests changes, resolves threads, or merges.
- Requests to repair a known bug, failure, or review finding once are `fix` and authorize scoped local repair plus proportionate validation.
- Requests that explicitly require a Goal, repeated inspection and repair, simulator or web acceptance loops, or continuing until supported findings reach zero are `converge` and authorize the scoped local convergence loop plus read-only subagent analysis. The user decides whether the required evidence is code review, browser testing, simulator or device testing, automated checks, runtime evidence, security or performance validation, or another named procedure; do not make review or browser testing mandatory merely because the mode is `converge`.
- Requests to analyze and store one or many bugs, small changes, chores, or follow-ups without implementing them are `task-add`; automatically preserve screenshots and image attachments supplied in the active intake batch unless the user explicitly opts out, and change only the repository-local dated task-pool Markdown and its evidence attachments.
- Requests to process stored work are `task-run`; every Agent independently claims one `pending` task by atomically changing its document status to `doing` with the Agent identity and claim time before any investigation or edit.

If the request mixes modes, preserve their boundaries and sequence them only as authorized. A plan authorizes only its canonical requirement decision document, not implementation. Ordinary, deep, and auto review do not authorize repair; `review auto` adds only the PR-comment delivery and monitoring defined by its reference. Build is execution-only and never invokes review as an implementation gate; ordinary build stops on the first material problem or decision point, while `build auto` autonomously decides and persists through in-scope intermediate problems, recording those decisions for later human review without seeking finding-zero. Top-level `auto` is the sole intentional build-to-converge composition and preserves a separate completion gate and Goal for each phase. `fix` is one bounded repair, while `converge` may repeat inspection, local repair, and validation until its Goal gate is satisfied. `task-add` archives work but does not implement it; `task-run` authorizes scoped local work only after a successful document-backed claim. None of `build`, top-level `auto`, `fix`, `converge`, or `task-run` authorizes commit, push, PR creation, deployment, production writes, or messages to other people; those actions require explicit user intent.

Read exactly one primary mode reference before acting. Load another reference only when the selected primary mode explicitly requires it, and follow that mode's stated phase or evidence-lane order; do not preload unrelated modes:

- For `plan`, read [references/plan.md](references/plan.md).
- For `build`, read [references/build.md](references/build.md).
- For top-level `auto`, read [references/auto.md](references/auto.md); it will load the build, converge, and deep-review references in phase order.
- For ordinary `review` and `review auto`, read [references/review.md](references/review.md); auto will then load its supplement.
- For `review deep`, read [references/review-deep.md](references/review-deep.md).
- For `fix`, read [references/fix.md](references/fix.md).
- For `converge`, read [references/converge.md](references/converge.md).
- For `task-add`, read [references/task-add.md](references/task-add.md).
- For `task-run`, read [references/task-run.md](references/task-run.md).

## Establish project context

Before mode-specific work:

1. Resolve the real repository or repositories in scope, including parent repositories, submodules, and worktrees. Do not assume the current directory is the target.
2. Read applicable host and project instructions, including `AGENTS.md`, `CLAUDE.md`, and repository documentation. Project instructions override this skill where they are more specific and do not violate user or system instructions.
3. Inspect the working tree before any mutation and preserve unrelated tracked and untracked changes.
4. Prefer an applicable Skill, then MCP or built-in tools. When comparable capabilities exist, prefer official or vendor-maintained Skills, Plugins, and MCP integrations without removing personal capabilities as a side effect.
5. If `.codegraph/` exists and CodeGraph is available, prefer it for architecture, dependency, and call-path discovery. Do not modify or rebuild its index unless needed and authorized.
6. For GitHub, use the authenticated `gh` CLI by default. Re-read live PR heads, reviews, checks, and refs before relying on them.
7. For browser automation, use the installed `cyh-browser-skill`: Codex exposes it as `browser-skill:cyh-browser-skill`, while Claude Code's plugin form is `/browser-skill:cyh-browser-skill`. Ordinary public web research should use the host's normal static search path. If the required browser Skill is unavailable, report the browser lane as blocked rather than substituting another automation system.

If the target, authorization, or destructive scope remains materially ambiguous after safe inspection, stop and ask one concise question.

## Subagent-first decomposition

Every mode is subagent-first. Before substantial work, map dependencies and split every independent bounded unit that can safely run in parallel, then use the maximum useful subagent concurrency available and dispatch the next ready unit as soon as capacity opens. Do not keep independent work on the coordinator merely because it could perform the work itself. When a stage is genuinely atomic or has no useful independent split, execute it directly rather than creating artificial agents whose coordination cost exceeds the work.

Give every subagent an exact objective, minimum necessary context, scope and ownership, read/write and side-effect boundary, dependencies, acceptance evidence, and required return shape. Inspect and integrate every result; a completed agent or successful command is not proof that its task is accepted. Subagents inherit the selected mode's authorization and may never turn planning, review, intake, or validation into unauthorized implementation or external mutation.

Parallelism must remain conflict-free. Do not give multiple writers overlapping files, generated artifacts, migrations, lockfiles, schemas, or Git state, and do not concurrently mutate the same dependency cache, simulator, device, browser target, database, build output, or external environment. The mode reference defines its writer topology: `plan` and `task-add` use read-only analysis workers plus one document writer; `build` uses disjoint implementation and validation workers; top-level `auto` adopts the build topology first and the converge topology only after the build Goal completes; ordinary `review` and `review auto` use one reviewer, while `review deep` uses four specialists plus a fresh master and overlaps the master's independent target inspection when capacity permits; `fix` and `converge` use one repair writer plus parallel read-only investigation or evidence workers; `task-run` uses independently claiming workers whose tasks and resources do not conflict.

## Shared boundaries

- Never merge a pull request.
- Do not reset, clean, discard, overwrite, or force-push work unless the user explicitly authorizes the exact target after the loss scope is shown.
- Prefer the optimal coherent solution for the real requirement and repository constraints. Reuse established project patterns before introducing new abstractions, but treat fewer lines or files only as a tiebreaker between equally correct, clear, maintainable, and verifiable options.
- Treat live refs, PR state, CI, deployments, configuration, and production data as time-sensitive; verify them in the current run.
- Separate source inspection, local validation, CI, deployment/runtime evidence, UI or device evidence, and business acceptance. Evidence in one lane does not prove another.
- Report pre-existing failures separately from failures introduced by the requested change.
- Respond in Chinese unless the user asks for another language; prefer fluent, compact prose over excessive headings and bullet lists.
- Lead the final response with the outcome, then the important evidence, incomplete checks, and any next action requiring the user.
