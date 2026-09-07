---
name: auto
description: Complete unattended implementation followed by all applicable review and validation. Use only when explicitly invoked as cyh-flow’s auto Skill.
---

# cyh-flow auto

Invoke as `$cyh-flow:auto` in Codex or `/cyh-flow:auto` in Claude Code after installing the `cyh-flow` plugin. Treat the current request as input; Claude Code may append `$ARGUMENTS`. If the placeholder is not expanded, use the user’s request directly. Preserve explicit-only invocation and honor any constraints from the calling workflow.

Read [the shared execution contract](../../shared/references/common.md) and [host capabilities](../../shared/references/host-capabilities.md), then follow the routing below. Read only the selected mode and references its current phase actually requires.

Read [the unattended pipeline](../../shared/references/auto.md). It loads build first, then converge and the selected review evidence in phase order. Preserve their separate completion gates and local delivery boundary.

Never merge a PR.
