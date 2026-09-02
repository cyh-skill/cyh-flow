# Ponytail complexity reviewer

Read [reviewer-contract.md](reviewer-contract.md), independently resolve the current target, and set `reviewer` to `ponytail-complexity`. Inspect only avoidable complexity introduced by the target: code that can be deleted, replaced by the standard library, replaced by a native platform feature, removed as YAGNI, or materially shrunk without hiding behavior.

Classify the proposal in its `title` or evidence as `delete`, `stdlib`, `native`, `yagni`, or `shrink`. Name the concrete replacement and use `evidence_refs` and `counterevidence` to establish behavioral equivalence, repository fit, and an estimated net line reduction. Do not report correctness, security, or performance defects in this lane, and do not treat necessary tests, assertions, compatibility branches, or explicit state transitions as bloat merely because they add lines.

Set `category` and `claim_type` to `complexity`. These candidates are advisory until the master falsifies the equivalence claim and verifies the maintainability benefit; an accepted advisory does not become a correctness finding or block clean. If equivalence is unknown, use `open_questions`; if nothing qualifies, return empty `candidates` and `open_questions` arrays. Write and validate the compact common artifact without severity, confidence, or repair fields.
