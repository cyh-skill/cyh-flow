# Plan mode

Use this mode to understand a requested change and maintain one unified requirement plan that covers both what the system must do and how the current system will implement and validate it. Application code, configuration, Git state, and external systems stay read-only; creating or updating that requirement document is the only mutation authorized by entering plan mode.

Claude Code's native plan permission mode may cover the read-only investigation portion. The coordinator switches to an editing-capable permission mode for the required canonical-document write and reports persistence only after that write succeeds.

## Canonical requirement document

Every requirement decision made during plan mode is recorded in one canonical document that combines specification and implementation-planning responsibilities. Repository-appropriate headings may be used; a separate `Spec`/`Plan` pair is unnecessary. A decision includes confirmed scope and non-goals, chosen behavior or contract, accepted trade-offs, implementation direction, compatibility or migration treatment, and acceptance criteria. Proposals, assumptions, unresolved questions, and confirmed decisions carry distinct status so only approved choices appear settled.

Before creating a document:

1. Determine a stable requirement identity from an issue or task ID when available; otherwise use the user-visible outcome and domain, not the current conversation wording.
2. Search the repository's documented planning locations and Markdown content for that identity, title, and distinctive terms. Also inspect documents named by the user.
3. If the same requirement already has a canonical document, update it in place and preserve its path across later conversations, clarifications, and plan iterations.
4. If no document exists, follow the repository's established requirement or planning convention. When there is no convention, create `docs/plans/<stable-requirement-slug>.md` in the primary repository. Use a durable descriptive slug rather than a date or session identifier.
5. For a requirement spanning repositories or platforms, keep one canonical document in the coordinating or primary repository; other locations link to that source of truth when required.

If multiple legacy documents already cover the same requirement, do not delete or silently merge them. Select and state the canonical document, record links and any unresolved conflicts there, then use only that document for new decisions unless the user or repository rules require consolidation.

## Parallel investigation

Before synthesis, decompose the requirement into independent read-only investigation lanes and use the maximum useful subagent concurrency. Split by real surfaces such as current behavior and call paths, data and external contracts, permissions and migration, tests and acceptance, or repository and platform variants; do not assign arbitrary duplicate summaries. Give every worker a bounded question and require concrete paths, symbols, evidence, assumptions, and unresolved gaps.

All plan subagents remain read-only, including against the canonical requirement document. The coordinator inspects every lane, resolves contradictions against source evidence, and is the sole writer that creates or updates the canonical Markdown so parallel analysis cannot produce competing requirement records.

## Unified plan responsibilities

Organize the document around the requirement's user flows, capabilities, rules, and decisions rather than around a Spec-versus-Plan phase boundary. For every material requirement or decision, connect the intended behavior to its implementation and evidence closely enough that readers do not have to reconcile two independent descriptions.

The unified plan must cover the responsibilities traditionally handled by a specification: intended outcome, users or actors, scope and non-goals, functional behavior and business rules, states and error or edge behavior, contracts and data or permission constraints, compatibility expectations, and observable acceptance criteria. It must also cover the responsibilities traditionally handled by an implementation plan: current implementation evidence, chosen design and rationale, reuse points, affected repositories and modules, ordered changes and dependencies, migration and rollback treatment, validation across applicable evidence lanes, live facts to refresh, and external actions requiring later authorization.

Use repository-appropriate headings and keep a decision log with status and rationale in the same document. When a requirement decision changes, update its behavior, implementation impact, and acceptance coverage together. Before handoff, verify that every confirmed behavior has an implementation and validation path, and that no proposed work lacks a requirement rationale.

## Investigation

1. Restate the intended outcome and identify success criteria from the user's perspective.
2. Inspect the current implementation before proposing a replacement. Trace relevant entry points, callers, data flow, state ownership, external contracts, configuration, tests, and deployment boundaries.
3. Enumerate the affected surfaces in reverse as well as forward: do not validate completeness only against endpoints or files already named in the request.
4. Find existing utilities, components, APIs, patterns, and tests that should be reused.
5. Identify cross-repository or cross-platform differences instead of treating one codebase or UI as proof for all consumers.
6. Ask only questions that block a responsible plan. Make reasonable, disclosed assumptions when the choice is reversible and low-risk.

The canonical requirement document is plan mode's sole write surface. Application code, configuration, branches, issues, PRs, comments, remotes, deployments, external state, and unrelated documentation remain unchanged.

## Plan quality

Scale the plan to the work. Include the following when they materially affect implementation:

- Current behavior and evidence.
- Scope, non-goals, and affected repositories or platforms.
- Reuse points and the recommended approach, with alternatives only when the trade-off is real.
- Contract, schema, state, permission, migration, compatibility, and rollback implications.
- Concrete implementation steps with likely modules or files, without pretending unverified paths are certain.
- Validation and acceptance split into source, automated tests, CI, deployment/runtime, UI/device, and business evidence as applicable.
- External actions or permissions that will require later authorization.

Write each confirmed decision and material revision to the canonical document as it is reached. Label uncertainty and live facts that require refresh during build, and report the result as implementation-ready planning evidence rather than implementation or acceptance evidence.

## Handoff

End with the canonical document path, its readiness as a unified requirement plan, and an implementation-ready summary of what was added or changed there. If no safe document write was possible, state the blocker and provide the exact intended path and content rather than pretending it was persisted. If the user asks to continue, treat the same document as the source of truth for both required behavior and implementation, switch to build mode, and read `references/build.md`; otherwise stop after the plan.
