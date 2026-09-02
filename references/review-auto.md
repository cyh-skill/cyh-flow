# Review auto supplement

Use this supplement only for the exact form `<cyh-flow> review auto <GitHub PR>`. It turns the ordinary review protocol into an unattended, event-driven loop. It does not change the reviewers, evidence standard, or read-only code boundary.

## Preconditions and Goal

Require one resolvable GitHub pull request, authenticated `gh` read access, permission to create ordinary issue comments on that PR, and a host execution loop capable of waiting and resuming. Resolve a PR number against the real repository rather than assuming the current checkout. If the target is not a GitHub PR or a required capability is unavailable, report the workflow as blocked; do not silently fall back to one-shot review or claim that monitoring remains active.

Establish one Goal whose completion gate is: the latest completed review cycle is clean and no relevant event arrived before the final live recheck, or the user explicitly said to end or stop this auto review. In Codex, use the native Goal API when available. In Claude Code, use an already user-activated matching `/goal` loop when present; otherwise keep the current run alive with the host's wait mechanism. Never claim background persistence after the host session or execution loop has ended. A user-requested stop completes the Goal as `stopped by user`, not as a clean review.

Do not create a repository ledger, immutable snapshot, target lock, or shared pre-review packet. Keep only a lightweight event cursor in host/session state. If the host loses that cursor, reconstruct it from the live PR and the idempotency markers already posted rather than writing into the target repository.

## Review and delivery cycle

1. Read the current live PR metadata and conversation, then run one entire ordinary review cycle: all four specialist lanes, fresh master, schema validation, candidate adjudication, impact closure, and coordinator clean-gate recomputation. Changes during the cycle do not invalidate or restart it.
2. If the cycle is incomplete because a required lane, surface, or material candidate is unresolved, do not present it as clean and do not publish speculative findings. Keep the Goal incomplete, retry recoverable failures with bounded backoff, and report a persistent blocker according to the host Goal rules.
3. Publish the completed cycle as one concise ordinary PR issue comment through authenticated `gh`: verified findings in priority order when any exist, otherwise the evidence-bounded clean conclusion. Include the evidence actually exercised, material coverage limits, and the fact that this was a live best-effort cycle. Never Approve, Request changes, submit a formal review state, resolve a thread, edit code, push, close, or merge the PR.
4. Write the exact Markdown body to a coordinator-created system temporary file and use `gh pr comment <target> --body-file <file>`. Append `<!-- cyh-flow-review-auto:<owner>/<repo>#<number>:<head-oid>:<visible-body-sha256> -->`, with the digest covering the visible body. Before posting and before retrying an uncertain result, query existing issue comments for that marker and reuse its URL. After posting, reread the comment, verify its author and exact body, report or retain its URL, and remove only the exact temporary path created for delivery.
5. Immediately reread the live event sources after delivery. If a relevant event arrived during publication or the clean cycle's final recheck, do not complete; coalesce the observed activity and begin another cycle against whatever content is live now. Otherwise a clean cycle completes the Goal. A cycle with verified findings enters monitoring.

## Monitor live PR activity

Use the host's recurring monitor or bounded wait facility rather than a tight shell loop. A roughly 30-second default poll is appropriate when no event notification exists; back off on GitHub rate limiting and resume without declaring success. Keep user-visible progress alive at the host's normal interval.

At each poll, query enough live GitHub state to detect:

- a changed head OID or new commit;
- a new, edited, or deleted human issue comment, review, or inline review comment;
- a review-thread resolution change, PR body or title change, and a requested-reviewer or scope change when it may alter the requirement baseline;
- a check-state change when a prior cycle depended on that check or treated it as missing coverage;
- PR state changes that make continued review impossible.

The cursor may contain event IDs, update timestamps or body digests, the last observed head OID, and the authenticated account identity. It exists only to notice activity. Do not use it to pin the next cycle, reject concurrent work, or require all reviewers to see the same revision. Ignore the workflow's own marker comments so they cannot trigger a loop.

A head change always starts another complete review cycle. Inspect each new or edited human discussion event; start another complete cycle when it may change requirements, scope, implementation evidence, an existing finding, or a claim that a finding was fixed or intentionally deferred. Coalesce a burst of events into one cycle and review the current live PR rather than replaying every intermediate revision. Irrelevant acknowledgements or bot noise advance the cursor without consuming a full review. If an event arrives during a new cycle, finish that cycle and handle the event at its delivery recheck.

Do not publish provisional replies while waiting. Do not repeat an identical result for the same observed head and visible body; the marker is the idempotency authority. A materially new head or result may receive a new cycle comment so PR participants can see what was re-reviewed.

## Stop and blocked states

There are only two successful exits:

- the most recent complete cycle passes the ordinary clean gate and its immediate live recheck finds no unprocessed relevant event; or
- the user explicitly tells this auto review to end or stop.

Findings, waiting without new activity, a temporarily failing GitHub query, pending checks needed by the evidence gate, and an incomplete cycle are not completion. Keep waiting or retrying while the execution loop remains available. If access is revoked, the PR is deleted or externally closed or merged, the host loop ends, or another persistent condition makes monitoring impossible, preserve the Goal as incomplete and report the exact blocker; never relabel it as clean. Never merge a PR.
