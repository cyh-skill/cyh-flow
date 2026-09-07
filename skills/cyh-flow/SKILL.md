---
name: cyh-flow
description: Software delivery workflows for planning, implementation, PR review, repair, convergence, and repository task pools. Use only when explicitly invoked as cyh-flow with a selected mode.
---

# cyh-flow

One Skill with on-demand modes. Preserve explicit-only invocation; ordinary mentions of planning, building, or reviewing do not activate this workflow.

## Invocation and routing

For a standalone Codex installation, use `$cyh-flow/review ...` or `$cyh-flow review ...`. Codex recognizes `$cyh-flow`; this Skill interprets the `/review` suffix. A plugin installation qualifies the same Skill as `$cyh-flow:cyh-flow`; use `$cyh-flow:cyh-flow /review ...` or its adjacent-suffix form. These are prompt invocations, not shell commands or separately registered subskills. Do not promise a native submenu for the modes.

Claude Code uses `/cyh-flow review ...` for a standalone Skill or `/cyh-flow:cyh-flow review ...` for the plugin. It may append `$ARGUMENTS`; if that placeholder is not expanded, use the user's request directly. A host-selected Skill mention followed by `/review ...` or `review ...` selects the same mode.

Read the mode from the first argument after the explicit Skill invocation, accepting an optional leading `/`. Match one complete mode from the table below; preserve the remaining request verbatim. Only the immediately following `deep` or `auto` argument selects a documented variant. Never select a mode or variant from quoted examples, file paths, URLs, or words later in the task. Missing or unknown modes require a concise mode-selection question; do not default to implementation or unattended work. If the user explicitly composes modes, preserve their order and separate permissions.

After selecting a route, read [the shared execution contract](references/common.md) and [host capabilities](references/host-capabilities.md), then only the references in that route's row. Other references are loaded only when the selected protocol's current phase requires them; a link in this index is not an instruction to read every file. Resolve `<resource-root>` as the directory containing this `SKILL.md`, independently of the user's working directory.

| Mode / variant | Read for this route | Boundary |
| --- | --- | --- |
| `plan` | [Planning](references/plan.md) | Investigate and write one canonical requirement/implementation document; no application code or external writes. |
| `build` | [Build](references/build.md) | Implement the scoped request; stop at the first material unexpected problem or decision point. |
| `build auto` | [Build](references/build.md) | Continue scoped implementation with a Goal and decision ledger; no automatic review phase. |
| `auto` | [Unattended pipeline](references/auto.md) | Load build, then converge and required evidence in phase order; preserve separate completion gates. |
| `review` | [Ordinary review](references/review.md) | One isolated read-only five-axis reviewer; no implementation or task workflows. |
| `review deep` | [Deep review](references/review-deep.md) | Four isolated specialists plus a fresh master; reviewers remain read-only. |
| `review auto` | [Ordinary review](references/review.md), [Auto supplement](references/review-auto.md) | Follow a GitHub PR using one reviewer per cycle; no deep review or source edits. |
| `re-review` | [Acceptance review](references/re-review.md) | One isolated acceptance reviewer reconciles existing issues and direct fix regressions; no broad new review or source edits. |
| `fix` | [Repair](references/fix.md) | One repair writer, scoped read-only evidence workers, and focused validation. |
| `converge` | [Convergence](references/converge.md) | Preserve user-selected evidence lanes, one repair writer, the finding ledger, and completion gate. |
| `task-add` | [Task intake](references/task-add.md) | Read-only analysis workers and one task-document writer; preserve intake screenshots, do not claim or implement tasks. |
| `task-run` | [Task execution](references/task-run.md) | Each worker atomically claims a task and checks file/resource conflicts before implementation. |

For eligible passing PR reviews, the coordinator follows [automatic approval](references/review-approval.md); reviewers do not post or approve. A review loaded as an implementation evidence lane inherits the calling workflow's delivery boundary.

For `build`, `fix`, and `task-run`, default to source inspection and the smallest relevant automated checks; preserve additional user-selected or authoritative acceptance requirements. Planning does not automatically enter build, review does not enter fix, and task intake does not enter execution. Never merge a PR.
