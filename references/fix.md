# Fix mode

Use this mode for an explicit, persistent review-repair objective: establish the current defects, repair supported findings, challenge the result with independent adversarial reviewers, and repeat until the defined completion gate is satisfied. Invoking `fix` authorizes scoped local file edits and read-only subagent review; it does not authorize external delivery or unrelated cleanup.

## Establish the Goal contract

Before editing, resolve the exact repository, target behavior, source of truth, scope, non-goals, starting revision or diff, and the evidence lanes needed for acceptance. Then use the available Codex Goal mechanism to create one durable objective with one verifiable stopping condition. Do not merely say that a Goal exists when no Goal was created, do not assign a token budget unless the user explicitly requested one, and do not replace an unfinished Goal with a different objective. Continue an existing Goal only when it is the same objective; if it conflicts, stop and ask the user to resolve the Goal state.

Define the stopping condition in evidence-bounded terms. “Bug zero” means zero unresolved, reproducible, in-scope findings supported by the current review and validation evidence; it is not a claim that the software is universally defect-free. Build a risk-and-evidence matrix covering source, automated tests, CI, runtime, UI/device, security, performance, external contracts, and business acceptance as applicable. Any lane or lens explicitly named by the user is required; exclusions need a concrete, reviewable reason. If a required lane cannot be exercised, it blocks Goal completion unless the user explicitly revises the Goal contract.

The Goal must preserve the ordinary authorization boundary. It may continue review, local repair, and local validation across turns, but it may not commit, push, create or edit a PR, post comments, deploy, write any external environment or account, run a scan or load test with external impact, or message people unless the user separately requests that exact action. Local repair does not mean a remote PR or branch was updated; delivery state must remain explicit.

## Baseline review before repair

Perform a fresh review before the first edit. Read the full relevant diff and surrounding implementation, not only the named failing line, then trace callers, state transitions, error paths, contracts, tests, platform variants, and operational boundaries far enough to identify root causes and likely sibling failures. Enumerate the expected affected surfaces independently of the diff and investigate the difference between that set and the surfaces intentionally changed, intentionally preserved with a reason, and actually validated.

Maintain a compact finding ledger containing a stable ID, lens, severity, location, triggering scenario, evidence, validation method, and status. Add every concrete in-scope defect backed by code, reproduction, a failing check, or strong reachability evidence, including supported defects that need a product decision, external change, or new permission and therefore remain blocked rather than locally fixable. Do not treat preferences, speculative hardening, or formatter-level style as bugs, and do not patch a reviewer claim until the main agent has reproduced or independently confirmed it.

The original reported failure must itself be accounted for: reproduce it on the starting state when safe, tie it to trustworthy logs or event evidence, or create a regression test or causal proof that fails before the repair and passes after it. An empty ledger is not completion when the initiating failure was never explained or validly disposed of.

## First repair

Repair the validated baseline findings in dependency order, choosing the optimal coherent root-cause correction for the real behavior and repository constraints instead of optimizing for line count or diff size. Prefer a shared ownership boundary over repeated symptom patches when consumer contracts align, but keep distinct behavior separate when they do not. Add or strengthen regression tests where the project normally tests the behavior or where a recurring defect needs a durable guard. Run focused checks after each coherent change, then broader relevant checks before adversarial review. Keep pre-existing failures separate from failures introduced by the repair.

Use one mutually exclusive writer for the entire Goal. Only the main agent or one explicitly designated writer edits the working tree, and writer ownership must never overlap. Parallel agents in this mode are reviewers, explorers, or test/log analysts and must remain read-only so their work cannot conflict or contaminate the review target.

## Adversarial review

After every repair round, enter a review barrier: stop the writer and identify an immutable target with base SHA, head SHA, merge-base, and a hash of the complete local diff and intentional untracked deliverables, or an equivalent isolated snapshot. A mutable shared worktree or a remote PR head that excludes local repairs is not a frozen target. If the target is a live PR, re-read its base, head, and merge-base before each round and before completion; drift in any of them invalidates results tied to the old target.

Delegate independent read-only reviews of that snapshot to multiple subagents. This `fix` invocation explicitly requests that delegation. Use a fresh agent instance with minimal context for every lens and round; give it the requirement, immutable target identifier, applicable repository instructions, and one bounded lens, but not the finding ledger, prior conclusions, suspected bugs, another reviewer's result, or a reused thread anchored on an earlier round. Its job is to falsify the claim that the repair is complete, not to approve it.

Choose lenses according to the change and cover every applicable risk surface across the reviewer set, including:

- requirement completeness, core correctness, state transitions, error handling, concurrency, ordering, cleanup, and boundary values;
- authentication, authorization, tenant or ownership isolation, data validation, secrets, logging, and destructive behavior;
- API, schema, migration, configuration, caller, legacy-data, localization, accessibility, browser, device, and platform compatibility;
- optimal implementation and ownership boundaries, including repository fit, justified reuse, clarity, maintainability, testability, avoidable duplication, speculative abstraction, unnecessary dependencies, and change-scope churn;
- regression-test quality, flakiness, performance, resource lifecycle, observability, recovery, and real user-flow acceptance.

Spawn at least two distinct reviewer agents, run them concurrently when runtime capacity permits and sequentially otherwise, split broad scopes across additional reviewers only when the lenses are genuinely independent, and wait for every requested result. Each reviewer must return the immutable target identifier, paths and scenarios examined, read-only checks performed, unverified areas, and either no supported finding or a concise finding with location, trigger, impact, evidence, and a fix direction. Reviewers must inspect relevant full paths and cross-file behavior rather than matching wording or reviewing only the latest hunk.

Reviewer commands must be genuinely read-only or run in an isolated disposable worktree or environment. Tests, generators, services, databases, and log tools that can persist changes do not count as read-only merely because the reviewer was told not to edit. Verify the shared target is unchanged when the review barrier ends.

If the runtime cannot provide two distinct subagents, do not present repeated self-review as independent adversarial review. Report the missing capability and keep the Goal incomplete unless the user explicitly accepts a single-agent fallback with reduced confidence.

The main agent inspects every result, reproduces or verifies each claim, merges duplicates by root cause, rejects unsupported findings with a reason, and updates the ledger. A clean reviewer result closes only the lens it actually examined.

An unverified area inside a required lane or lens prevents that lens from closing and blocks Goal completion. It may be excluded only with a concrete reason that is consistent with the Goal contract; silently treating it as non-required is not allowed.

## Repeat the repair loop

While the ledger contains any supported open finding:

1. Repair the validated root cause with the single-writer rule.
2. Run the targeted regression check and the broader checks affected by the change.
3. Start a fresh adversarial review against the latest complete target; do not reuse a previous clean conclusion after code changed.
4. Consolidate results and continue until the latest full round produces no new supported finding.

Do not impose an arbitrary round limit while the loop is making measurable progress, measured by reduced open-finding count or severity, closed causal gaps, stronger regression evidence, and no oscillation or unapproved scope growth. If a round has no net progress, the same class of issue returns, or fixes alternate between regressions, stop applying local patches, expand the root-cause trace, add a regression test, and change strategy. If the revised strategy still cannot progress without a product decision, unavailable environment, new permission, destructive action, or external mutation, do not loop forever, guess, or weaken the stopping condition; report the exact blocker and keep the Goal incomplete under the host's Goal lifecycle rules.

## Completion gate

Mark the Goal complete only when all of the following are true:

- the finding ledger contains zero supported open findings;
- the original reported failure has reproducible before/after evidence, a passing regression test that failed on the starting state, or another documented causal resolution accepted by the Goal contract;
- the latest full adversarial round covers every applicable lens and all reviewers report no new supported finding after the final code change;
- required focused and broader checks pass, with unrelated baseline failures explicitly separated;
- the final diff has no unintended files, generated noise, credentials, debug residue, or unreviewed behavior;
- every acceptance lane declared necessary in the Goal contract has evidence, including real UI/device/runtime behavior when the requirement depends on it;
- all requested reviewer agents have finished and their results were inspected.

Report completion as “zero supported findings within the reviewed scope and executed evidence lanes,” followed by the rounds performed, fixes made, checks run, immutable target revision, local-versus-remote delivery state, and any justified non-required lane that remains unverified. Never shorten the Goal's success condition merely because the work is taking longer than expected.
