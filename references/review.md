# Review mode

Use this mode for a read-only review of local changes, a commit, a branch, or a pull request. Run exactly four independent specialist review lanes, then give their reports to a fresh master reviewer for evidence-based rechecking and consolidation. The deliverable is verified findings or an evidence-bounded clean result, not a patch.

The four specialists plus fresh master are this mode's required subagent decomposition. Use maximum available concurrency for the four lanes and start the master only after all four reach a terminal result; do not replace them with coordinator-only review, collapse roles, or add a writing agent.

## Review standard

Review for the optimal implementation, not the fewest lines, files, or abstractions. An implementation is eligible to be called optimal only after it satisfies the real requirement, correctness invariants, security and data-integrity boundaries, compatibility contracts, and applicable accessibility or operational constraints. Among candidates that clear those hard gates, prefer the best evidenced fit for the repository: clear ownership, established architecture, readable control flow, testability, maintainability, appropriate performance, and controlled change scope.

Code brevity is a useful result only when behavior and comprehension remain equal. A one-line expression that hides state transitions or edge cases is worse than explicit code; an abstraction, extra test, migration, or compatibility path is justified when it closes a real requirement or risk. Conversely, do not preserve boilerplate, speculative flexibility, duplicate logic, or a new dependency merely because it appears architecturally elaborate.

Treat every clean conclusion as evidence-bounded. The goal is to close all supported associated risks in the enumerated impact surface, not to promise that arbitrary software is universally bug-free.

## Resolve the review target

1. Honor a target explicitly named by the user. Otherwise detect local uncommitted work or the branch's real base without assuming `main`.
2. For a GitHub PR, use `gh` to fetch the live base, head SHA, changed files, commits, description, review threads, and checks. Do not review a stale local approximation when the remote head differs.
3. Use a disposable copy or clone outside the repository when the current checkout is dirty, on another branch, or would contaminate validation. Do not register a worktree in or otherwise change the target repository's git metadata, index, or active worktree.
4. Include staged, unstaged, and relevant untracked source files for local reviews. Validate that the diff is non-empty before drawing conclusions.
5. Establish the originating requirement, issue, plan, or user intent. If none exists, state that requirement completeness cannot be verified.

Freeze the target as a review packet using [review/reviewer-contract.md](review/reviewer-contract.md). Record base, head, merge-base, complete local diff, relevant untracked deliverables, and a stable target fingerprint as applicable. A review result belongs to that immutable packet, not to a branch or PR name forever.

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

## Run the four specialist lanes

After the packet and impact map are frozen, launch one read-only subagent for each role below. Give every lane the same packet, [review/reviewer-contract.md](review/reviewer-contract.md), its role file, and no other reviewer's output:

1. `codex-correctness` using [review/codex-reviewer.md](review/codex-reviewer.md).
2. `ponytail-complexity` using [review/ponytail-reviewer.md](review/ponytail-reviewer.md).
3. `differential-security` using [review/differential-reviewer.md](review/differential-reviewer.md).
4. `performance-engineer` using [review/performance-reviewer.md](review/performance-reviewer.md).

Start all four concurrently when capacity permits. Spawn every specialist with no inherited conversation turns (`fork_turns: "none"` or the runtime's equivalent) and put only the immutable packet, common contract, role-file path, and execution boundary in its initial task. If the runtime cannot provide isolated context, mark that lane blocked instead of leaking another reviewer's result into it.

If the runtime has fewer free slots, use the maximum available parallelism and start each remaining isolated lane as soon as a slot opens; never collapse two personalities into one agent, expose one lane's conclusions to another, or omit a lane. A lane must not spawn more agents. The repository-carried adapter is the complete controlling contract; its pinned upstream link is provenance, not permission to dynamically execute an upstream workflow with different output, write, or nested-agent behavior.

Each lane reads the full diff, relevant surrounding code, applicable instructions, and the impact-map surfaces material to its lens. It returns only the common structured envelope. A malformed or target-mismatched result gets one isolated correction attempt with the same packet. If correction fails, preserve the raw result using the terminal transport schema in the common contract, including that role, target, `terminal_status: malformed` for a schema failure or `terminal_status: invalid` for a target mismatch, validation errors, and raw-output digest; never invent findings or a completed reviewer report.

Run focused checks when they materially increase confidence. A check may write only inside an exact coordinator-created system temporary directory or disposable repository copy; it must not change the target repository, git metadata, dependencies, user configuration, remote service, browser, infrastructure, or production state. Do not install packages during review. Read-only network requests are allowed when needed to inspect the named target. The coordinator may remove only the exact temporary path it created after capturing results; report any residue it cannot safely remove. Do not claim CI passed while checks are pending, skipped, or absent.

## Run the master recheck

Wait for all four lanes to finish or reach a terminal blocked, invalid, or malformed state, then start a fresh read-only subagent with no inherited conversation turns using [review/master-reviewer.md](review/master-reviewer.md). Give it the immutable packet, exactly four lane records (valid envelopes or terminal transport records), and read-only access to the target repository. The master is sequential and is not a fifth specialist vote: it independently reopens the code, verifies target identity, tests the evidence and reachability of every candidate, deduplicates by root cause and repair boundary, resolves conflicts, and recalculates final P0-P3 priority.

Agreement is not proof and disagreement is not disproof. Keep unsupported candidates in the rejected or unresolved audit trail instead of silently deleting them. A strong finding from one lane survives if the master verifies it; a popular finding is rejected if the evidence fails. The coordinator must validate the master's target fingerprint and schema, verify that every input candidate has exactly one disposition, and recompute the clean gate from the four lane records, impact closure, evidence lanes, coverage, and adjudicated candidates. Never trust `clean_eligible` as an assertion by itself.

## Findings

Only present verified actionable findings supported by code, reproduction, tests, measurement, or strong reachability evidence. Rank them by user impact and likelihood, consolidate sibling symptoms under their shared root cause, preserve which reviewers reported them, and provide:

- Location.
- Concrete failure or risk.
- Why it matters.
- Evidence or triggering scenario.
- A concise direction for fixing it.

Do not invent findings, style preferences, or hypothetical redesigns to appear thorough. An optimality finding must name the viable replacement and explain why it is better under the real constraints; “make this shorter” is not enough.

Report a clean result only when all four specialist lanes and the master completed against the same target, the impact map has no unexplained difference, no verified finding, advisory, or unresolved actionable candidate remains, no material coverage item is unverified, and every applicable evidence lane was exercised. Phrase it as “no supported findings within the reviewed target, enumerated impact surface, and executed evidence lanes,” then list immaterial unverified areas separately. A blocked lane, target drift, missing report, required surface that cannot be inspected, or unresolved material candidate makes the result incomplete rather than clean.

## Side-effect boundary

Review mode does not authorize editing source, applying fixes, committing, pushing, resolving threads, approving, posting comments, or changing PR state. If the user explicitly asks to post the review, use `gh`, preserve Markdown safely, re-read the posted body, and report the URL. If the user later authorizes a bounded repair, switch to `fix` and read `references/fix.md`; if they request a persistent Goal that continues until supported findings reach zero, switch to `converge` and read `references/converge.md`.

Never merge a PR.
