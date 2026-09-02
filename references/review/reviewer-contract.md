# Parallel reviewer contract

This contract keeps four independent reviewer personalities comparable without erasing their different lenses. Every specialist is read-only, resolves the current review target for itself, and returns claims for a later master to verify.

## Review input

The coordinator supplies only the minimum routing context:

- `target`: the user-supplied working tree, branch, commit, range, or pull-request locator;
- repository access information when the target cannot otherwise be reached safely;
- explicit user intent or requirement text already present in the request, if any;
- applicable project instructions and the read-only side-effect boundary.

Do not supply a coordinator-generated diff summary, changed-file shortlist, architecture conclusion, suspicious location, candidate finding, severity, confidence, repair advice, another reviewer's output, or a shared verdict. Each specialist independently reads the current diff, surrounding code, repository instructions, requirement sources, history, callers, contracts, tests, configuration, and checks material to its own lens.

The target is live and best-effort. Do not freeze, pin, fingerprint, copy, hash, verify, compare, or monitor it. Do not wait for the worktree, branch, or pull request to become stable, and do not restart merely because it changes. Different reviewers and the master may observe different revisions; that is an accepted limitation, not an invalid run. Report only evidence actually inspected and do not claim that the result covers a later or final revision.

For GitHub targets, use authenticated `gh` for PR metadata, diff, reviews, checks, and repository access. Choose the cheapest safe way to read enough surrounding source; use a disposable clone only when necessary, and never change the user's checkout just to represent a PR.

## Boundaries

- Do not edit source, apply fixes, commit, push, post comments, approve, resolve threads, change PR state, or merge.
- Do not spawn another agent or invoke a recursive top-level review command.
- Keep other specialist reports hidden so the lanes remain independent.
- Do not change the target worktree, index, git metadata, dependencies, user configuration, remote services, browser state, infrastructure, or production data. Checks that write caches or generated output may run only in a coordinator-approved system temporary directory or disposable repository copy using already-available dependencies; never install packages during review.
- Batch independent reads, searches, history queries, and checks within each bounded investigation stage. Use adaptive sequential investigation only when one result genuinely determines the next query.
- Candidates must be introduced by or materially exposed by the target as the reviewer observed it. Put pre-existing concerns in coverage and unsupported hypotheses in `open_questions`, not `candidates`.

## Candidate admission

The first round discovers and substantiates candidates; it does not produce final findings. A changed condition, enum member, frontend button, nearby pattern, or plausible consequence is a hypothesis rather than proof. Before admitting a candidate, fill every gate below with `passed`, `failed`, `unknown`, or `not_applicable` plus concrete evidence:

- `introduced_by_target`: compare the observed target with its available baseline and identify the exact introduced or materially exposed behavior. This gate is always required and cannot be `not_applicable`.
- `business_reachability`: trace a real entry point to the behavior. A state-dependent claim also needs a producer, persisted legacy path, fixture, test, runtime record, or authoritative contract that can create the state; a conditional branch or enum value alone does not pass.
- `authoritative_contract`: inspect the source of truth when semantics cross a boundary. Authorization claims must trace the UI, API request, backend enforcement or FSM, and relevant multi-role behavior; a frontend gate is not the authorization authority.
- `scope_decision`: inspect available user intent, issue or plan history, and explicit accepted, rejected, deferred, or out-of-scope decisions. `not_applicable` is allowed only after recording which available sources were checked.
- `repair_ownership`: identify the component or repository that owns the invariant and show that the proposed repair boundary can satisfy the contract; “change the cited line” is not ownership evidence.

Before marking a gate `passed`, actively test the nearest plausible counter-hypothesis: an alternate producer, unreachable business path, backend rejection, different role behavior, preserved legacy route, explicit scope decision, or different owning component. Record those checks in a non-empty `counterevidence_checked` list. If required counterevidence cannot be inspected, that gate is `unknown`, not `passed`.

All applicable gates must be `passed` before an item enters `candidates`. Put a plausible item with any required `unknown` gate in `open_questions` without severity or repair advice. Omit a disproved hypothesis or record the disproof in coverage. Performance candidates may pass reachability and impact with a mechanically proven scale bound; complexity candidates must prove behavioral equivalence and repository ownership fit.

## Specialist result

Return one JSON object and no prose outside it:

```json
{
  "reviewer": "role-id",
  "source": "upstream source URL",
  "target": "user-supplied target locator",
  "status": "completed | blocked",
  "terminal_reason": null,
  "coverage": {
    "paths": ["path or symbol inspected"],
    "scenarios": ["behavior or threat examined"],
    "checks": ["command and result"],
    "unverified": [
      {
        "item": "surface or claim not verified",
        "material": true,
        "required": true,
        "reason": "why it remains unverified"
      }
    ]
  },
  "candidates": [
    {
      "id": "role-local stable id",
      "title": "specific candidate claim",
      "native_severity": "source lens severity",
      "category": "correctness | complexity | security | performance",
      "claim_type": "local-behavior | state-dependent | cross-boundary | authorization | performance | complexity",
      "path": "repository-relative path",
      "line_start": 1,
      "line_end": 1,
      "root_cause": "what the target changed incorrectly",
      "trigger_or_reachability": "concrete conditions that exercise it",
      "concrete_impact": "observable user, data, security, or resource impact",
      "evidence": ["code, history, test, trace, benchmark, or calculation"],
      "evidence_gates": {
        "introduced_by_target": {"status": "passed", "evidence": ["baseline proof"]},
        "business_reachability": {"status": "passed", "evidence": ["entry point and producer proof"]},
        "authoritative_contract": {"status": "not_applicable", "evidence": ["why no external authority applies"]},
        "scope_decision": {"status": "passed", "evidence": ["requirement or decision provenance"]},
        "repair_ownership": {"status": "passed", "evidence": ["owning boundary proof"]}
      },
      "counterevidence_checked": ["baseline, alternate path, or contract that could disprove the claim"],
      "fix_direction": "minimal repair direction, not a patch",
      "confidence": "high | medium | low"
    }
  ],
  "open_questions": [
    {
      "id": "role-local question id",
      "claim": "plausible but unproven concern",
      "missing_gates": ["business_reachability"],
      "available_evidence": ["what is currently known"]
    }
  ]
}
```

Use empty `candidates` and `open_questions` arrays when appropriate. Do not promote an open question to make the report look useful, and do not assign it severity or a repair. `native_severity`, `confidence`, and `fix_direction` on an admitted candidate remain untrusted specialist proposals; the master ignores them until independent falsification is complete. Keep source-native details that do not fit the common fields inside `evidence`.

Set `terminal_reason` to `null` for a completed lane. For `blocked`, provide the precise reason there and keep any partially completed inspection in `coverage`.

If malformed output cannot be corrected, the coordinator records it with this terminal transport schema; it is an execution artifact, not a substitute reviewer report:

```json
{
  "reviewer": "role-id",
  "target": "user-supplied target locator",
  "terminal_status": "blocked | malformed",
  "attempt_count": 2,
  "validation_errors": ["precise schema or execution error"],
  "raw_output_sha256": "sha256:<hex>",
  "raw_output": "exact raw output or lossless artifact reference",
  "envelope": null
}
```
