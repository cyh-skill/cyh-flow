---
name: build
description: Implement a scoped change, with an explicit auto option for unattended decisions. Use only when explicitly invoked as cyh-flow’s build Skill.
---

# cyh-flow build

Invoke as `$cyh-flow:build` in Codex or `/cyh-flow:build` in Claude Code after installing the `cyh-flow` plugin. Treat the current request as input; Claude Code may append `$ARGUMENTS`. If the placeholder is not expanded, use the user’s request directly. Preserve explicit-only invocation and honor any constraints from the calling workflow.

Read [the shared execution contract](../../shared/references/common.md) and [host capabilities](../../shared/references/host-capabilities.md), then follow the routing below. Read only the selected mode and references its current phase actually requires.

Read [the build protocol](../../shared/references/build.md). With leading `auto`, use the unattended build phase and its decision ledger; otherwise stop at the first material unexpected problem or decision point. Source inspection and the smallest relevant automated checks are the default validation contract; additional evidence lanes require the user or an authoritative acceptance contract.

Never merge a PR.
