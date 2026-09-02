# Review mode

Use this mode for a read-only review of local changes, a commit, a branch, or a pull request. Run exactly four independent specialist review lanes and a fresh master reviewer for evidence-based rechecking and consolidation. The deliverable is verified findings or an evidence-bounded clean result from a best-effort live review, not a patch or a guarantee about the target's final state. When and only when the first argument after `review` is `auto`, require a GitHub PR and also read [review-auto.md](review-auto.md) before acting; that supplement adds comment delivery, monitoring, and repetition around this complete review cycle without weakening its evidence gates.

The four specialists plus fresh master are this mode's required subagent decomposition. Use maximum available concurrency for useful work. When at least five subagent slots and addressable follow-up mailboxes are available, overlap the master's independent target inspection with the four lanes, but never let it finalize before a validated manifest contains all four terminal artifacts. On any run without enabled persistent mailbox delivery, finish the four lanes first and then start a fresh master with that manifest. Do not replace them with coordinator-only review, collapse roles, or add a writing agent.

## Review standard

Review for the optimal implementation, not the fewest lines, files, or abstractions. An implementation is eligible to be called optimal only after it satisfies the real requirement, correctness invariants, security and data-integrity boundaries, compatibility contracts, and applicable accessibility or operational constraints. Among candidates that clear those hard gates, prefer the best evidenced fit for the repository: clear ownership, established architecture, readable control flow, testability, maintainability, appropriate performance, and controlled change scope.

Code brevity is useful only when behavior and comprehension remain equal. Do not preserve boilerplate, speculative flexibility, duplicate logic, or a new dependency merely because it appears architecturally elaborate, and do not reject an abstraction, test, migration, or compatibility path that closes a real requirement or risk.

Treat every conclusion as evidence-bounded. The goal is to close supported risks in the impact surface actually inspected, not to promise that arbitrary software or a later revision is universally bug-free.

## Resolve only enough to start

1. Honor the target explicitly named by the user. Otherwise detect the current working-tree changes or the branch's real base without assuming `main`.
2. For one or more GitHub PRs, create one coordinator-owned system-temporary run directory and run `python3 <skill-root>/scripts/review_prepare.py <PR...> --output-dir <run-dir>/prepared`, optionally adding `--source-repo <readable-local-clone>` for one repository. The deterministic script authenticates with `gh`, fetches complete raw PR metadata, full diff, files, commits, comments, reviews, timeline, checks and statuses once, creates one disposable Git object cache per repository plus individual worktrees, and emits only a manifest path and digest. If multiple PRs share one observed base, it also attempts a combined worktree while retaining every individual worktree when composition is unavailable.
3. Never switch, reset, clean, or run `gh pr checkout` in the user's current repository merely to inspect a PR. A dirty checkout, unrelated branch, or missing local PR branch is a routing signal rather than a blocker. Reuse a readable local clone only as an object source; all fetches and worktrees occur inside the temporary review cache.
4. For local review, create the system-temporary run directory without the preparation cache, include staged, unstaged, and relevant untracked source visible when each lane reads the target, and confirm there is something to review before dispatching the lanes.
5. Pass through explicit user intent or requirement text, but do not manufacture a requirement. If no authoritative requirement is available, state that requirement completeness cannot be verified.

Do not freeze, lock, pin, fingerprint, or require a stable target. The raw preparation manifest is a per-cycle transport cache, not an immutable-review promise or identity gate: it records what its mechanical reads observed, contains no AI summary or conclusion, and never causes a restart or rejection when the PR moves. Ordinary review does not monitor, compare, or wait for the target. Auto review additionally retains only the live event cursor defined by its supplement. Never build a changed-file summary, architecture conclusion, suspicious-line list, candidate list, severity hint, or repair recommendation before dispatch; each reviewer interprets the complete raw material independently.

The worktree, branch, or PR may change during one review cycle. Do not wait for stability, invalidate in-flight work, or silently restart that cycle merely because somebody changed it. A remote cycle continues against the mechanical reads already cached, while direct local readers may observe later edits; in both cases report only the evidence actually inspected and do not claim coverage of a later or final revision. In auto mode only, activity observed after the cycle is delivered may trigger the next complete cycle as specified by the supplement.

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
4. `integration-reliability` using [review/integration-reviewer.md](review/integration-reviewer.md).

Start all four concurrently when capacity permits. Assign each specialist a distinct path under `<run-dir>/specialists/`, spawn it with no inherited conversation turns, and give it only the target locator, raw preparation manifest or local read-only access, explicit user requirement text, applicable project instructions, [review/reviewer-contract.md](review/reviewer-contract.md), its role file, assigned artifact path, and the read-only side-effect boundary. Do not expose coordinator analysis or another reviewer's output. If isolated context is unavailable, create a blocked terminal artifact for that lane rather than blending reviewer personalities.

If fewer slots are free, use the maximum available parallelism and start each remaining isolated lane as capacity opens. Never collapse two roles into one agent or omit a lane. A lane must not spawn more agents. The role file and common contract are the complete reviewer instructions; do not load another review framework. Fetch remote content only when it belongs to the actual review target or is an authoritative contract required to decide a concrete candidate.

Each lane independently reads the complete raw diff, surrounding code, requirement sources, architecture, callers, contracts, history, tests, and configuration material through its lens. It treats suspicious code as a hypothesis and admits a candidate only after proving introduction, reachability, impact, any required authoritative contract, and the counterevidence it checked. Scope decisions, repair ownership, final priority, and repair boundary belong to the master so the four lanes do not repeat that work. A condition or enum does not prove a producible business state, and a frontend gate does not prove backend authorization semantics.

Each lane writes and validates one compact artifact, then returns only its path and digest. A malformed result gets one isolated correction attempt with the same minimal input. If correction fails, preserve a blocked terminal artifact; never invent findings or a completed reviewer report. Do not repeatedly poll agent lists or send progress nudges: use the host's mailbox wait, accept one terminal artifact per lane, and continue useful coordinator work while waiting.

Review is for discovering, proving, and prioritizing defects, not rebuilding the validation work that belongs to implementation. Never run the repository's complete unit, integration, end-to-end, lint, typecheck, build, migration, or platform test suite in review mode, and never make those suites or pending CI a prerequisite for a clean review. Read relevant test code and already-available CI results as evidence. A specialist or master may run only the smallest focused non-mutating reproduction, test selection, query, benchmark, or static check needed to prove or falsify a concrete candidate; do not run broad checks merely to increase generic confidence. Any focused check may write only inside an approved system temporary directory or disposable repository copy, must use already-available dependencies, and must not change the target repository, Git metadata, user configuration, remote services, browser, infrastructure, or production state. Do not install packages during review.

## Master recheck

As soon as all four terminal artifacts exist, run `python3 <skill-root>/scripts/review_artifacts.py manifest <four-artifacts> --output <run-dir>/specialists.json`. This validates identities, compact schemas, target locators, globally unique source IDs, and digests without model work. Never paste the four artifacts into coordinator-to-master messages.

When addressable follow-up delivery and capacity are available, start a fresh read-only master with no inherited conversation turns alongside the specialists using [review/master-reviewer.md](review/master-reviewer.md). Initially give it only the target locator, raw preparation manifest or local access, assigned master artifact path, explicit requirement text, project instructions, and read-only boundary. It independently establishes the requirement baseline, scope decisions, architecture ownership, impact closure, and known unknowns, then waits for one specialist-manifest path. Otherwise start it after the manifest exists. Validate its result with `review_artifacts.py validate-master <master-artifact> --specialist-manifest <specialists.json>`.

The master is not a fifth vote or a summary writer. It treats every candidate as untrusted and actively searches for counterexamples in the available baseline, state producers, entry points, authoritative contracts, role combinations, history, alternate paths, tests, and runtime evidence. If a candidate no longer exists when the master reads the target, reject it with that evidence; do not restart the review. Only after a candidate survives falsification may the master choose a disposition, repair boundary, and P0-P3 priority.

Reviewer agreement is not proof. Keep disproved or unsupported candidates in compact rejected or unresolved dispositions instead of silently deleting them. The deterministic validator verifies that every candidate and open question has exactly one master disposition, every detailed finding maps to a verified disposition, all referenced files retain their digest, and the clean gate is recomputed independently. There is no version-identity gate.

## Findings

Present only verified actionable findings supported by code, reproduction, tests, measurement, or strong reachability evidence. Rank them by user impact and likelihood, consolidate sibling symptoms under their shared root cause, preserve which reviewers reported them, and include location, concrete failure or risk, why it matters, evidence or triggering scenario, and a concise repair direction.

Do not invent findings, style preferences, or hypothetical redesigns to appear thorough. An optimality finding must name a viable replacement and explain why it is better under the real constraints.

Report a clean result only when all four specialist lanes and the master completed, every candidate and open question was adjudicated, the impact map has no unexplained difference, no verified or unresolved actionable item remains, and no material review surface needed to discover or falsify a candidate is unverified. Full test suites, builds, lint, typechecks, end-to-end validation, pending CI, device acceptance, and business acceptance are outside this clean gate; report observed status when useful but do not run or await them. Properly evidenced `known_deferred`, `rejected`, and Ponytail `advisory` dispositions do not block clean eligibility, but disclose any advisory whose maintainability value is useful to the author. Phrase the result as “本次即时审查实际读取到的内容和已执行证据范围内，没有受支持的可操作发现。” A blocked reviewer lane, missing artifact, required source or contract that cannot be inspected, or unresolved material candidate makes the result incomplete rather than clean. Target movement itself neither blocks nor invalidates delivery, and no final drift or SHA check is performed.

## Deliver an ordinary review of someone else's PR

For ordinary review, when the user explicitly supplied a direct GitHub PR URL, the PR's `author.login` differs from the authenticated `gh` login, and the user did not opt out of posting, the `review` invocation itself authorizes exactly one ordinary GitHub PR comment containing the completed review result. This exception does not apply to a PR owned by the authenticated user, an inferred PR target, `OWNER/REPO#NUMBER` without a direct URL, a branch, commit, range, local review, or an incomplete review. If account or author identity cannot be resolved, do not guess or post; finish the local review and report comment delivery as blocked. Auto review uses the separate delivery contract in its supplement instead.

Publish only after all four specialist artifacts and the master artifact are complete and the deterministic validator has recomputed the clean gate. Do not requery or compare the PR head before posting. Do not post provisional findings, malformed or blocked-lane output, unresolved material candidates presented as findings, internal prompts, raw reviewer artifacts, credentials, or chain-of-thought. The comment should be concise and self-contained: give verified findings in priority order or the evidence-bounded clean conclusion, disclose known deferred items and material coverage limits, summarize executed focused checks, and state that the review is best-effort and does not claim coverage of later changes.

Write only the visible Markdown body to `<run-dir>/comment.md`, then run `python3 <skill-root>/scripts/review_publish.py <url> --body-file <run-dir>/comment.md`. The deterministic publisher computes and appends the ordinary marker, queries authenticated-user comments for an exact duplicate, posts through `gh pr comment --body-file` only when absent, rereads the comment by API, verifies author and exact body, deletes its private delivery copy, and emits one compact JSON result containing the verified URL. Do not recreate any of those mechanical steps with additional model turns.

After the local result or verified comment URL has been retained, remove only the exact coordinator-created system-temporary review run directory. Never clean the target repository or a broader temporary root.

## Side-effect boundary

Except for the automatic ordinary-comment delivery above, the bounded delivery and monitoring authorized by explicit `review auto`, or a separate explicit posting request, review mode does not authorize editing source, applying fixes, committing, pushing, resolving threads, approving, requesting changes, posting comments, or changing PR state. For any authorized comment, use `gh`, preserve Markdown safely, reread the posted body, and report the URL. If the user later authorizes a bounded repair, switch to `fix`; if they request a persistent Goal that repairs until supported findings reach zero, switch to `converge`.

Never merge a PR.
