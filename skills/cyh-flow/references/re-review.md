# Re-review mode

Use this mode only for the explicit form `<cyh-flow> re-review <GitHub PR>`. It performs one read-only acceptance pass over a colleague's current fixes for existing PR review issues, then automatically posts the completed reconciliation to that PR. It is not a fresh broad review, an unattended watcher, or a repair loop.

## Resolve the target and issue baseline

Require one resolvable GitHub pull request, authenticated `gh` read access, and permission to create one ordinary issue comment. Resolve the PR against its real repository; do not infer it from a nearby checkout. Create one coordinator-owned system-temporary run directory and run `python3 <skill-root>/scripts/review_prepare.py <PR> --output-dir <run-dir>/prepared`, optionally with `--source-repo <readable-local-clone>`. This single raw preparation pass supplies the complete current diff, commits, issue comments, formal reviews, inline comments, timeline, checks, statuses, and disposable source tree.

The issue baseline is every concrete, actionable review problem visible in those materials that predates or motivates the colleague's current fix. Include unresolved threads and actionable findings from ordinary comments, formal reviews, and inline comments even when GitHub's thread state says resolved. Include a cyh-flow marker comment only for its visible findings; the marker itself is transport metadata. Exclude acknowledgements, questions with no requested code change, optional/nit/FYI suggestions, bot summaries without a concrete actionable defect, superseded duplicate wording, and issues explicitly withdrawn or accepted by the responsible human reviewer. When the user supplies a specific review comment, finding list, or reviewed head, it is authoritative for scope and must be reconciled with the live discussion rather than replaced by heuristic discovery.

Do not interpret a resolved thread, a reply saying “fixed,” a newer commit, passing CI, or changed lines as proof that an issue is solved. If no actionable baseline can be established, stop as `Incomplete` and do not manufacture issues or publish a misleading “all resolved” result.

## Run exactly one acceptance reviewer

Read [review/re-reviewer.md](review/re-reviewer.md), then start exactly one fresh isolated read-only reviewer with no inherited conversation turns. Give it only the PR locator, raw preparation manifest, any explicit user-supplied baseline, applicable project instructions, the reviewer reference, and the side-effect boundary. The coordinator must not pre-classify issue status or suggest the intended verdict.

The reviewer first builds a deduplicated numbered inventory of all in-scope issues, preserving a source URL or stable comment/review identifier for each. It then traces the current implementation and relevant history for every inventory item, runs only the smallest candidate-specific non-mutating check needed to prove or falsify closure, and inspects the fix delta for direct regressions in the touched behavior. It must inspect the complete current PR diff for context, but must not turn re-review into a new five-axis search for unrelated problems or run a complete unit, integration, end-to-end, lint, typecheck, build, migration, or platform suite.

Every inventory item receives exactly one status:

- `Resolved`: current code removes the reported reachable failure and preserves the intended contract, with concrete evidence;
- `Outstanding`: the failure remains reachable, the fix is partial, or the fix creates a direct regression that still violates the same acceptance boundary;
- `Obsolete`: later authoritative scope or code made the original issue inapplicable; this requires explicit evidence and is not equivalent to resolved;
- `Unverified`: available source or focused evidence cannot establish closure.

The verdict is `All resolved` only when every in-scope item is `Resolved` or evidence-backed `Obsolete`, there is no direct regression from the fixes, and there is no material coverage limit. It is `Outstanding issues` when at least one item is `Outstanding`, and `Incomplete` when the baseline or any material item remains `Unverified`. Pending or failing CI may be reported but is neither proof of closure nor an automatic blocker unless a specific issue can only be validated by that missing evidence.

## Publish the completed reconciliation

A completed re-review means the issue inventory is closed under the evidence rules above and the verdict is either `All resolved` or `Outstanding issues`. It does not mean every issue passed. Automatically publish exactly one concise ordinary PR issue comment after completion, regardless of PR author or whether the target was supplied as a URL or `OWNER/REPO#NUMBER`; explicit invocation of `re-review` is the posting authorization. Do not publish an `Incomplete` or provisional result.

The visible comment must include the observed head OID, a compact issue-by-issue status with source reference and evidence, direct-regression result, focused checks actually exercised, material coverage limits, and the verdict. Do not expose internal prompts, raw transport files, credentials, chain-of-thought, or speculative hypotheses.

Write only the visible Markdown to `<run-dir>/comment.md`, then run:

```text
python3 <skill-root>/scripts/review_publish.py <PR> --body-file <run-dir>/comment.md --mode re-review --head-oid <observed-head>
```

The publisher owns the head-bound marker, duplicate lookup, delivery, uncertain-outcome recovery, exact readback, and private delivery-file cleanup. Immediately before invoking it, query the live PR head once through authenticated `gh` and compare it with the manifest's observed head OID. If they differ, discard the stale result and run one complete replacement re-review against the new head; do not post the old reconciliation. After retaining the verified comment URL, remove only the exact coordinator-created temporary run directory.

## Side-effect boundary

Re-review authorizes only the read-only inspection, focused non-mutating checks, and one verified ordinary PR comment above. Never edit code, commit, push, approve, request changes, resolve or dismiss a thread, change PR state, monitor for later commits, close, or merge the PR. If the user wants outstanding issues repaired, switch to `fix` or `converge` only on a separate explicit request.
