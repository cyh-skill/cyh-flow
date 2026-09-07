---
name: plan
description: Investigate and write one canonical requirement and implementation plan. Use only when explicitly invoked as cyh-flow’s plan Skill.
---

# cyh-flow plan

Invoke as `$cyh-flow:plan` in Codex or `/cyh-flow:plan` in Claude Code after installing the `cyh-flow` plugin. Treat the current request as input; Claude Code may append `$ARGUMENTS`. If the placeholder is not expanded, use the user’s request directly. Preserve explicit-only invocation and honor any constraints from the calling workflow.

Read [the shared execution contract](../../shared/references/common.md) and [host capabilities](../../shared/references/host-capabilities.md), then follow the routing below. Read only the selected mode and references its current phase actually requires.

Read [the planning protocol](../../shared/references/plan.md). Keep application code and external state unchanged; the canonical plan document is the sole write surface. Native plan permission mode must permit that document write before the writing phase.

Never merge a PR.
