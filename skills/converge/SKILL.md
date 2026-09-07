---
name: converge
description: Repeat inspection, repair, and selected evidence until supported findings reach zero. Use only when explicitly invoked as cyh-flow’s converge Skill.
---

# cyh-flow converge

Invoke as `$cyh-flow:converge` in Codex or `/cyh-flow:converge` in Claude Code after installing the `cyh-flow` plugin. Treat the current request as input; Claude Code may append `$ARGUMENTS`. If the placeholder is not expanded, use the user’s request directly. Preserve explicit-only invocation and honor any constraints from the calling workflow.

Read [the shared execution contract](../../shared/references/common.md) and [host capabilities](../../shared/references/host-capabilities.md), then follow the routing below. Read only the selected mode and references its current phase actually requires.

Read [the convergence protocol](../../shared/references/converge.md). Preserve the user-selected evidence lanes, one repair writer, finding ledger, and completion gate. Load only the review or validation protocols selected for the current phase.

Never merge a PR.
