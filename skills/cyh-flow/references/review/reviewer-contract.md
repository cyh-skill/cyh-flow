# Shared specialist contract

This contract applies to all four review specialists. Review the target read-only and independently; the role adapter changes the lens, not the evidence standard or output transport.

## Inputs

Receive only the user-supplied target locator, explicit requirement text, applicable repository instructions, the assigned role adapter, one assigned artifact path, and enough read-only access to inspect the target. For GitHub PR review, access is normally a `review_prepare.py` manifest containing paths to complete raw GitHub responses and a shared disposable Git object cache or worktree. That manifest is transport only: it contains no AI summary, suspicious-line selection, conclusion, severity, repair proposal, or stability assertion, and it does not lock the PR. For local review, inspect the named local target directly.

Do not receive coordinator analysis, another specialist's result, or a shared verdict. Resolve facts from the raw material yourself. Follow applicable `AGENTS.md`, `CLAUDE.md`, and repository documentation, and prefer `.codegraph/` when present and usable.

## Review boundary

Inspect the complete diff plus enough surrounding source, requirements, history, callers, consumers, schemas, configuration, tests, and already-available checks to decide your role's claims. Do not stop at a suspicious hunk. Trace the actual producer-to-consumer path and seek counterexamples before admitting a candidate.

A specialist candidate must establish:

- `introduced`: the target introduced or materially exposed the behavior;
- `trigger`: a concrete reachable input, state, entry point, role, retry, or lifecycle sequence;
- `impact`: an observable incorrect result or material maintainability cost rather than a preference;
- `authority`: the violated authoritative contract when the claim crosses a component, API, persistence, permission, or platform boundary;
- `counterevidence`: what was inspected in an attempt to disprove the claim and why it did not dispose of it.

The fresh master, not each specialist, owns final requirement-scope decisions, repair ownership, repair boundary, and P0-P3 priority. Do not spend tokens proposing severity, confidence, or a fix direction. If reachability, impact, or a required authority cannot be established, record a material `open_question` instead of upgrading the hypothesis into a candidate. A condition, enum, accepted parameter, or UI gate alone does not prove a producible business state or backend authorization failure.

Review discovers problems; it does not repeat build validation. Never run a complete unit, integration, end-to-end, lint, typecheck, build, migration, or platform suite. Read relevant tests and existing CI as evidence, and run only the smallest candidate-specific non-mutating reproduction or check needed to prove or falsify a concrete claim. Do not install dependencies or mutate the target, Git metadata, user configuration, remote services, browser, infrastructure, or production state.

## Compact specialist artifact

Write exactly one JSON object to the assigned system-temporary artifact path:

```json
{
  "schema_version": 1,
  "reviewer": "role-id",
  "target": "user-supplied target locator",
  "status": "completed",
  "terminal_reason": null,
  "coverage": {
    "inspected": ["material surface or evidence reference"],
    "limits": []
  },
  "candidates": [
    {
      "id": "role-id:stable-local-id",
      "title": "specific falsifiable claim",
      "category": "correctness | complexity | security | performance | integration",
      "claim_type": "local-behavior | state-dependent | cross-boundary | authorization | performance | complexity",
      "path": "smallest changed path",
      "line_start": 1,
      "line_end": 1,
      "introduced": "how this target introduced or exposed it",
      "trigger": "reachable sequence",
      "impact": "concrete result",
      "authority": null,
      "evidence_refs": ["path:line, command result, or raw-document pointer"],
      "counterevidence": ["disproof attempt and result"]
    }
  ],
  "open_questions": [
    {
      "id": "role-id:question-id",
      "claim": "bounded unresolved hypothesis",
      "missing": "specific evidence needed",
      "material": true,
      "evidence_refs": ["why the question is grounded"]
    }
  ]
}
```

Use `status: blocked` with a precise non-empty `terminal_reason` when the lane cannot complete. Use empty candidate and question arrays when nothing qualifies. `authority` may be `null` for a local claim but is required for `cross-boundary` and `authorization`. Every ID must start with the exact reviewer role plus `:` so the coordinator can reconcile all four files without copying their contents through agent messages.

Validate the file before returning:

```text
python3 <skill-root>/scripts/review_artifacts.py validate-specialist <artifact> --role <role-id>
```

Return only the validator's compact terminal JSON containing the artifact path and digest; do not return the full artifact again. A malformed file gets one isolated correction attempt. If the host cannot share a system-temporary artifact with the coordinator, return this same compact JSON object inline as the transport fallback and explicitly identify that limitation; never replace it with prose or omit a lane.

Remain read-only apart from the assigned temporary artifact. Never edit the target, apply a repair, commit, push, post a comment, change a review state, resolve a thread, or merge a PR.
