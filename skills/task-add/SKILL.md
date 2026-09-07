---
name: task-add
description: Analyze and record tasks with preserved intake evidence and screenshots. Use only when explicitly invoked as cyh-flow’s task-add Skill.
---

# cyh-flow task-add

Invoke as `$cyh-flow:task-add` in Codex or `/cyh-flow:task-add` in Claude Code after installing the `cyh-flow` plugin. Treat the current request as input; Claude Code may append `$ARGUMENTS`. If the placeholder is not expanded, use the user’s request directly. Preserve explicit-only invocation and honor any constraints from the calling workflow.

Read [the shared execution contract](../../shared/references/common.md) and [host capabilities](../../shared/references/host-capabilities.md), then follow the routing below. Read only the selected mode and references its current phase actually requires.

Read [the intake protocol](../../shared/references/task-add.md). Use read-only analysis workers and one task-document writer. Record tasks and preserve intake evidence; do not claim or implement the tasks.

Never merge a PR.
