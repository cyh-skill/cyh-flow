---
name: review
description: Review a diff or PR; deep uses specialists and auto follows GitHub PR activity. Use only when explicitly invoked as cyh-flow’s review Skill.
---

# cyh-flow review

Invoke as `$cyh-flow:review` in Codex or `/cyh-flow:review` in Claude Code after installing the `cyh-flow` plugin. Treat the current request as input; Claude Code may append `$ARGUMENTS`. If the placeholder is not expanded, use the user’s request directly. Preserve explicit-only invocation and honor any constraints from the calling workflow.

Read [the shared execution contract](../../shared/references/common.md) and [host capabilities](../../shared/references/host-capabilities.md), then follow the routing below. Read only the selected mode and references its current phase actually requires.

Use only the leading argument to select a variant: `deep` reads [deep review](../../shared/references/review-deep.md); `auto` reads [ordinary review](../../shared/references/review.md) then [the auto supplement](../../shared/references/review-auto.md); otherwise read only [ordinary review](../../shared/references/review.md). Ordinary and auto use one isolated reviewer; deep uses four specialists plus a fresh master. Reviewers remain read-only. The coordinator applies [automatic approval](../../shared/references/review-approval.md) after an eligible passing PR review. Do not load implementation or task workflows.

Never merge a PR.
