# Build mode

Use this mode to implement a concrete request, plan, issue, or agreed fix. Local file edits within the stated scope are authorized; external mutations are not implied.

## Before editing

1. Read the complete source of truth named by the user and verify it is concrete enough to implement. Resolve missing facts from the repository when possible.
2. Inspect branch, HEAD, working-tree changes, submodules, and relevant generated artifacts. Preserve unrelated user work.
3. Confirm the intended repositories and deployment surfaces. If multiple repositories are involved, keep their changes and validation evidence distinct.
4. Reuse existing project patterns, clients, components, types, migrations, and test helpers. Avoid speculative abstractions and unrelated cleanup.

Do not use destructive Git operations as an implementation shortcut. Do not modify production data or configuration unless explicitly authorized.

## Implement and verify

1. Implement the optimal coherent solution for the agreed behavior and repository constraints. Compare viable reuse, standard-library, native-platform, installed-dependency, direct-code, and new-abstraction options; prefer less code only when correctness, clarity, maintainability, testability, performance, and compatibility remain equal.
2. Add or update tests when the project normally tests that behavior or the regression risk warrants them.
3. Run focused checks early, then broader checks in proportion to risk and repository norms. Inspect every failure and distinguish introduced failures from the baseline.
4. Exercise the real user flow when UI, device, browser, deployment, or external integration behavior is part of acceptance and the required access is available.
5. Review the final diff for unintended files, generated noise, secrets, scope creep, and incomplete requirements.

A successful typecheck, build, HTTP response, CI job, deployment, or screenshot proves only its own evidence lane. Do not claim full completion when business behavior or another platform remains unverified.

## GitHub and delivery

Commit, push, create or edit a PR, post a message, or deploy only when the user explicitly asks for that action.

When commit or push is authorized:

- Re-read status, diff, branch, remote, and relevant live refs immediately before acting.
- Include only scoped files; exclude `.codegraph/`, caches, credentials, logs, build output, screenshots, and unrelated user artifacts unless they are intentional deliverables.
- Run the checks that are safe and proportionate. If the user asks to ship before a long check finishes, push the reviewed change and state exactly what remains unverified.
- Use a normal push unless history rewriting was explicitly authorized and its lease target was verified.
- After pushing, verify the remote branch SHA and report the exact URL when one exists.

Never merge a PR.

## Completion

Report what changed, where it changed, validation results, incomplete or baseline checks, delivery state, and any remaining business acceptance. Do not quietly continue into unrelated tasks.
