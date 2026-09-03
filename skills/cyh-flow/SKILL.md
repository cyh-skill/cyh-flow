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
<cyh-flow> re-review <GitHub pull request>
<cyh-flow> fix <known bug, failing behavior, or review finding>
<cyh-flow> converge <objective and user-selected evidence lanes>
<cyh-flow> task-add <bugs, small changes, or follow-up work>
<cyh-flow> task-run [task ID or all eligible tasks]
```

Native host commands are controls, not aliases owned by this Skill. Codex `/plan` or `/review` may be used alongside the corresponding workflow. Claude Code plan permission mode is useful for read-only investigation, but `cyh-flow plan` must exit or switch from that permission mode before its sole authorized mutation: creating or updating the canonical requirement document. Claude Code's native `/review` is not an alias for `cyh-flow review`. Never claim that cyh-flow installed those controls or a standalone `/build`, `/auto`, `/fix`, `/converge`, `/task-add`, or `/task-run` command.

## Host capability mapping

Preserve the same workflow contract on both hosts while using their real capabilities:

- A `Goal` below means one outcome with an explicit completion gate. In Codex, use the native Goal API when available. In Claude Code, a user-activated `/goal` may provide the persistent across-turn loop, but it is a session-scoped prompt-based Stop hook, not the Codex create/get/update Goal API; use Claude Code Task tools for live phases and dependencies when available. When a mode defines a repository-local ledger, it is that mode's durable cross-host resume authority. `review auto` intentionally writes no repository ledger and reconstructs a lost event cursor from the live PR plus its own comment markers. If no native goal loop is active, continue within the current run and preserve whatever resume cursor that mode defines rather than claiming persistence that the host does not provide.
- A `subagent` means an isolated worker created by the host: Codex agent tools or Claude Code `Agent`. Use the maximum useful conflict-free concurrency that the selected mode actually calls for. Ordinary `review`, `review auto`, and `re-review` use exactly one isolated reviewer; `review deep` uses four isolated specialists plus a fresh master. If concurrent workers are unavailable for deep review, run its independent lanes sequentially in fresh isolated contexts without dropping or blending a required lane.
- Addressable worker mailboxes and follow-up turns are capability-gated, not a cross-host assumption. Codex exposes them directly. Claude Code may expose `SendMessage` and shared team coordination only when the user has already enabled experimental agent teams; use them when available, but never enable that experiment as a Skill side effect. A deep review without addressable follow-up delivery finishes all four specialist lanes first, validates their compact artifact manifest, and then starts a fresh master with the target locator plus that manifest; it does not overlap the master's independent target inspection.
- Claude Code Task tools and experimental agent teams are optional orchestration facilities, not authorization. Standard `Agent` subagents are sufficient for independent lanes; never change settings, enable experimental teams, or replace an active `/goal` unless the user explicitly authorizes that host action.
- Host-specific tool names are examples of capabilities, not universal identifiers. Use the official or user-required equivalent available in the active host, preserve all side-effect boundaries, and report a required unavailable capability as blocked.

Use an explicit `plan`, `build`, `auto`, `review`, `re-review`, `fix`, `converge`, `task-add`, or `task-run` argument when present. Otherwise infer the mode conservatively:

- `plan` serves requests to investigate, understand, map, propose, or plan. Its write surface is one canonical requirement plan; application code and external state remain unchanged.
- `build` serves implementation requests. Its write surface is scoped local files, and its workers are implementers or validators. Ordinary build pauses at the first material unexpected problem or decision point; explicit `build auto` creates one Goal, records evidence-grounded in-scope decisions in a repository-local ledger, and continues to its build completion gate.
- Top-level `auto` is the explicit unattended pipeline. It runs `build auto` to completion and then runs `converge` on the resulting target. Its derived validation matrix includes applicable code review and automated checks; browser, simulator, device, deployment, remote-environment, and business-acceptance lanes enter the matrix when the user or an authoritative acceptance contract explicitly selects them.
- `review` serves diff, branch, commit, or PR inspection with one fresh read-only five-axis reviewer through [references/review.md](references/review.md). Exact `review deep` uses four specialists plus a fresh master through [references/review-deep.md](references/review-deep.md); exact `review auto` repeats the ordinary reviewer through [references/review-auto.md](references/review-auto.md). Top-level `re-review` reconciles existing actionable review issues through [references/re-review.md](references/re-review.md). Review write surfaces are limited to approved temporary artifacts and the bounded comment delivery explicitly defined by the selected review mode.
- `fix` serves one bounded repair of a known bug, failure, or review finding and authorizes scoped local repair plus its selected validation contract.
- `converge` serves an explicit Goal with repeated inspection, repair, and user-selected evidence lanes until zero supported findings remain. The evidence contract names the required review, automated, browser, simulator/device, runtime, security, performance, or custom procedures.
- `task-add` turns bugs, small changes, chores, or follow-ups into repository-local dated task records and preserved intake evidence. Its write surface is the task-pool Markdown and evidence attachments.
- `task-run` processes stored work after each Agent atomically claims one `pending` task and receives ownership of that task's scoped local implementation.

For mixed requests, compose only the named or clearly authorized modes and preserve each mode's write surface and completion gate. Top-level `auto` is the predefined build-to-converge composition; other transitions require the user's request. Commit, push, PR creation or mutation, deployment, production writes, and messages to other people remain separate delivery actions requiring explicit user intent.

## Default validation contract

Implementation and repair modes default to source inspection plus the smallest relevant static or automated checks needed for the changed behavior. Browser, simulator, real-device, deployment, remote-environment, and business acceptance are independent evidence lanes: execute them when the user requests them or an authoritative acceptance contract explicitly selects them. A lane discovered as useful but not selected is reported as a coverage limitation or recommendation, not silently added as a completion requirement. Review modes follow their own focused non-mutating evidence contract.

Read the selected primary mode reference before acting. Load additional references only through that mode's stated phase or evidence-lane routing:

- For `plan`, read [references/plan.md](references/plan.md).
- For `build`, read [references/build.md](references/build.md).
- For top-level `auto`, read [references/auto.md](references/auto.md); it will load the build, converge, and deep-review references in phase order.
- For ordinary `review` and `review auto`, read [references/review.md](references/review.md); auto will then load its supplement.
- For `review deep`, read [references/review-deep.md](references/review-deep.md).
- For `re-review`, read [references/re-review.md](references/re-review.md).
- For `fix`, read [references/fix.md](references/fix.md).
- For `converge`, read [references/converge.md](references/converge.md).
- For `task-add`, read [references/task-add.md](references/task-add.md).
- For `task-run`, read [references/task-run.md](references/task-run.md).

## Establish project context

Before mode-specific work:

1. Resolve the real repository or repositories in scope, including parent repositories, submodules, and worktrees; treat the current directory as a starting point rather than proof of scope.
2. Read applicable host and project instructions, including `AGENTS.md`, `CLAUDE.md`, and repository documentation. Project instructions override this skill where they are more specific and do not violate user or system instructions.
3. Inspect the working tree before any mutation and preserve unrelated tracked and untracked changes.
4. Prefer an applicable Skill, then MCP or built-in tools. When comparable capabilities exist, prefer official or vendor-maintained Skills, Plugins, and MCP integrations without removing personal capabilities as a side effect.
5. If `.codegraph/` exists and CodeGraph is available, prefer it for architecture, dependency, and call-path discovery. Its existing index is the default read surface; index mutation or rebuild requires task need and authorization.
6. For GitHub, use the authenticated `gh` CLI by default. Re-read live PR heads, reviews, checks, and refs before relying on them.
7. A selected browser evidence lane uses the installed `cyh-browser-skill`: Codex exposes it as `browser-skill:cyh-browser-skill`, while Claude Code's plugin form is `/browser-skill:cyh-browser-skill`. Ordinary public web research uses the host's normal static search path. If a required browser lane lacks that Skill, report the lane as blocked.

If the target, authorization, or destructive scope remains materially ambiguous after safe inspection, stop and ask one concise question.

## Subagent-first decomposition

Every mode is subagent-first. Before substantial work, map dependencies and split independent bounded units that can safely run in parallel, then use the maximum useful subagent concurrency and dispatch the next ready unit as capacity opens. Atomic stages and work whose coordination cost exceeds its benefit stay with the coordinator.

Give every subagent an exact objective, minimum necessary context, scope and ownership, read/write and side-effect boundary, dependencies, acceptance evidence, and required return shape. Inspect and integrate every result; a completed agent or successful command is not proof that its task is accepted. Subagents inherit the selected mode's authorization and may never turn planning, review, intake, or validation into unauthorized implementation or external mutation.

Parallelism uses disjoint ownership. Each file, generated artifact, migration, lockfile, schema, Git surface, dependency cache, simulator, device, browser target, database, build output, or external environment has at most one mutating owner at a time. The mode reference defines its writer topology: `plan` and `task-add` use read-only analysis workers plus one document writer; `build` uses disjoint implementation and validation workers; top-level `auto` adopts the build topology first and the converge topology after the build Goal completes; ordinary `review`, `review auto`, and `re-review` use one reviewer; `review deep` uses four specialists plus a fresh master; `fix` and `converge` use one repair writer plus parallel read-only evidence workers; `task-run` uses independently claiming workers with non-conflicting tasks and resources.

## Shared boundaries

- Never merge a pull request.
- Do not reset, clean, discard, overwrite, or force-push work unless the user explicitly authorizes the exact target after the loss scope is shown.
- Prefer the optimal coherent solution for the real requirement and repository constraints. Reuse established project patterns before introducing new abstractions, but treat fewer lines or files only as a tiebreaker between equally correct, clear, maintainable, and verifiable options.
- Treat live refs, PR state, CI, deployments, configuration, and production data as time-sensitive; verify them in the current run.
- Separate source inspection, local validation, CI, deployment/runtime evidence, UI or device evidence, and business acceptance. Evidence in one lane does not prove another.
- Report pre-existing failures separately from failures introduced by the requested change.
- Respond in Chinese unless the user asks for another language; prefer fluent, compact prose over excessive headings and bullet lists.
- Lead the final response with the outcome, then the important evidence, incomplete checks, and any next action requiring the user.
