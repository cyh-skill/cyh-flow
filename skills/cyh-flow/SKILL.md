---
name: cyh-flow
description: Software delivery workflows for PR review, repair, convergence, repository task pools, and final-state cleanup. Use only when explicitly invoked as cyh-flow with a selected mode.
---

# cyh-flow

One Skill with on-demand modes. Preserve explicit-only invocation; ordinary mentions of reviewing, fixing, converging, or tidying do not activate this workflow.

## Invocation and routing

For a standalone Codex installation, use `$cyh-flow/review ...` or `$cyh-flow review ...`. Codex recognizes `$cyh-flow`; this Skill interprets the `/review` suffix. A plugin installation qualifies the same Skill as `$cyh-flow:cyh-flow`; use `$cyh-flow:cyh-flow /review ...` or its adjacent-suffix form. These are prompt invocations, not shell commands or separately registered subskills. Do not promise a native submenu for the modes.

Claude Code uses `/cyh-flow review ...` for a standalone Skill or `/cyh-flow:cyh-flow review ...` for the plugin. It may append `$ARGUMENTS`; if that placeholder is not expanded, use the user's request directly. A host-selected Skill mention followed by `/review ...` or `review ...` selects the same mode.

Read the mode from the first argument after the explicit Skill invocation, accepting an optional leading `/`. Match one complete mode from the table below; preserve the remaining request verbatim. Only the immediately following `deep` or `auto` argument selects a documented variant. Never select a mode or variant from quoted examples, file paths, URLs, or words later in the task. Missing or unknown modes require a concise mode-selection question; do not default to implementation or unattended work. If the user explicitly composes modes, preserve their order and separate permissions.

After selecting a route, read [the shared execution contract](references/common.md) and [host capabilities](references/host-capabilities.md), then only the references in that route's row. Other references are loaded only when the selected protocol's current phase requires them; a link in this index is not an instruction to read every file. Resolve `<resource-root>` as the directory containing this `SKILL.md`, independently of the user's working directory.

| Mode / variant | Read for this route | Boundary |
| --- | --- | --- |
| `review` | [Ordinary review](references/review.md) | One isolated read-only five-axis reviewer; no implementation or task workflows. |
| `review deep` | [Deep review](references/review-deep.md) | Four isolated specialists plus a fresh master; reviewers remain read-only. |
| `review auto` | [Ordinary review](references/review.md), [Auto supplement](references/review-auto.md) | Follow a GitHub PR using one reviewer per cycle; no deep review or source edits. |
| `fix` | [Repair](references/fix.md) | One repair writer, scoped read-only evidence workers, and focused validation. |
| `converge` | [Convergence](references/converge.md) | Preserve user-selected evidence lanes, one repair writer, the finding ledger, and completion gate. |
| `task-add` | [Task intake](references/task-add.md) | Read-only analysis workers and one task-document writer; preserve intake screenshots, do not claim or implement tasks. |
| `tidy` | [Final-state cleanup](references/tidy.md) | One cleanup writer; preserve final deliverables and unrelated work; no automatic commit, push, or Git history rewriting. |
| `task-run` | [Task execution](references/task-run.md) | Each worker atomically claims a task and checks file/resource conflicts before implementation. |

For `tidy`, read only its route references and perform scoped cleanup with one writer; do not automatically invoke it from another mode.

For eligible passing PR reviews, the coordinator follows [automatic approval](references/review-approval.md); reviewers do not post or approve. A review loaded as an implementation evidence lane inherits the calling workflow's delivery boundary.

For `fix` and `task-run`, default to source inspection and the smallest relevant automated checks; preserve additional user-selected or authoritative acceptance requirements. Review does not enter fix, and task intake does not enter execution. Never merge a PR.
