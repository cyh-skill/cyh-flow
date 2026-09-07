---
name: re-review
description: Verify existing PR review issues against current fixes and publish the reconciliation. Use only when explicitly invoked as cyh-flow’s re-review Skill.
---

# cyh-flow re-review

Invoke as `$cyh-flow:re-review` in Codex or `/cyh-flow:re-review` in Claude Code after installing the `cyh-flow` plugin. Treat the current request as input; Claude Code may append `$ARGUMENTS`. If the placeholder is not expanded, use the user’s request directly. Preserve explicit-only invocation and honor any constraints from the calling workflow.

Read [the shared execution contract](../../shared/references/common.md) and [host capabilities](../../shared/references/host-capabilities.md), then follow the routing below. Read only the selected mode and references its current phase actually requires.

Read [the acceptance protocol](../../shared/references/re-review.md) and [automatic approval](../../shared/references/review-approval.md). Use one isolated acceptance reviewer. Reconcile existing issues and direct fix regressions; do not expand into a new broad review or modify code.

Never merge a PR.
