# Review mode

Use this mode for the ordinary, token-conscious review of local changes, a commit, a branch, or a pull request. Run one five-axis code-quality reviewer, not the four specialist lanes or fresh master from deep review. The result is a read-only, evidence-bounded review of the content actually inspected, not a patch, GitHub approval, or guarantee about a later revision.

The exact first argument selects the extension: `review auto` requires a GitHub PR and also reads [review-auto.md](review-auto.md), while `review deep` uses [review-deep.md](review-deep.md). Ordinary review stays on this single-reviewer protocol.

## Resolve the target

1. Honor the target explicitly named by the user. Otherwise detect current working-tree changes or the branch's real base without assuming `main`.
2. For one or more GitHub PRs, create one coordinator-owned system-temporary run directory and run `python3 <skill-root>/scripts/review_prepare.py <PR...> --output-dir <run-dir>/prepared`, optionally adding `--source-repo <readable-local-clone>` for one repository. The script authenticates with `gh`, caches complete raw PR responses and disposable source access once, and returns a compact manifest path and digest.
3. Never switch, reset, clean, or run `gh pr checkout` in the user's current repository merely to inspect a PR. A dirty checkout, unrelated branch, or missing local PR branch is a routing signal, not a blocker.
4. For local review, include staged, unstaged, and relevant untracked source visible when the reviewer reads the target, and confirm there is something to review.
5. Pass through explicit requirement, issue, or decision text without manufacturing missing product intent. If no authoritative requirement is available, disclose that requirement completeness was not verified.

The preparation manifest is raw transport for the observed target. Ordinary review proceeds once against that material and reports the exact evidence and revision inspected; monitoring, target stability, later changes, and final drift are outside its coverage.

## Run exactly one reviewer

Read [review/daily-reviewer.md](review/daily-reviewer.md), then start one fresh isolated read-only reviewer with no inherited conversation turns. Its complete input is the target locator, raw preparation manifest or local read-only access, explicit requirement text, applicable project instructions, the daily reviewer reference, and the side-effect boundary. This reviewer independently performs the five-axis analysis and returns the final local verdict.

If an isolated worker is unavailable, perform the same daily-reviewer protocol once in the coordinator rather than blocking or simulating multiple reviewers. A failed isolated reviewer gets one bounded retry only for a recoverable transport or malformed-output failure; it does not trigger extra independent review rounds.

The reviewer reads the complete diff and enough surrounding requirements, tests, callers, contracts, configuration, and history to support its claims. It evaluates correctness, readability and simplicity, architecture, security, and performance in one pass. It inspects the author's verification story and dependency or dead-code implications when relevant. Suspicious code remains a hypothesis until the reviewer establishes that the target introduced it, identifies a reachable trigger and concrete impact, and checks plausible counterevidence.

Review discovers and explains problems through source inspection, relevant tests, existing CI evidence, and the smallest candidate-specific non-mutating check needed to prove or falsify a concrete concern. Its write surface is an approved system temporary directory or disposable source copy. Full validation suites, dependency installation, target mutation, and CI waiting belong to implementation or explicitly selected validation workflows.

## Interpret the result

The reviewer separates feedback into:

- `Critical`: a security vulnerability, data loss, broken core behavior, or another release-blocking defect;
- required findings with no optional prefix: concrete issues the author should address before the change is review-ready;
- `Optional` or `Consider`: worthwhile but non-blocking improvements;
- `Nit` or `FYI`: minor or informational feedback that the author may ignore.

Required findings must name the smallest changed location, reachable scenario, concrete consequence, supporting evidence, and concise repair direction. Structural findings must propose the simplifying move rather than merely say that code is complex. Do not turn personal style, speculative future scale, generic best practice, or pre-existing defects into required findings.

The local verdict is one of `Review-ready`, `Changes required`, or `Incomplete`; it is never a GitHub review state. `Review-ready` requires one completed five-axis review, no Critical or required finding, no material unresolved question, and no material coverage limit. Optional, Consider, Nit, and FYI feedback does not block it. Existing CI, build, device, runtime, and business evidence may be summarized but is not silently upgraded into coverage the reviewer did not execute.

## Deliver an ordinary review of someone else's PR

When the user explicitly supplied a direct GitHub PR URL, the PR's `author.login` differs from the authenticated `gh` login, the review completed, and the user did not opt out, the invocation authorizes exactly one ordinary PR issue comment containing the final review result. This exception does not apply to a PR owned by the authenticated user, an inferred PR, `OWNER/REPO#NUMBER` without a direct URL, a branch, commit, range, local review, or an incomplete result. Auto review follows its own delivery loop.

The comment must be concise and self-contained: required findings first, optional feedback separately, the local verdict, verification evidence, material coverage limits, and a best-effort statement that later changes were not covered. Never publish internal prompts, credentials, raw preparation material, provisional hypotheses, or chain-of-thought.

Write only the visible Markdown body to `<run-dir>/comment.md`, then run `python3 <skill-root>/scripts/review_publish.py <url> --body-file <run-dir>/comment.md`. The publisher owns fingerprinting, duplicate detection, `gh` delivery, exact readback, and private delivery-file cleanup. After retaining the local result or verified comment URL, remove only the exact coordinator-created system-temporary run directory.

## Side-effect boundary

Review's default write surface is its temporary result. The bounded comment delivery above, `review auto`, or a separate posting request may add only the stated ordinary comment. Repair enters `fix`; a repeated finding-zero objective enters `converge`. Source edits, commits, pushes, thread resolution, formal review state, other PR mutation, and messages remain outside review authorization. Never merge a PR.
