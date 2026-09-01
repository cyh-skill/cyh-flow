# Plan mode

Use this mode to understand a requested change and maintain its Spec and implementation Plan together in one canonical Markdown document. Application code, configuration, Git state, and external systems stay read-only; creating or updating that requirement document is the only mutation authorized by entering plan mode.

## Canonical requirement document

Every requirement decision made during plan mode must be recorded in the canonical document, not left only in chat. The document must contain both the requirement Spec and its implementation Plan; do not create separately maintained `*-spec.md` and `*-plan.md` files for the same requirement. A decision includes confirmed scope and non-goals, chosen behavior or contract, accepted trade-offs, implementation direction, compatibility or migration treatment, and acceptance criteria. Keep proposals, assumptions, unresolved questions, and confirmed decisions visibly distinct so an unapproved option is never recorded as settled.

Before creating a document:

1. Determine a stable requirement identity from an issue or task ID when available; otherwise use the user-visible outcome and domain, not the current conversation wording.
2. Search the repository's documented planning locations and Markdown content for that identity, title, and distinctive terms. Also inspect documents named by the user.
3. If the same requirement already has a canonical document, update it in place and preserve its path. Do not create a dated copy, revision copy, `v2`, or a new file for a later conversation, clarification, or plan iteration.
4. If no document exists, follow the repository's established requirement or planning convention. When there is no convention, create `docs/plans/<stable-requirement-slug>.md` in the primary repository. Use a durable descriptive slug rather than a date or session identifier.
5. For a requirement spanning repositories or platforms, keep one canonical document in the coordinating or primary repository. Other locations may link to it when required, but must not carry separately maintained copies of the decisions.

If multiple legacy documents already cover the same requirement, do not delete or silently merge them. Select and state the canonical document, record links and any unresolved conflicts there, then use only that document for new decisions unless the user or repository rules require consolidation.

## Required Spec and Plan

Use recognizable `## Spec` and `## Plan` sections in the same file by default. A repository's established headings may be retained only when the two parts remain explicit and unambiguous.

The Spec defines what must be true independently of a particular implementation. Record the intended outcome, users or actors, scope and non-goals, functional behavior and business rules, states and error or edge behavior, contracts and data or permission constraints, compatibility expectations, and observable acceptance criteria. Mark assumptions and open product questions separately from confirmed requirements.

The Plan defines how the current system will satisfy that Spec. Record current implementation evidence, the chosen design and rationale, reuse points, affected repositories and modules, ordered implementation steps and dependencies, contract or schema migration and rollback treatment, validation across the applicable evidence lanes, live facts to refresh, and external actions requiring later authorization.

Keep a decision log with status and rationale in the same document, either shared or inside the relevant section. Write the Spec before finalizing the Plan, derive Plan steps from explicit Spec requirements, and update both sections together when a decision changes. Before handoff, check that every confirmed Spec requirement maps to implementation and validation coverage in the Plan, with no unexplained Plan work outside the Spec.

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

End with the canonical document path, the readiness of its Spec and Plan, and an implementation-ready summary of what was added or changed there. If no safe document write was possible, state the blocker and provide the exact intended path and content rather than pretending it was persisted. If the user asks to continue, treat the Spec as the behavior source of truth and the Plan as the implementation handoff, switch to build mode, and read `references/build.md`; otherwise stop after the plan.
