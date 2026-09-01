# Task-run mode

Use this mode to independently claim and process stored work from `.cyh-flow/tasks/YYYY-MM-DD.md`. The Markdown task fields are the only persistent ownership and status record; there is no primary dispatcher, separate claim database, durable lock record, or claim token.

## Launch claiming workers

Use the maximum useful subagent concurrency for a user-selected task ID or all eligible work in the selected pool. Launch independent workers early and refill capacity as workers finish until the selected task is done, no `pending` work remains, or claimed tasks conflict on files or runtime resources. The invoking coordinator may select the pool or pass one requested task ID and consolidate outcomes, but it must not promise unsupported date, content-scope, or global-count filtering, preassign a task from an unlocked read, or become a separate ownership authority.

Every worker receives the pool path, selection boundary, applicable instructions, unique Agent identity, and the same claim-before-acting contract below. Each worker claims for itself, handles only its successfully claimed task, records completion or waiting state through the document, and returns the task ID, changed paths, validation, status, and question if blocked. A single selected task uses one worker; do not invent duplicate work merely to increase the Agent count.

## Claim before acting

Every Agent needs a distinct, stable identity for the current run, preferably its host-provided session or Agent ID. Before investigating or editing application files, the Agent must claim exactly one task through [scripts/task_pool.py](../scripts/task_pool.py):

```text
python3 <skill-root>/scripts/task_pool.py --pool <repository>/.cyh-flow/tasks claim --agent <agent-id>
```

Pass `--task-id <ID>` only when the user selected a specific task. The claim command takes a short operating-system file lock, re-reads the current Markdown, selects an eligible `pending` task, changes it to `doing`, writes the Agent identity and claim time into that same task, appends the event to its history, and releases the lock. The lock carries no business state. If several Agents race, each later Agent sees the already-written `doing` state and claims another task or receives an empty result.

Never select work from a prior unlocked read, manually change `pending` to `doing`, process a task whose successful claim was not observed, or take over a `doing` task. An abandoned `doing` task remains owned until the user explicitly authorizes reassignment; safety favors a visible stale claim over duplicate work.

## Conflict gate before mutation

After a successful claim and full task read, but before any application-file edit or command that can mutate shared runtime resources, re-read all visible `doing` tasks and the working tree. Resolve the claimed task's expected files, modules, generated artifacts, Git surfaces, dependency caches, browser targets, simulators, devices, databases, build outputs, and external environments, then compare them with every other current owner and unrelated active work.

When scopes overlap or require the same exclusive resource, exactly one claimant proceeds: the earlier recorded claim time wins; if claim times are equal, the lexicographically smaller task ID wins. Every lower-priority claimant must make no source or runtime mutation, move its own task to `waiting`, and record the winning task ID, owner, and conflicting surface. A later claimant that appears after another worker passed the gate yields under the same rule. This post-claim gate is mandatory because the atomic Markdown claim protects task ownership, not source files or runtime-resource leases.

## Process the claimed task

After claiming, re-read the returned task section and applicable project instructions. View every locally preserved screenshot or other evidence linked by that task before deciding the cause or expected behavior. Missing or unreadable evidence must be reported honestly and becomes a question only when it blocks responsible execution.

Handle only the claimed task. `task-run` authorizes coherent local edits and proportionate validation required by its acceptance condition. It does not authorize commit, push, PR changes, deployment, production or external writes, destructive actions, or messages to other people without separate user intent.

Independent Agents may run concurrently only after passing the conflict gate and only while their claimed tasks retain non-conflicting file ownership and runtime resources. If new evidence reveals an overlap after work began, stop before the next mutation, apply the same deterministic priority rule, and move the losing task to `waiting`. Do not race the edit or silently broaden a small change into unrelated cleanup.

When a necessary product decision, missing input, new authorization, destructive action, unavailable required environment, or ownership conflict blocks the task, record a concise question and move it to `waiting`. Continue directly when the task and authority are clear; do not ask for routine confirmation.

## Finish through the document

Only the Agent recorded as the current owner may finish its `doing` task. Update it through the script so the owner is checked under the same short document lock:

```text
python3 <skill-root>/scripts/task_pool.py --pool <repository>/.cyh-flow/tasks finish --task-id <ID> --agent <agent-id> --status done --note <summary>
python3 <skill-root>/scripts/task_pool.py --pool <repository>/.cyh-flow/tasks finish --task-id <ID> --agent <agent-id> --status waiting --note <question-or-blocker>
```

Use `done` only when the requested behavior is implemented and its required evidence passes; include changed paths and validation in the history note. Use `waiting` when user input or another explicit dependency is required, preserve the last owner and claim time, and surface the exact question to the user. A failed check that can be diagnosed and repaired within scope remains `doing` while progress is possible.

After the user answers a waiting task, record that answer and return the task to `pending` before anyone claims it again:

```text
python3 <skill-root>/scripts/task_pool.py --pool <repository>/.cyh-flow/tasks reopen --task-id <ID> --agent <agent-id> --note <user-answer>
```

`reopen` accepts only `waiting` tasks, clears current ownership, and preserves the earlier claim in history. It cannot be used to steal a `doing` task.

After finishing one task, an Agent may claim the next eligible task and repeat until no `pending` task remains or safe progress requires user input. Report completed IDs, waiting IDs and questions, checks performed, remaining `pending` or pre-existing `doing` work, and local-versus-delivered state.
