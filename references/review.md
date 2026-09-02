# Review mode

Use this mode for a read-only review of local changes, a commit, a branch, or a pull request. Run exactly four independent specialist review lanes and a fresh master reviewer for evidence-based rechecking and consolidation. The deliverable is verified findings or an evidence-bounded clean result from a best-effort live review, not a patch or a guarantee about the target's final state.

The four specialists plus fresh master are this mode's required subagent decomposition. Use maximum available concurrency for useful work. When at least five subagent slots and addressable follow-up mailboxes are available, overlap the master's independent target inspection with the four lanes, but never let it finalize before all four reach a terminal result. On any run without enabled persistent mailbox delivery, finish the four lanes first and then start a fresh master with their terminal records. Do not replace them with coordinator-only review, collapse roles, or add a writing agent.

## Review standard

Review for the optimal implementation, not the fewest lines, files, or abstractions. An implementation is eligible to be called optimal only after it satisfies the real requirement, correctness invariants, security and data-integrity boundaries, compatibility contracts, and applicable accessibility or operational constraints. Among candidates that clear those hard gates, prefer the best evidenced fit for the repository: clear ownership, established architecture, readable control flow, testability, maintainability, appropriate performance, and controlled change scope.

Code brevity is useful only when behavior and comprehension remain equal. Do not preserve boilerplate, speculative flexibility, duplicate logic, or a new dependency merely because it appears architecturally elaborate, and do not reject an abstraction, test, migration, or compatibility path that closes a real requirement or risk.

Treat every conclusion as evidence-bounded. The goal is to close supported risks in the impact surface actually inspected, not to promise that arbitrary software or a later revision is universally bug-free.

## Resolve only enough to start

1. Honor the target explicitly named by the user. Otherwise detect the current working-tree changes or the branch's real base without assuming `main`.
2. For a GitHub PR, use authenticated `gh` for current metadata, diff, reviews, checks, and repository access. Use `gh api` only for required GitHub data not exposed by ordinary `gh pr` commands. Do not open a browser for ordinary PR inspection.
3. Never switch, reset, clean, or run `gh pr checkout` in the user's current repository merely to inspect a PR. A dirty checkout, unrelated branch, or missing local PR branch is a routing signal rather than a blocker. Read through existing objects or `gh` when sufficient; create one disposable clone only when surrounding source cannot otherwise be inspected safely.
4. For local review, include staged, unstaged, and relevant untracked source visible when each lane reads the target. Confirm there is something to review before dispatching the lanes.
5. Pass through explicit user intent or requirement text, but do not manufacture a requirement. If no authoritative requirement is available, state that requirement completeness cannot be verified.

Do not freeze, lock, pin, fingerprint, snapshot, copy, hash, verify, compare, or monitor the target. Do not build a shared fact packet, changed-file summary, architecture conclusion, suspicious-line list, candidate list, severity hint, or repair recommendation before dispatch. Each reviewer is responsible for discovering the current diff and every fact material to its own review.

The worktree, branch, or PR may change during review. Do not wait for stability, check drift, invalidate completed work, silently restart, or rerun merely because somebody changed it. Specialists and the master may therefore observe different revisions. Complete the review using the evidence each role actually inspected, and do not claim that the result covers a later or final revision.

## Build the impact closure

Do not review only changed hunks. Each specialist independently traces the surfaces material to its lens, and the master builds and closes the final impact map:

1. Identify changed behavior and its owning symbols, files, data, configuration, and contracts.
2. Trace upstream requirements, callers, permissions, schemas, legacy data, platform rules, and external contracts.
3. Trace downstream consumers, UI and API entry points, jobs, events, caches, persistence, generated artifacts, tests, build or deployment paths, and observability.
4. Inspect sibling paths that share the same abstraction or invariant, including alternate entry points, roles, tenants, locales, platforms, errors, retries, concurrency, initialization, update, cleanup, migration, and rollback.
5. Compare expected affected surfaces with what changed, what was intentionally preserved, and what was actually validated; investigate unexplained differences before reporting clean.

When shared code changes, enumerate its consumers rather than validating only the ticket path. When a symptom is patched locally, verify whether the root cause belongs at a shared ownership boundary without forcing centralization where consumers intentionally differ.

## Judge implementation choices

After understanding the flow, consider in order: no change because the requirement is already met or should not exist; an established project helper or pattern; a language or standard-library facility; a native platform capability; an already-installed dependency; direct explicit local code; and finally a new abstraction or dependency. This is a search order, not an instruction to stop at the first mechanically available choice. Semantics, ownership, coupling, lifecycle, compatibility, readability, and verifiability decide; fewer lines are only a tiebreaker.

## Run the four specialist lanes

Launch one isolated read-only subagent for each role:

1. `codex-correctness` using [review/codex-reviewer.md](review/codex-reviewer.md).
2. `ponytail-complexity` using [review/ponytail-reviewer.md](review/ponytail-reviewer.md).
3. `differential-security` using [review/differential-reviewer.md](review/differential-reviewer.md).
4. `performance-engineer` using [review/performance-reviewer.md](review/performance-reviewer.md).

Start all four concurrently when capacity permits. Spawn each specialist with no inherited conversation turns and give it only the target locator, any necessary repository access path, explicit user requirement text, applicable project instructions, [review/reviewer-contract.md](review/reviewer-contract.md), its role file, and the read-only side-effect boundary. Do not expose coordinator analysis or another reviewer's output. If isolated context is unavailable, mark that lane blocked rather than blending reviewer personalities.

If fewer slots are free, use the maximum available parallelism and start each remaining isolated lane as capacity opens. Never collapse two roles into one agent or omit a lane. A lane must not spawn more agents. The repository-carried adapter is the complete controlling contract; its upstream link is provenance, not permission to execute a different workflow.

Each lane independently reads the current full diff, surrounding code, requirement sources, architecture, callers, contracts, history, tests, and configuration material to its lens. It treats suspicious code as a hypothesis and admits a candidate only after satisfying the common contract's introduction, reachability, authoritative-contract, scope-decision, and repair-ownership gates. A condition or enum does not prove a producible business state, a frontend gate does not prove authorization semantics, and a nearby historical implementation does not override an explicit scope decision.

Each lane returns only the common structured envelope. A malformed result gets one isolated correction attempt with the same minimal input. If correction fails, preserve the raw result using the terminal transport schema; never invent findings or a completed reviewer report.

Run focused checks only when they materially increase confidence. Reviewers choose and execute the checks needed for their own candidates, and the master may rerun a proportionate non-mutating check during falsification. Checks may write only inside an approved system temporary directory or disposable repository copy, must use already-available dependencies, and must not change the target repository, Git metadata, user configuration, remote services, browser, infrastructure, or production state. Do not install packages during review and do not claim CI passed while checks are pending, skipped, or absent.

## Master recheck

When addressable follow-up delivery and capacity are available, start a fresh read-only master with no inherited conversation turns alongside the specialists using [review/master-reviewer.md](review/master-reviewer.md). Initially give it only the same minimal target locator and access context, common contract, master role, explicit requirement text, project instructions, and read-only boundary. It independently reads the current target, establishes the requirement baseline, scope decisions, architecture ownership, impact closure, and known unknowns, then waits. Send exactly one terminal record for each role as it arrives. Otherwise collect all four records first and then start a fresh master with the minimal target context plus those records.

The master is not a fifth vote or a summary writer. It treats every candidate, proposed severity, confidence, and repair direction as untrusted and actively searches for counterexamples in the available baseline, state producers, entry points, authoritative contracts, role combinations, history, alternate paths, tests, and runtime evidence. If a candidate no longer exists when the master reads the target, reject it with that evidence; do not restart the review. Only after a candidate survives falsification may the master choose a disposition, repair boundary, and P0-P3 priority.

Agreement is provenance rather than proof. Keep disproved or unsupported candidates in the rejected or unresolved audit trail instead of silently deleting them. The coordinator validates the four role identities and schemas, verifies that every candidate and open question has exactly one master disposition, rejects any verified finding whose applicable evidence gate did not pass or whose falsification was inconclusive, and independently recomputes the clean gate. There is no version-identity or cross-reviewer target-consistency gate.

## Findings

Present only verified actionable findings supported by code, reproduction, tests, measurement, or strong reachability evidence. Rank them by user impact and likelihood, consolidate sibling symptoms under their shared root cause, preserve which reviewers reported them, and include location, concrete failure or risk, why it matters, evidence or triggering scenario, and a concise repair direction.

Do not invent findings, style preferences, or hypothetical redesigns to appear thorough. An optimality finding must name a viable replacement and explain why it is better under the real constraints.

Report a clean result only when all four specialist lanes and the master completed, every candidate and open question was adjudicated, the impact map has no unexplained difference, no verified finding, advisory, or unresolved actionable candidate remains, no material coverage item is unverified, and every required evidence lane was exercised. A properly evidenced `known_deferred` item does not block clean eligibility but must be disclosed. Phrase the result as “本次即时审查实际读取到的内容和已执行证据范围内，没有受支持的可操作发现。” A blocked lane, missing report, required surface that cannot be inspected, or unresolved material candidate makes the result incomplete rather than clean. Target movement itself neither blocks nor invalidates delivery, and no final drift or SHA check is performed.

## Deliver a review of someone else's PR

When the user explicitly supplied a direct GitHub PR URL, the PR's `author.login` differs from the authenticated `gh` login, and the user did not opt out of posting, the `review` invocation itself authorizes exactly one ordinary GitHub PR comment containing the completed review result. This exception does not apply to a PR owned by the authenticated user, an inferred PR target, `OWNER/REPO#NUMBER` without a direct URL, a branch, commit, range, local review, or an incomplete review. If account or author identity cannot be resolved, do not guess or post; finish the local review and report comment delivery as blocked.

Publish only after all four specialist records and the master result are complete and the coordinator has validated their schemas and recomputed the clean gate. Do not requery or compare the PR head before posting. Do not post provisional findings, malformed or blocked-lane output, unresolved material candidates presented as findings, internal prompts, raw reviewer envelopes, credentials, or chain-of-thought. The comment should be concise and self-contained: give verified findings in priority order or the evidence-bounded clean conclusion, disclose known deferred items and material coverage limits, summarize executed checks, and state that the review is best-effort and does not claim coverage of later changes.

Write the exact Markdown body to a coordinator-created system temporary file and post it with `gh pr comment <url> --body-file <file>` so shell interpolation cannot corrupt code or Markdown. Append a non-rendering marker in the form `<!-- cyh-flow-review:<owner>/<repo>#<number>:<visible-body-sha256> -->`, where the digest covers the final visible Markdown before the marker. Before posting, and again before retrying any command with an uncertain outcome, query the PR's issue comments through `gh` for that marker; reuse the matching comment URL instead of creating a duplicate. After posting, reread the identified comment through `gh`, verify its author and exact body, and report its GitHub URL. Remove only the exact temporary file or directory created for delivery after verification.

## Side-effect boundary

Except for the automatic ordinary-comment delivery above or a separate explicit posting request, review mode does not authorize editing source, applying fixes, committing, pushing, resolving threads, approving, requesting changes, posting comments, or changing PR state. For any explicitly authorized comment, use `gh`, preserve Markdown safely, reread the posted body, and report the URL. If the user later authorizes a bounded repair, switch to `fix`; if they request a persistent Goal that continues until supported findings reach zero, switch to `converge`.

Never merge a PR.
