# Review mode

Use this mode for a read-only review of local changes, a commit, a branch, or a pull request. The deliverable is verified findings or a clean result, not a patch.

## Review standard

Review for the optimal implementation, not the fewest lines, files, or abstractions. An implementation is eligible to be called optimal only after it satisfies the real requirement, correctness invariants, security and data-integrity boundaries, compatibility contracts, and applicable accessibility or operational constraints. Among candidates that clear those hard gates, prefer the best evidenced fit for the repository: clear ownership, established architecture, readable control flow, testability, maintainability, appropriate performance, and controlled change scope.

Code brevity is a useful result only when behavior and comprehension remain equal. A one-line expression that hides state transitions or edge cases is worse than explicit code; an abstraction, extra test, migration, or compatibility path is justified when it closes a real requirement or risk. Conversely, do not preserve boilerplate, speculative flexibility, duplicate logic, or a new dependency merely because it appears architecturally elaborate.

Treat every clean conclusion as evidence-bounded. The goal is to close all supported associated risks in the enumerated impact surface, not to promise that arbitrary software is universally bug-free.

## Resolve the review target

1. Honor a target explicitly named by the user. Otherwise detect local uncommitted work or the branch's real base without assuming `main`.
2. For a GitHub PR, use `gh` to fetch the live base, head SHA, changed files, commits, description, review threads, and checks. Do not review a stale local approximation when the remote head differs.
3. Use an isolated worktree or temporary checkout when the current checkout is dirty, on another branch, or would contaminate validation. Do not disturb the user's active worktree.
4. Include staged, unstaged, and relevant untracked source files for local reviews. Validate that the diff is non-empty before drawing conclusions.
5. Establish the originating requirement, issue, plan, or user intent. If none exists, state that requirement completeness cannot be verified.

Freeze or record the reviewed target precisely enough that later drift is detectable: base, head, merge-base, complete local diff, and relevant untracked deliverables as applicable. A review result belongs to that target, not to a branch or PR name forever.

## Build the impact closure

Do not review only the changed hunks or only the paths named by the report. Construct an impact map before deciding that the change is complete:

1. Identify the changed behavior and its owning symbols, files, data, configuration, and contracts.
2. Trace upstream constraints: requirements, callers, permissions, schemas, legacy data, platform rules, and external contracts that determine what the behavior must preserve.
3. Trace downstream consumers: direct and transitive callers, UI and API entry points, jobs, events, caches, persistence, generated artifacts, tests, build or deployment paths, and observability.
4. Inspect sibling paths that share the same abstraction or invariant, including alternate entry points, roles, tenants, locales, platforms, error paths, retries, concurrency, initialization, update, cleanup, migration, and rollback.
5. Enumerate the expected affected surfaces independently of the diff, then compare them with the surfaces intentionally changed, intentionally preserved with a reason, and actually validated. Investigate every unexplained item in that difference set before reporting clean.

When shared code is changed, enumerate its consumers rather than validating only the ticket path. When a symptom is patched locally, verify whether the root cause belongs at a shared ownership boundary; do not force centralization when consumers intentionally have different contracts.

## Judge the implementation choices

After understanding the full flow, use this adapted reuse ladder to discover candidates:

1. No implementation change because the requirement is already met or should not exist.
2. An existing project helper, type, component, client, test utility, or established pattern.
3. A language or standard-library facility.
4. A native platform capability, such as browser semantics, CSS, operating-system behavior, or a database constraint.
5. An already-installed dependency whose semantics, lifecycle, security, and footprint fit the use case.
6. Direct, explicit local code.
7. A new abstraction or dependency when the preceding options cannot satisfy the real constraints cleanly.

This is a search order, not a command to stop at the first mechanically available option. Compare viable candidates against the hard gates and repository context. Reuse is wrong when semantics, ownership, coupling, lifecycle, or compatibility do not fit; local code is wrong when it needlessly duplicates a proven capability. One line is never a goal by itself, and a shorter diff is only a tiebreaker between equally correct, clear, maintainable, and verifiable solutions.

## Review passes

Read the full diff, relevant surrounding code, and applicable repository instructions. Check:

- Requirement completeness and scope: missing behavior, partial implementation, wrong interpretation, or unrelated changes.
- Correctness: logic, error paths, state transitions, concurrency, ordering, idempotency, cleanup, and boundary values.
- Security and data boundaries: authentication, authorization, tenant or ownership isolation, input validation, secrets, logging, and destructive behavior.
- Compatibility and contracts: API shapes, schema and migration behavior, callers, legacy data, configuration, localization, and platform differences.
- Optimality and project fit: whether the chosen ownership boundary and implementation beat the viable alternatives above without duplicate code, speculative abstraction, hidden cleverness, unnecessary dependencies, or avoidable churn.
- Tests and acceptance: whether tests fail for the relevant broken behavior, exercise affected consumers and sibling paths, and leave any evidence lane uncovered.
- Operations and lifecycle: performance where material, resource cleanup, retries, recovery, observability, rollout, migration, and rollback behavior.

Run focused, non-mutating checks when they materially increase confidence. Use an isolated worktree if a command writes caches or generated files. Do not claim CI passed while checks are pending, skipped, or absent.

## Findings

Only report actionable findings supported by code, reproduction, tests, or strong reachability evidence. Rank them by user impact and likelihood, consolidate sibling symptoms under their shared root cause, and provide:

- Location.
- Concrete failure or risk.
- Why it matters.
- Evidence or triggering scenario.
- A concise direction for fixing it.

Do not invent findings, style preferences, or hypothetical redesigns to appear thorough. An optimality finding must name the viable replacement and explain why it is better under the real constraints; “make this shorter” is not enough.

Report a clean result only when the impact map has no unexplained difference, no supported actionable finding remains, and the applicable evidence lanes have been exercised. Phrase it as “no supported findings within the reviewed target, enumerated impact surface, and executed evidence lanes,” then list material unverified areas separately. If a required surface cannot be inspected or validated, report the limitation instead of declaring the implementation fully clean.

## Side-effect boundary

Review mode does not authorize editing source, applying fixes, committing, pushing, resolving threads, approving, posting comments, or changing PR state. If the user explicitly asks to post the review, use `gh`, preserve Markdown safely, re-read the posted body, and report the URL. If the user later authorizes fixes, switch to build mode and read `references/build.md`.

Never merge a PR.
