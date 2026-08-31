# Review mode

Use this mode for a read-only review of local changes, a commit, a branch, or a pull request. The deliverable is verified findings or a clean result, not a patch.

## Resolve the review target

1. Honor a target explicitly named by the user. Otherwise detect local uncommitted work or the branch's real base without assuming `main`.
2. For a GitHub PR, use `gh` to fetch the live base, head SHA, changed files, commits, description, review threads, and checks. Do not review a stale local approximation when the remote head differs.
3. Use an isolated worktree or temporary checkout when the current checkout is dirty, on another branch, or would contaminate validation. Do not disturb the user's active worktree.
4. Include staged, unstaged, and relevant untracked source files for local reviews. Validate that the diff is non-empty before drawing conclusions.
5. Establish the originating requirement, issue, plan, or user intent. If none exists, state that requirement completeness cannot be verified.

## Review passes

Read the full diff, relevant surrounding code, and applicable repository instructions. Check:

- Requirement completeness and scope: missing behavior, partial implementation, wrong interpretation, or unrelated changes.
- Correctness: logic, error paths, state transitions, concurrency, ordering, idempotency, cleanup, and boundary values.
- Security and data boundaries: authentication, authorization, tenant or ownership isolation, input validation, secrets, logging, and destructive behavior.
- Compatibility and contracts: API shapes, schema and migration behavior, callers, legacy data, configuration, localization, and platform differences.
- Project fit: reuse of established abstractions and conventions; avoid generic advice already enforced by formatter or linter.
- Tests and acceptance: whether tests would fail for a broken implementation and which evidence lanes remain uncovered.

Run focused, non-mutating checks when they materially increase confidence. Use an isolated worktree if a command writes caches or generated files. Do not claim CI passed while checks are pending, skipped, or absent.

## Findings

Only report actionable findings supported by code, reproduction, tests, or strong evidence. Rank them by severity and provide:

- Location.
- Concrete failure or risk.
- Why it matters.
- Evidence or triggering scenario.
- A concise direction for fixing it.

Do not invent findings to appear thorough. If no actionable issue remains, say the review is clean and list important unverified areas separately.

## Side-effect boundary

Review mode does not authorize editing source, applying fixes, committing, pushing, resolving threads, approving, posting comments, or changing PR state. If the user explicitly asks to post the review, use `gh`, preserve Markdown safely, re-read the posted body, and report the URL. If the user later authorizes fixes, switch to build mode and read `references/build.md`.

Never merge a PR.
