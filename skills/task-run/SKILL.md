---
name: task-run
description: Atomically claim stored tasks and implement them with disjoint ownership. Use only when explicitly invoked as cyh-flow’s task-run Skill.
---

# cyh-flow task-run

Invoke as `$cyh-flow:task-run` in Codex or `/cyh-flow:task-run` in Claude Code after installing the `cyh-flow` plugin. Treat the current request as input; Claude Code may append `$ARGUMENTS`. If the placeholder is not expanded, use the user’s request directly. Preserve explicit-only invocation and honor any constraints from the calling workflow.

Read [the shared execution contract](../../shared/references/common.md) and [host capabilities](../../shared/references/host-capabilities.md), then follow the routing below. Read only the selected mode and references its current phase actually requires.

Read [the task execution protocol](../../shared/references/task-run.md). Each worker claims a pending task and checks file and resource conflicts before implementation. Source inspection and the smallest relevant automated checks are the default validation contract; preserve additional explicitly selected evidence lanes.

Never merge a PR.
