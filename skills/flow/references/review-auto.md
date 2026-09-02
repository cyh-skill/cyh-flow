# Review auto supplement

Use this supplement only for the exact form `<flow> review auto <GitHub PR>`. It turns the ordinary review protocol into an unattended, event-driven loop. It does not change the reviewers, evidence standard, or read-only code boundary.

## Preconditions and Goal

Require one resolvable GitHub pull request, authenticated `gh` read access, permission to create ordinary issue comments on that PR, Python 3, and a host execution facility that can keep the Skill's [watcher script](../scripts/review_watch.py) running and resume when it exits. Resolve a PR number against the real repository rather than assuming the current checkout. If the target is not a GitHub PR or a required capability is unavailable, report the workflow as blocked; do not silently fall back to one-shot review or claim that monitoring remains active.

Establish one Goal whose completion gate is: the latest completed review cycle is clean and no relevant event arrived before the final live recheck, or the user explicitly said to end or stop this auto review. In Codex, use the native Goal API when available. In Claude Code, use an already user-activated matching `/goal` loop when present; otherwise keep the current run alive with the host's wait mechanism. Never claim background persistence after the host session or execution loop has ended. A user-requested stop completes the Goal as `stopped by user`, not as a clean review.

Do not create a repository ledger, immutable target contract, or target lock. Each ordinary cycle may create the raw transport cache defined by the base review protocol; it is disposable, contains no AI interpretation, and is never used as a stability gate. Give the watcher a separate coordinator-created system-temporary state file; it stores only hashes and GitHub event identifiers with mode `0600`, never source code or full comment bodies. If that cursor is lost, reconstruct it from the live PR and the idempotency markers already posted rather than writing into the target repository.

## Review and delivery cycle

1. Before reading the PR for the first cycle, launch the watcher as a long-running tool process, wait only for its single `ready` JSON record, and retain the process handle. It captures the event baseline before AI review begins, so activity during review is not missed.
2. Run one entire ordinary review cycle, beginning with one deterministic raw preparation pass and continuing through all four specialist artifacts, their validated manifest, the fresh master's independent adjudication, and deterministic clean-gate validation. Changes during the cycle do not invalidate or restart it.
3. If the cycle is incomplete because a required lane, surface, or material candidate is unresolved, do not present it as clean and do not publish speculative findings. Keep the Goal incomplete, retry recoverable failures with bounded backoff, and report a persistent blocker according to the host Goal rules.
4. Publish the completed cycle as one concise ordinary PR issue comment through authenticated `gh`: verified findings in priority order when any exist, otherwise the evidence-bounded clean conclusion. Include the evidence actually exercised, material coverage limits, and the fact that this was a live best-effort cycle. Never Approve, Request changes, submit a formal review state, resolve a thread, edit code, push, close, or merge the PR.
5. Write only the visible Markdown body to the current cycle's system-temporary `comment.md`, then run `python3 <skill-root>/scripts/review_publish.py <target> --body-file <comment.md> --mode auto --head-oid <cycle-observed-head>`. The script owns marker construction, duplicate lookup, `gh pr comment`, uncertain-outcome recovery, exact author/body readback, and private delivery-file cleanup; retain its single verified comment URL and do not reproduce those steps in model turns.
6. Check the watcher process output after delivery rather than issuing another AI-driven GitHub query. If it reported `changed`, immediately start a replacement watcher with the same temporary cursor file, then coalesce the event and begin another cycle against whatever content is live now. If it remains silent, a clean cycle may terminate the exact watcher and complete the Goal; a cycle with verified findings leaves the watcher running and suspends AI work until it reports an event.

## Monitor live PR activity

Run the deterministic watcher from the installed Skill root, with a cursor path inside a coordinator-created system temporary directory:

```text
python3 <skill-root>/scripts/review_watch.py <PR> --state-file <system-temp>/cursor.json --interval 30
```

The script owns every recurring GitHub query, cursor comparison, retry backoff, sleep, and self-comment filter. It does not poll Checks because CI completion is not a review gate. The Agent must not reproduce those polls with model turns, shell snippets, or scheduled prompts while this process is alive; if the host periodically yields the long-running process, resume it with the longest safe wait and do not re-read GitHub from the Agent.

On a new cursor, the script emits one `ready` record and keeps running. While nothing changes it produces no output: GitHub querying and comparison consume no model tokens, although a host that periodically returns long-running process control may still incur a small handle-resume cost. It writes the latest cursor atomically after every query. On relevant mechanical activity it emits one `changed` record containing event kinds and identifiers, then exits successfully; after repeated GitHub failures it emits one `blocked` record and exits nonzero. Do not ask the model to semantically classify a comment before the script wakes it.

At each poll, query enough live GitHub state to detect:

- a changed head OID or new commit;
- a new, edited, or deleted human issue comment, review, or inline review comment;
- a review-thread resolution change, PR body or title change, and a requested-reviewer or scope change when it may alter the requirement baseline;
- PR state changes that make continued review impossible.

The cursor contains event IDs and content digests, the last observed head OID, and a PR-state digest. It exists only to notice activity. Do not use it to pin the next cycle, reject concurrent work, or require all reviewers to see the same revision. The script ignores bot comments and the authenticated account's own auto-review marker comments so they cannot trigger a loop.

A head change always starts another complete review cycle. Any new, edited, or deleted human discussion wakes the Agent; inspect only that event first, then start another complete cycle when it may change requirements, scope, implementation evidence, an existing finding, or a claim that a finding was fixed or intentionally deferred. An irrelevant acknowledgement may restart the watcher without a full review. Coalesce a burst of events into one cycle and review the current live PR rather than replaying every intermediate revision. If an event arrives during a new cycle, finish that cycle and handle the event at its delivery recheck.

Do not publish provisional replies while waiting. Do not repeat an identical result for the same observed head and visible body; the marker is the idempotency authority. A materially new head or result may receive a new cycle comment so PR participants can see what was re-reviewed.

## Stop and blocked states

There are only two successful exits:

- the most recent complete cycle passes the ordinary clean gate and its immediate live recheck finds no unprocessed relevant event; or
- the user explicitly tells this auto review to end or stop.

Findings, waiting without new activity, a temporarily failing GitHub query, and an incomplete review cycle are not completion. Keep the watcher running or retry internally while the execution loop remains available. Pending or failing CI may be disclosed but does not keep review auto alive by itself. If access is revoked, the PR is deleted or externally closed or merged, the watcher or host loop ends unexpectedly, or another persistent condition makes monitoring impossible, preserve the Goal as incomplete and report the exact blocker; never relabel it as clean. A Skill cannot promise cross-session background work merely by starting this child process: if the host cannot retain it, use an explicitly configured external scheduler or report blocked rather than falling back to repeated AI polling. Never merge a PR.
