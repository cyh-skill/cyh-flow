# Shared execution contract

Read this contract plus only the selected workflow reference. Do not load unrelated mode references. Resolve `<resource-root>` as the Skill directory containing `SKILL.md`, `references/`, and `scripts/`; script paths use that root, never the user's working directory. In workflow notation, `<cyh-flow> MODE` means selecting MODE through the single cyh-flow Skill: standalone Codex uses `$cyh-flow/MODE` or `$cyh-flow MODE`, and the plugin uses `$cyh-flow:cyh-flow /MODE`; standalone Claude Code uses `/cyh-flow MODE`, and the plugin uses `/cyh-flow:cyh-flow MODE`. These are host prompt invocations, not shell commands.

Compose only explicitly selected workflows. A reference loaded as an evidence lane inherits the calling workflow’s write boundary; loading review during local implementation does not authorize GitHub posting or approval. Commit, push, PR creation, deployment, production writes, and messages require explicit user intent except for the bounded comment and approval actions in an explicitly invoked PR review workflow.

## Establish project context

Before mode-specific work:

1. Resolve the real repository or repositories in scope, including parent repositories, submodules, and worktrees; treat the current directory as a starting point rather than proof of scope.
2. Read applicable host and project instructions, including `AGENTS.md`, `CLAUDE.md`, and repository documentation. Project instructions override this skill where they are more specific and do not violate user or system instructions.
3. Inspect the working tree before any mutation and preserve unrelated tracked and untracked changes.
4. Prefer an applicable Skill, then MCP or built-in tools. When comparable capabilities exist, prefer official or vendor-maintained Skills, Plugins, and MCP integrations without removing personal capabilities as a side effect.
5. If `.codegraph/` exists and CodeGraph is available, prefer it for architecture, dependency, and call-path discovery. Its existing index is the default read surface; index mutation or rebuild requires task need and authorization.
6. For GitHub, use the authenticated `gh` CLI by default. Re-read live PR heads, reviews, checks, and refs before relying on them.
7. A selected browser evidence lane uses the installed `cyh-browser-skill`: Codex exposes it as `browser-skill:cyh-browser-skill`, while Claude Code's plugin form is `/browser-skill:cyh-browser-skill`. Ordinary public web research uses the host's normal static search path. If a required browser lane lacks that Skill, report the lane as blocked.

If the target, authorization, or destructive scope remains materially ambiguous after safe inspection, stop and ask one concise question.

## Subagent-first decomposition

By default, modes are subagent-first; a mode-specific topology overrides this default. Before substantial work, map dependencies and split independent bounded units that can safely run in parallel, then use the maximum useful subagent concurrency and dispatch the next ready unit as capacity opens. Atomic stages and work whose coordination cost exceeds its benefit stay with the coordinator.

The `tidy` mode overrides this default: the coordinator is the sole cleanup writer and completes ordinary cleanup directly; independent read-only dependency or reference checks are delegated only when the benefit exceeds coordination cost.

Give every subagent an exact objective, minimum necessary context, scope and ownership, read/write and side-effect boundary, dependencies, acceptance evidence, and required return shape. Inspect and integrate every result; a completed agent or successful command is not proof that its task is accepted. Subagents inherit the selected mode's authorization and may never turn planning, review, intake, or validation into unauthorized implementation or external mutation.

Each mutable file, artifact, Git surface, runtime, or external resource has at most one owner. The selected mode defines worker count, isolation, and writer topology; do not import another mode’s topology.

## Shared boundaries

- Never merge a pull request.
- Do not reset, clean, discard, overwrite, or force-push work unless the user explicitly authorizes the exact target after the loss scope is shown.
- Prefer the optimal coherent solution for the real requirement and repository constraints. Reuse established project patterns before introducing new abstractions, but treat fewer lines or files only as a tiebreaker between equally correct, clear, maintainable, and verifiable options.
- Treat live refs, PR state, CI, deployments, configuration, and production data as time-sensitive; verify them in the current run.
- Separate source inspection, local validation, CI, deployment/runtime evidence, UI or device evidence, and business acceptance. Evidence in one lane does not prove another.
- Report pre-existing failures separately from failures introduced by the requested change.
- Respond in Chinese unless the user asks for another language; prefer fluent, compact prose over excessive headings and bullet lists.
- Lead the final response with the outcome, then the important evidence, incomplete checks, and any next action requiring the user.
