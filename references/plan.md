# Plan mode

Use this mode to understand a requested change and maintain one unified requirement plan that covers both what the system must do and how the current system will implement and validate it. Application code, configuration, Git state, and external systems stay read-only; creating or updating that requirement document is the only mutation authorized by entering plan mode.

## Canonical requirement document

Every requirement decision made during plan mode must be recorded in the canonical document, not left only in chat. The document must fulfill both specification and implementation-planning responsibilities as one integrated deliverable; do not model them as separately maintained artifacts or require separate `Spec` and `Plan` sections, and do not create `*-spec.md` and `*-plan.md` files for the same requirement. A decision includes confirmed scope and non-goals, chosen behavior or contract, accepted trade-offs, implementation direction, compatibility or migration treatment, and acceptance criteria. Keep proposals, assumptions, unresolved questions, and confirmed decisions visibly distinct so an unapproved option is never recorded as settled.

Before creating a document:

1. Determine a stable requirement identity from an issue or task ID when available; otherwise use the user-visible outcome and domain, not the current conversation wording.
2. Search the repository's documented planning locations and Markdown content for that identity, title, and distinctive terms. Also inspect documents named by the user.
3. If the same requirement already has a canonical document, update it in place and preserve its path. Do not create a dated copy, revision copy, `v2`, or a new file for a later conversation, clarification, or plan iteration.
4. If no document exists, follow the repository's established requirement or planning convention. When there is no convention, create `docs/plans/<stable-requirement-slug>.md` in the primary repository. Use a durable descriptive slug rather than a date or session identifier.
5. For a requirement spanning repositories or platforms, keep one canonical document in the coordinating or primary repository. Other locations may link to it when required, but must not carry separately maintained copies of the decisions.

If multiple legacy documents already cover the same requirement, do not delete or silently merge them. Select and state the canonical document, record links and any unresolved conflicts there, then use only that document for new decisions unless the user or repository rules require consolidation.

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

Do not edit application code or configuration, create branches, create or update issues or PRs, post comments, push, deploy, or change external state in plan mode. Do not modify unrelated documentation. The canonical requirement document is the sole default write boundary.

## Plan quality

Scale the plan to the work. Include the following when they materially affect implementation:

- Current behavior and evidence.
- Scope, non-goals, and affected repositories or platforms.
- Reuse points and the recommended approach, with alternatives only when the trade-off is real.
- Contract, schema, state, permission, migration, compatibility, and rollback implications.
- Concrete implementation steps with likely modules or files, without pretending unverified paths are certain.
- Validation and acceptance split into source, automated tests, CI, deployment/runtime, UI/device, and business evidence as applicable.
- External actions or permissions that will require later authorization.

Write each confirmed decision and material plan revision to the canonical document as it is reached. Call out uncertainty and live facts that must be refreshed during build. Do not present a plan as proof that implementation or acceptance has happened.

## Handoff

End with the canonical document path, its readiness as a unified requirement plan, and an implementation-ready summary of what was added or changed there. If no safe document write was possible, state the blocker and provide the exact intended path and content rather than pretending it was persisted. If the user asks to continue, treat the same document as the source of truth for both required behavior and implementation, switch to build mode, and read `references/build.md`; otherwise stop after the plan.
