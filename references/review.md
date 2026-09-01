# Review mode

Use this mode for a read-only review of local changes, a commit, a branch, or a pull request. Run exactly four independent specialist review lanes and a fresh master reviewer for evidence-based rechecking and consolidation. The deliverable is verified findings or an evidence-bounded clean result for one immutable snapshot, not a patch or a live-worktree monitor.

The four specialists plus fresh master are this mode's required subagent decomposition. Use maximum available concurrency for all useful work. When at least five subagent slots are available, overlap the master's independent packet precheck with the four lanes, but never let it finalize before all four reach a terminal result. Do not replace them with coordinator-only review, collapse roles, or add a writing agent.

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

After one batched read of repository identity, applicable instructions, Git state, and required live PR metadata, freeze the target before deep code investigation. Use `python3 <cyh-flow>/scripts/review_snapshot.py freeze --repo <root> --kind local` for a working tree, or add `--kind pr|branch|commit|range --base <sha> --head <sha> [--merge-base <sha>]` for committed targets. Run it separately for every relevant dirty submodule or additional repository reported by target resolution. It creates the canonical manifest, retained diffs, copied untracked content, an inspectable detached snapshot, and the stable target fingerprint required by [review/reviewer-contract.md](review/reviewer-contract.md). Do not rewrite this logic ad hoc in shell, Python, JavaScript, or another language, and keep any explicit `--output` outside the source repository.

Build the human-readable packet around the script output and record requirement context, base, head, merge-base, changed files, project constraints, an initial impact seed, packet directory, snapshot root, and allowed checks. Reviewers inspect the frozen snapshot and retained artifacts, never the mutable source checkout. A review result belongs to that immutable packet, not to a branch or PR name forever.

Review is snapshot-first, not convergence. Once a packet is frozen, later edits to the source worktree or movement of a branch or PR do not corrupt that packet. They only mean the result is not a review of the newer target. Never wait for the live target to become stable, silently refreeze, or automatically restart review. Complete and deliver the frozen result promptly with a drift warning; refresh only when the user explicitly requests the latest target or when the enclosing `converge` or top-level `auto` contract requires a new round.

## Build the impact closure

Do not review only the changed hunks or only the paths named by the report. The coordinator creates a concise initial impact seed from the requirement, changed-file index, repository architecture, and known contracts; specialists expand the surfaces material to their lenses, and the master closes the final map before deciding that the change is complete:

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

After the packet and initial impact seed are frozen, launch one read-only subagent for each role below. Give every lane the same packet, [review/reviewer-contract.md](review/reviewer-contract.md), its role file, and no other reviewer's output:

1. `codex-correctness` using [review/codex-reviewer.md](review/codex-reviewer.md).
2. `ponytail-complexity` using [review/ponytail-reviewer.md](review/ponytail-reviewer.md).
3. `differential-security` using [review/differential-reviewer.md](review/differential-reviewer.md).
4. `performance-engineer` using [review/performance-reviewer.md](review/performance-reviewer.md).

Start all four concurrently when capacity permits. Spawn every specialist with no inherited conversation turns (`fork_turns: "none"` or the runtime's equivalent) and put only the immutable packet, common contract, role-file path, and execution boundary in its initial task. If the runtime cannot provide isolated context, mark that lane blocked instead of leaking another reviewer's result into it.

If the runtime has fewer free slots, use the maximum available parallelism and start each remaining isolated lane as soon as a slot opens; never collapse two personalities into one agent, expose one lane's conclusions to another, or omit a lane. A lane must not spawn more agents. The repository-carried adapter is the complete controlling contract; its pinned upstream link is provenance, not permission to dynamically execute an upstream workflow with different output, write, or nested-agent behavior.

Each lane reads the full diff, relevant surrounding code, applicable instructions, and the impact-map surfaces material to its lens. Minimize model/tool round trips without narrowing coverage: read the packet, contract, role, and deterministic verification result in one first-stage batch; use `rg` or CodeGraph to form the next candidate set; batch every independent file read, history query, and check within each bounded stage; never reread an unchanged artifact merely to regain context. Use adaptive sequential investigation only when one result genuinely determines the next query. Do not reconstruct hashes or compare against the mutable source checkout when `scripts/review_snapshot.py verify` already validated the retained packet.

Each lane returns only the common structured envelope. A malformed or packet-target-mismatched result gets one isolated correction attempt with the same packet. If correction fails, preserve the raw result using the terminal transport schema in the common contract, including that role, target, `terminal_status: malformed` for a schema failure or `terminal_status: invalid` for a packet validation failure, validation errors, and raw-output digest; never invent findings or a completed reviewer report.

Run focused checks when they materially increase confidence. The coordinator owns shared static or test evidence and runs each applicable command once against the frozen snapshot, recording command, working directory, environment assumptions, exit status, output digest, and result. Specialists and the master reuse that retained evidence and rerun only a candidate-specific check needed to challenge or confirm a claim. A check may write only inside an exact coordinator-created system temporary directory or disposable repository copy; it must not change the target repository, git metadata, dependencies, user configuration, remote service, browser, infrastructure, or production state. Do not install packages during review. Read-only network requests are allowed when needed to inspect the named target. The coordinator may remove only the exact temporary path it created after capturing results; report any residue it cannot safely remove. Do not claim CI passed while checks are pending, skipped, or absent.

## Overlap the master recheck

When at least five subagent slots are free, start a fresh read-only master with no inherited conversation turns at the same time as the four specialists using [review/master-reviewer.md](review/master-reviewer.md). Initially give it only the immutable packet, deterministic verification result, retained shared-check evidence, master role, and frozen snapshot access. It independently establishes the baseline, impact closure, and evidence map while specialists work, then waits. Send each valid envelope or terminal transport record to the master as it arrives; the master must receive exactly one terminal record for each required role and cannot finalize early. If fewer than five slots are available, prioritize specialist throughput and start the master as soon as a slot becomes free.

Use event-driven mailbox waits with a minutes-scale timeout rather than repeated short waits or status polling. Query the agent list only to diagnose a missing or stuck result. The master is not a fifth specialist vote: after all four records arrive, it independently reopens only enough relevant frozen code to test candidate evidence and reachability, deduplicates by root cause and repair boundary, resolves conflicts, and recalculates final P0-P3 priority.

Agreement is not proof and disagreement is not disproof. Keep unsupported candidates in the rejected or unresolved audit trail instead of silently deleting them. A strong finding from one lane survives if the master verifies it; a popular finding is rejected if the evidence fails. The coordinator must validate the master's target fingerprint and schema, verify that every input candidate has exactly one disposition, and recompute the clean gate from the four lane records, impact closure, evidence lanes, coverage, and adjudicated candidates. Never trust `clean_eligible` as an assertion by itself.

## Findings

Only present verified actionable findings supported by code, reproduction, tests, measurement, or strong reachability evidence. Rank them by user impact and likelihood, consolidate sibling symptoms under their shared root cause, preserve which reviewers reported them, and provide:

- Location.
- Concrete failure or risk.
- Why it matters.
- Evidence or triggering scenario.
- A concise direction for fixing it.

Do not invent findings, style preferences, or hypothetical redesigns to appear thorough. An optimality finding must name the viable replacement and explain why it is better under the real constraints; “make this shorter” is not enough.

Report a clean result only when all four specialist lanes and the master completed against the same frozen target, the impact map has no unexplained difference, no verified finding, advisory, or unresolved actionable candidate remains, no material coverage item is unverified, and every applicable evidence lane was exercised. Phrase it as “no supported findings within the reviewed target, enumerated impact surface, and executed evidence lanes,” then list immaterial unverified areas separately. A blocked lane, corrupted or mismatched packet, missing report, required surface that cannot be inspected, or unresolved material candidate makes the result incomplete rather than clean.

Immediately before delivery, run `python3 <cyh-flow>/scripts/review_snapshot.py verify --packet-dir <dir>` against the retained packet and `python3 <cyh-flow>/scripts/review_snapshot.py compare-live --packet-dir <dir>` against the source repository. The script re-resolves retained local ref inputs, so it detects a local branch moving after freeze. For a PR or other remote ref, also reread its live head with `gh`; the script does not fetch or query moving remote names. Packet verification failure invalidates the run. Live drift does not: report both frozen and current target IDs or SHAs, state that the result covers only the frozen snapshot, and deliver it without waiting, refreezing, or restarting. A drifted snapshot may be clean for its own target but must never be described as clean for the current worktree or latest PR head.

## Side-effect boundary

Review mode does not authorize editing source, applying fixes, committing, pushing, resolving threads, approving, posting comments, or changing PR state. If the user explicitly asks to post the review, use `gh`, preserve Markdown safely, re-read the posted body, and report the URL. If the user later authorizes a bounded repair, switch to `fix` and read `references/fix.md`; if they request a persistent Goal that continues until supported findings reach zero, switch to `converge` and read `references/converge.md`.

Never merge a PR.
