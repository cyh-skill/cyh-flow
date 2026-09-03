# Deep review mode

Use this mode only for the exact form `<cyh-flow> review deep <target>`. Run exactly four independent specialist review lanes and a fresh master reviewer for evidence-based rechecking and consolidation. The deliverable is verified findings or an evidence-bounded clean result from a best-effort live review, not a patch or a guarantee about the target's final state. Deep review is one-shot and does not imply monitoring; `review auto` uses the ordinary single-reviewer protocol instead.

The required topology is exactly four isolated specialists plus one fresh master. Use maximum available concurrency for useful work. With at least five slots and addressable follow-up mailboxes, overlap the master's independent target inspection with the four lanes and finalize after the validated four-artifact manifest arrives. For runs without enabled persistent mailbox delivery, finish the specialists first and then start the master from that manifest. The coordinator orchestrates this topology and does not act as a reviewer or writer.

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

The raw preparation manifest is a transport cache of mechanical reads, with no AI summary, conclusion, target lock, or stability promise. Deep review is a one-shot inspection of that observed material. Dispatch each reviewer with the complete raw inputs so it independently derives changed behavior, architecture, candidates, severity evidence, and impact.

The worktree, branch, or PR may change during review. A remote run continues against its cached mechanical reads, while direct local readers may observe later edits; the report identifies the evidence actually inspected and treats later or final revisions as outside coverage.

## Build the impact closure

Each specialist starts from the changed hunks and independently traces every material surface for its lens; the master builds and closes the final impact map:

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

Start all four concurrently when capacity permits. Assign each specialist a distinct path under `<run-dir>/specialists/`, spawn it with no inherited conversation turns, and give it exactly the target locator, raw preparation manifest or local read-only access, explicit requirement text, applicable project instructions, [review/reviewer-contract.md](review/reviewer-contract.md), its role file, assigned artifact path, and the read-only side-effect boundary. Each lane receives independent raw evidence; unavailable isolation produces a blocked terminal artifact.

If fewer slots are free, use the maximum available parallelism and start each remaining isolated lane as capacity opens. Each role keeps one dedicated agent and performs no further delegation. The role file and common contract are its complete reviewer instructions. Remote content is limited to the actual review target and authoritative contracts needed for concrete candidates.

Each lane independently reads the complete raw diff, surrounding code, requirement sources, architecture, callers, contracts, history, tests, and configuration material through its lens. It treats suspicious code as a hypothesis and admits a candidate only after proving introduction, reachability, impact, any required authoritative contract, and the counterevidence it checked. Scope decisions, repair ownership, final priority, and repair boundary belong to the master so the four lanes do not repeat that work. A condition or enum does not prove a producible business state, and a frontend gate does not prove backend authorization semantics.

Each lane writes and validates one compact artifact, then returns only its path and digest. A malformed result gets one isolated correction attempt with the same minimal input. If correction fails, preserve a blocked terminal artifact; never invent findings or a completed reviewer report. Do not repeatedly poll agent lists or send progress nudges: use the host's mailbox wait, accept one terminal artifact per lane, and continue useful coordinator work while waiting.

Review discovers, proves, and prioritizes defects through complete source tracing, relevant test code, available CI evidence, and the smallest focused non-mutating reproduction, test selection, query, benchmark, or static check needed for a concrete candidate. Focused checks use already-available dependencies and write only inside an approved system temporary directory or disposable repository copy. Never run the repository's complete unit, integration, end-to-end, lint, typecheck, build, migration, or platform test suite in review mode. Package installation, CI waiting, and mutation of the target repository, Git metadata, user configuration, remote services, browser, infrastructure, or production state also remain outside review mode.

## Master recheck

As soon as all four terminal artifacts exist, run `python3 <skill-root>/scripts/review_artifacts.py manifest <four-artifacts> --output <run-dir>/specialists.json`. This validates identities, compact schemas, target locators, globally unique source IDs, and digests without model work. Never paste the four artifacts into coordinator-to-master messages.

When addressable follow-up delivery and capacity are available, start a fresh read-only master with no inherited conversation turns alongside the specialists using [review/master-reviewer.md](review/master-reviewer.md). Initially give it only the target locator, raw preparation manifest or local access, assigned master artifact path, explicit requirement text, project instructions, and read-only boundary. It independently establishes the requirement baseline, scope decisions, architecture ownership, impact closure, and known unknowns, then waits for one specialist-manifest path. Otherwise start it after the manifest exists. Validate its result with `review_artifacts.py validate-master <master-artifact> --specialist-manifest <specialists.json>`.

The master is not a fifth vote or a summary writer. It treats every candidate as untrusted and actively searches for counterexamples in the available baseline, state producers, entry points, authoritative contracts, role combinations, history, alternate paths, tests, and runtime evidence. If a candidate no longer exists when the master reads the target, reject it with that evidence; do not restart the review. Only after a candidate survives falsification may the master choose a disposition, repair boundary, and P0-P3 priority.

Reviewer agreement is not proof. Keep disproved or unsupported candidates in compact rejected or unresolved dispositions instead of silently deleting them. The deterministic validator verifies that every candidate and open question has exactly one master disposition, every detailed finding maps to a verified disposition, all referenced files retain their digest, and the clean gate is recomputed independently. There is no version-identity gate.

## Findings

Present only verified actionable findings supported by code, reproduction, tests, measurement, or strong reachability evidence. Rank them by user impact and likelihood, consolidate sibling symptoms under their shared root cause, preserve which reviewers reported them, and include location, concrete failure or risk, why it matters, evidence or triggering scenario, and a concise repair direction.

Do not invent findings, style preferences, or hypothetical redesigns to appear thorough. An optimality finding must name a viable replacement and explain why it is better under the real constraints.

Report a clean result only when all four specialist lanes and the master completed, every candidate and open question was adjudicated, the impact map has no unexplained difference, no verified or unresolved actionable item remains, and no material review surface needed to discover or falsify a candidate is unverified. Full test suites, builds, lint, typechecks, end-to-end validation, pending CI, device acceptance, and business acceptance are outside this clean gate; report observed status when useful but do not run or await them. Properly evidenced `known_deferred`, `rejected`, and Ponytail `advisory` dispositions do not block clean eligibility, but disclose any advisory whose maintainability value is useful to the author. Phrase the result as “本次即时审查实际读取到的内容和已执行证据范围内，没有受支持的可操作发现。” A blocked reviewer lane, missing artifact, required source or contract that cannot be inspected, or unresolved material candidate makes the result incomplete rather than clean. Target movement itself neither blocks nor invalidates delivery, and no final drift or SHA check is performed.

## Deliver a deep review of someone else's PR

When the user explicitly supplied a direct GitHub PR URL, the PR's `author.login` differs from the authenticated `gh` login, and the user did not opt out of posting, the `review deep` invocation authorizes exactly one ordinary GitHub PR comment containing the completed deep-review result. This exception does not apply to a PR owned by the authenticated user, an inferred PR target, `OWNER/REPO#NUMBER` without a direct URL, a branch, commit, range, local review, or an incomplete review. If account or author identity cannot be resolved, do not guess or post; finish the local review and report comment delivery as blocked.

Publish only after all four specialist artifacts and the master artifact are complete and the deterministic validator has recomputed the clean gate. Do not requery or compare the PR head before posting. Do not post provisional findings, malformed or blocked-lane output, unresolved material candidates presented as findings, internal prompts, raw reviewer artifacts, credentials, or chain-of-thought. The comment should be concise and self-contained: give verified findings in priority order or the evidence-bounded clean conclusion, disclose known deferred items and material coverage limits, summarize executed focused checks, and state that the review is best-effort and does not claim coverage of later changes.

Write only the visible Markdown body to `<run-dir>/comment.md`, then run `python3 <skill-root>/scripts/review_publish.py <url> --body-file <run-dir>/comment.md`. The deterministic publisher computes and appends the ordinary marker, queries authenticated-user comments for an exact duplicate, posts through `gh pr comment --body-file` only when absent, rereads the comment by API, verifies author and exact body, deletes its private delivery copy, and emits one compact JSON result containing the verified URL. Do not recreate any of those mechanical steps with additional model turns.

After the local result or verified comment URL has been retained, remove only the exact coordinator-created system-temporary review run directory. Never clean the target repository or a broader temporary root.

## Side-effect boundary

Except for the automatic comment delivery above or a separate explicit posting request, deep review does not authorize editing source, applying fixes, committing, pushing, resolving threads, approving, requesting changes, posting comments, or changing PR state. For any authorized comment, use `gh`, preserve Markdown safely, reread the posted body, and report the URL. If the user later authorizes a bounded repair, switch to `fix`; if they request a persistent Goal that repairs until supported findings reach zero, switch to `converge`.

Never merge a PR.
