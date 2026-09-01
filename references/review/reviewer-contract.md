# Parallel reviewer contract

This contract keeps four independent reviewer personalities comparable without erasing their different lenses. Every specialist is read-only, receives the same immutable target, and returns claims for a later master to verify.

## Review packet

The coordinator supplies:

- `target_id`: `sha256:<hex>` fingerprint of the exact canonical target-manifest artifact described below.
- `repo_root`, immutable `snapshot_root`, retained `packet_dir`, and `target_kind`: local changes, commit, branch, PR, or explicit range.
- `base_sha`, `head_sha`, and `merge_base_sha` when applicable; use explicit `null` rather than guessing.
- `changed_files`, exact references to the retained diff artifacts, and copied content plus hashes for relevant untracked files; mutable commands are not a substitute for the frozen artifacts.
- `requirement`: fact-only user intent, issue, plan, PR description, or `unknown`, with source provenance and the resulting limitation.
- `scope_decisions`: explicit accepted, rejected, deferred, or out-of-scope decisions with provenance; use an empty list rather than inventing one.
- `project_instructions`, repository constraints, a fact-only impact seed, known unknowns, and allowed non-mutating checks. The packet must not contain provisional findings, severity, confidence, or repair advice that could anchor the lanes.

The coordinator invokes `scripts/review_snapshot.py freeze`, which alone serializes the manifest as RFC 8785 JSON Canonicalization Scheme (JCS): UTF-8 without a BOM, lexicographically sorted object keys, canonical JSON numbers, and explicit JSON `null` for inapplicable fields. Do not reproduce this logic in an ad hoc command. The script uses this exact schema and no additional keys:

```json
{
  "artifacts": [
    {"kind": "cached_diff | committed_diff | unstaged_diff", "length": 0, "sha256": "lowercase hex"}
  ],
  "base_sha": null,
  "entries": [
    {"kind": "submodule | untracked", "mode": "git octal mode", "path_b64url": "raw repository-relative path bytes", "sha256": "lowercase hex", "size": 0}
  ],
  "format": "cyh-review-target/v1",
  "head_sha": "full object id",
  "merge_base_sha": null,
  "repository_roots": ["full root commit object id"],
  "target_kind": "local | commit | branch | pr | range"
}
```

Encode `path_b64url` with unpadded RFC 4648 base64url over the raw Git path bytes. Sort `repository_roots` by lowercase object-id bytes, `artifacts` by `kind`, and `entries` first by decoded raw path bytes and then by `kind` before JCS serialization. Derive `repository_roots` from the root commits reachable from the fixed `head_sha` or local `HEAD`; this intentionally identifies forks with identical reachable history as the same content lineage. All sizes are byte counts and all object IDs retain the repository's full hash width.

The example shows `null` where a field is inapplicable; otherwise every SHA field contains the full immutable object ID.

For a committed range or PR, include fixed base, head, and merge-base SHAs plus the length and SHA-256 of the exact raw `git diff --binary --full-index --no-ext-diff <base>...<head>` artifact as `committed_diff`. For local changes, include the current `HEAD`, separate lengths and SHA-256 values for the exact raw unstaged and cached diff artifacts, and every relevant untracked or submodule entry with mode, size, and content or state SHA-256. Do not normalize paths, content, or line endings. Set `target_id` to `sha256:` plus the lowercase SHA-256 of the exact JCS manifest bytes.

Retain the exact manifest, every referenced diff artifact, copied untracked content, submodule state records, and detached snapshot beside the packet. Every lane and the master invoke `scripts/review_snapshot.py verify` once and inspect that snapshot; they do not regenerate the serialization, rehash the mutable checkout, or resolve a mutable PR number, branch name, or tag.

Before analyzing, verify the retained packet identity. Return `invalid` if a retained artifact or snapshot is corrupted, missing, mismatched, or cannot be reproduced. A later source-worktree edit or moving branch/PR ref is live drift, not packet drift: keep reviewing the immutable snapshot and let the coordinator report staleness at delivery. Never silently switch to a nearby branch, newer PR head, incomplete local diff, regenerated manifest, or current source file.

## Boundaries

- Do not edit source, apply fixes, commit, push, post comments, approve, resolve threads, change PR state, or merge.
- Do not spawn another agent or invoke a recursive top-level review command.
- Keep other specialist reports hidden so the lanes remain independent.
- Do not change the target worktree, index, git metadata, dependencies, user configuration, remote services, browser state, infrastructure, or production data. Checks that write caches or generated output may run only in an exact coordinator-created system temporary directory or disposable repository copy, using already-available dependencies; never install packages during review.
- Batch independent reads, searches, history queries, and checks within each bounded investigation stage. Read the packet, this contract, the role, and packet verification result once; do not spend later turns rereading unchanged control files or manually repeating deterministic hashes.
- Reuse coordinator-retained shared check evidence when its target, command, environment, and output digest match the packet. Rerun only a focused check whose result is necessary to verify a candidate.
- Candidates must be introduced by or materially exposed by the reviewed target. Put pre-existing concerns in coverage and unsupported hypotheses in `open_questions`, not `candidates`.

## Candidate admission

The first round discovers and substantiates candidates; it does not produce final findings. A changed condition, enum member, frontend button, nearby pattern, or plausible consequence is a hypothesis rather than proof. Before admitting a candidate, fill every gate below with `passed`, `failed`, `unknown`, or `not_applicable` plus concrete evidence:

- `introduced_by_target`: compare the frozen target with its baseline and identify the exact introduced or materially exposed behavior. This gate is always required and cannot be `not_applicable`.
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
  "target_id": "packet target_id",
  "status": "completed | blocked | invalid",
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

Set `terminal_reason` to `null` for a completed lane. For `blocked` or `invalid`, provide the precise reason there and keep any partially completed inspection in `coverage`.

If malformed output cannot be corrected, the coordinator records it with this terminal transport schema; it is an execution artifact, not a substitute reviewer report:

```json
{
  "reviewer": "role-id",
  "target_id": "packet target_id",
  "terminal_status": "blocked | invalid | malformed",
  "attempt_count": 2,
  "validation_errors": ["precise schema or execution error"],
  "raw_output_sha256": "sha256:<hex>",
  "raw_output": "exact raw output or lossless artifact reference",
  "envelope": null
}
```
