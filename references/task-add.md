# Task-add mode

Use this mode to turn a raw batch of bugs, small changes, chores, or follow-up ideas into durable, independently executable tasks without implementing them. The only authorized mutation is the task pool under `<repository>/.cyh-flow/tasks/`; source code, configuration, Git state, and external systems remain read-only.

## Analyze before storing

Resolve the real repository first, then inspect only enough read-only context to make each item understandable and actionable. Separate distinct outcomes into distinct tasks, merge clear duplicates, link dependencies, and preserve uncertainty instead of inventing product behavior. A task may describe a bug, change, chore, investigation, or another bounded unit of software work; do not force every item into bug terminology.

Store confirmed facts separately from assumptions. Each task should state the observed problem or desired outcome, relevant scope and evidence, a concise analysis, and an acceptance condition another Agent can use without needing the original conversation. Missing information does not block intake: record it under the task and let `task-run` move the item to `waiting` and ask the user if that information becomes necessary for execution.

## Dated Markdown pool

The task document is the only persistent source of truth for status and ownership. Store tasks in `.cyh-flow/tasks/YYYY-MM-DD.md` using the target repository's local date at first intake; later status changes stay in that original document. Use stable IDs in the form `TASK-YYYYMMDD-NNN` and never reuse or renumber an ID.

Every task must visibly contain:

- status: `pending`, `doing`, `waiting`, or `done`;
- type, title, source, creation time, and last-update time;
- current owner and claim time, using `—` before the first claim;
- the content or observed behavior, analysis, acceptance condition, evidence, and an append-only handling history.

Use [scripts/task_pool.py](../scripts/task_pool.py) from this Skill directory to add the analyzed batch so concurrent intake cannot produce duplicate IDs or overwrite a daily document. Prepare a temporary UTF-8 JSON object or array with `title` and optional `type`, `source`, `content`, `analysis`, `acceptance`, and `screenshots` fields, then run:

```text
python3 <skill-root>/scripts/task_pool.py --pool <repository>/.cyh-flow/tasks add --input <json-file-or-->
```

Each `screenshots` entry may be a local image path or an object containing `path` and optional `label` and `source` fields. The script preserves the original bytes under `.cyh-flow/tasks/assets/<TASK-ID>/`, inserts a relative Markdown image link, and records its source and intake time in that task so later Agents can view the original evidence. Never recompress, edit, overwrite, or upload a screenshot unless the user separately asks. If an attachment is visible in the conversation but no readable local artifact is available, record that the screenshot could not yet be persisted and ask the user to attach or provide it; do not fabricate a replacement.

Do not manually synthesize IDs or rewrite existing task sections. If the same work is already present, report the existing ID rather than creating a duplicate; do not silently merge materially different screenshots or acceptance conditions.

## Completion

Report the dated Markdown path, new task IDs, preserved screenshot paths, duplicate relationships, and any uncertainty retained for execution. Do not start implementation, claim a task, or change delivery state in `task-add` mode.
