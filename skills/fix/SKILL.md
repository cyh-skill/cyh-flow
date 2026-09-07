---
name: fix
description: Repair one known bug or review finding with focused validation. Use only when explicitly invoked as cyh-flow’s fix Skill.
---

# cyh-flow fix

Invoke as `$cyh-flow:fix` in Codex or `/cyh-flow:fix` in Claude Code after installing the `cyh-flow` plugin. Treat the current request as input; Claude Code may append `$ARGUMENTS`. If the placeholder is not expanded, use the user’s request directly. Preserve explicit-only invocation and honor any constraints from the calling workflow.

Read [the shared execution contract](../../shared/references/common.md) and [host capabilities](../../shared/references/host-capabilities.md), then follow the routing below. Read only the selected mode and references its current phase actually requires.

Read [the repair protocol](../../shared/references/fix.md). Use one repair writer and scoped read-only evidence workers. Source inspection and the smallest relevant automated checks are the default; load review or other evidence lanes only when selected.

Never merge a PR.
