---
name: cyh-flow
description: Route software-development work through CYH's cross-project plan, build, four-lens parallel review, or goal-backed adversarial fix workflow with explicit authorization boundaries. Use when the user invokes $cyh-flow, asks to plan or implement a scoped repository change, asks for a read-only review, or explicitly requests a persistent review-fix-re-review loop until no supported findings remain. Do not use for general questions unrelated to software delivery.
---

# CYH Flow

Apply one consistent development workflow across repositories without hard-coding any product, organization, branch, or technology stack.

## Invocation and mode

The supported explicit forms are:

```text
$cyh-flow plan <requirement or problem>
$cyh-flow build <plan, issue, task, or requested change>
$cyh-flow review <working tree, branch, commit, or pull request>
$cyh-flow fix <bug, failing behavior, branch, pull request, or repair objective>
```

`$cyh-flow` invokes this skill. Codex `/` commands are host controls, not custom aliases owned by this skill. A native `/plan` or `/review` may be used alongside the corresponding mode, and the native Goal mechanism hosts the persistent `fix` loop when available; never claim that `/build`, `/fix`, or `/cyh-flow` was installed.

Use an explicit `plan`, `build`, `review`, or `fix` argument when present. Otherwise infer the mode conservatively:

- Requests to investigate, understand, map, propose, or plan are `plan`; application code and external state stay read-only, while the requirement's canonical Markdown decision document containing both Spec and Plan is created or updated.
- Requests to implement, change, fix a known issue once, or build are `build` and authorize scoped local file edits only.
- Requests to review, re-review, audit a diff, or inspect a PR are `review` and use four independent read-only specialist lanes followed by a fresh master recheck.
- Requests that explicitly require a Goal, adversarial agents, repeated review and repair, or continuing until supported bugs reach zero are `fix` and authorize the scoped local repair loop plus read-only subagent review.

If the request mixes modes, preserve their boundaries and sequence them only as authorized. A plan authorizes only its canonical requirement decision document, not implementation. A review does not authorize fixes. `fix` includes review and local repair within its stated objective, but neither `build` nor `fix` authorizes commit, push, PR creation, deployment, production writes, or messages to other people. Those actions require explicit user intent.

Read exactly one mode reference before acting:

- For `plan`, read [references/plan.md](references/plan.md).
- For `build`, read [references/build.md](references/build.md).
- For `review`, read [references/review.md](references/review.md).
- For `fix`, read [references/fix.md](references/fix.md).

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

## Shared boundaries

- Never merge a pull request.
- Do not reset, clean, discard, overwrite, or force-push work unless the user explicitly authorizes the exact target after the loss scope is shown.
- Prefer the optimal coherent solution for the real requirement and repository constraints. Reuse established project patterns before introducing new abstractions, but treat fewer lines or files only as a tiebreaker between equally correct, clear, maintainable, and verifiable options.
- Treat live refs, PR state, CI, deployments, configuration, and production data as time-sensitive; verify them in the current run.
- Separate source inspection, local validation, CI, deployment/runtime evidence, UI or device evidence, and business acceptance. Evidence in one lane does not prove another.
- Report pre-existing failures separately from failures introduced by the requested change.
- Respond in Chinese unless the user asks for another language; prefer fluent, compact prose over excessive headings and bullet lists.
- Lead the final response with the outcome, then the important evidence, incomplete checks, and any next action requiring the user.
