---
name: cyh-flow
description: Run cyh-flow's Codex-first software-delivery workflow in Claude Code with explicit authorization boundaries and host-aware fallbacks.
argument-hint: "<plan|build|auto|review|fix|converge|task-add|task-run> <request>"
disable-model-invocation: true
---

# cyh-flow for Claude Code

Treat `$ARGUMENTS` as an explicit cyh-flow invocation. Read and follow the canonical [cyh-flow Skill](../../../SKILL.md) at `${CLAUDE_PLUGIN_ROOT}/SKILL.md`, including exactly one selected mode reference and all authorization boundaries.

Apply the canonical Skill's host mapping: use Claude Code `Agent` subagents for independent work, structured Task tools for live phase and dependency tracking, and the repository-local `.cyh-flow` ledger as the durable cross-host record. A user-activated Claude Code `/goal` may keep an eligible workflow running across turns, but it is a session-scoped Stop hook rather than the Codex Goal API; do not claim API equivalence or silently replace an unrelated active goal. Use `SendMessage` or shared team coordination only when the user has already enabled experimental agent teams; never enable that experiment as a Skill side effect. Claude Code plan permission mode may support read-only investigation, but exit it before `cyh-flow plan` writes its canonical document. If a required host capability is unavailable, use the documented sequential or ledger fallback and report the limitation instead of weakening evidence, independence, authorization, or completion gates.
