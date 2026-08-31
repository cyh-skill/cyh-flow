# Plan mode

Use this mode to understand a requested change and produce an actionable implementation plan. Stay read-only throughout unless the user separately asks to save the plan as a file.

## Investigation

1. Restate the intended outcome and identify success criteria from the user's perspective.
2. Inspect the current implementation before proposing a replacement. Trace relevant entry points, callers, data flow, state ownership, external contracts, configuration, tests, and deployment boundaries.
3. Enumerate the affected surfaces in reverse as well as forward: do not validate completeness only against endpoints or files already named in the request.
4. Find existing utilities, components, APIs, patterns, and tests that should be reused.
5. Identify cross-repository or cross-platform differences instead of treating one codebase or UI as proof for all consumers.
6. Ask only questions that block a responsible plan. Make reasonable, disclosed assumptions when the choice is reversible and low-risk.

Do not edit application code, create branches, create or update issues or PRs, post comments, push, deploy, or change external state in plan mode.

## Plan quality

Scale the plan to the work. Include the following when they materially affect implementation:

- Current behavior and evidence.
- Scope, non-goals, and affected repositories or platforms.
- Reuse points and the recommended approach, with alternatives only when the trade-off is real.
- Contract, schema, state, permission, migration, compatibility, and rollback implications.
- Concrete implementation steps with likely modules or files, without pretending unverified paths are certain.
- Validation and acceptance split into source, automated tests, CI, deployment/runtime, UI/device, and business evidence as applicable.
- External actions or permissions that will require later authorization.

Call out uncertainty and live facts that must be refreshed during build. Do not present a plan as proof that implementation or acceptance has happened.

## Handoff

End with an implementation-ready summary. If the user asks to continue, switch to build mode and read `references/build.md`; otherwise stop after the plan.
