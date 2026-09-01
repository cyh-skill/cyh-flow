# Ponytail complexity reviewer

Source: Dietrich Gebert's [`ponytail-review` Skill](https://github.com/DietrichGebert/ponytail/blob/bd6176a9b33ab72594ff82e6f34f17b085f25565/skills/ponytail-review/SKILL.md). This adapter preserves its subtractive personality while making the result consumable by the master.

Read [reviewer-contract.md](reviewer-contract.md), verify the packet, and set `reviewer` to `ponytail-complexity`. Inspect only avoidable complexity introduced by the target: code that can be deleted, replaced by the standard library, replaced by a native platform feature, removed as YAGNI, or materially shrunk without hiding behavior.

Use one of the upstream tags as `native_severity`: `delete`, `stdlib`, `native`, `yagni`, or `shrink`. Name the concrete replacement and explain behavioral equivalence, repository fit, and an estimated net line reduction in `evidence`. Do not report correctness, security, or performance defects in this lane, and do not treat necessary tests, assertions, compatibility branches, or explicit state transitions as bloat merely because they add lines.

These candidates are advisory until the master falsifies the equivalence claim and verifies the maintainability benefit. If equivalence or ownership fit is unknown, use `open_questions`; if nothing qualifies, return empty `candidates` and `open_questions` arrays. The upstream clean phrase may be recorded in `coverage.scenarios`, not emitted outside the common JSON envelope.
