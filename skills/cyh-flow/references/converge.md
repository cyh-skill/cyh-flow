# Converge mode

Use this mode for an explicit, persistent finding-zero objective. Create a durable Goal, discover supported findings through the user-selected evidence lanes, repair them with one writer, rerun every required lane invalidated by the repair, and continue until the completion gate is satisfied. `converge` is not a synonym for repeatedly running code review: review, automated checks, simulator or device flows, browser flows, runtime evidence, security analysis, performance validation, CI, and business acceptance can all be finding sources.

Invoking `converge` authorizes scoped local repair, local validation, and read-only subagent analysis across rounds. It does not authorize commit, push, PR changes, deployment, production writes, external load, or unrelated cleanup.

## Establish the Goal and evidence contract

Resolve the exact repository, objective, source of truth, scope, non-goals, starting target, and stopping condition. Then establish one Goal through the canonical Skill's host mapping. In Codex, create the native Goal when available. In Claude Code, use a user-activated `/goal` only when it already owns this objective, mirror live phases with Task tools when available, and treat the repository ledger as the durable resume authority; do not claim that this is the Codex Goal API. Do not claim that a Goal exists when no host goal or ledger contract was established, assign a token budget unless the user explicitly requested one, replace an unfinished different Goal, or mark completion merely because work stopped.

The user owns the required evidence lanes. They may define any combination, including only four-lens code review, only a named browser journey, a simulator scenario plus Web testing, automated tests, runtime or log checks, security or performance validation, or a custom acceptance procedure. Do not infer that review is mandatory from words such as “recheck” or “finding zero,” and do not infer that browser testing is mandatory merely because the target has a Web UI. Record the user's selection verbatim in the Goal contract. A passing unrequested lane cannot substitute for a required lane, and the agent must not silently add, remove, or weaken a required lane.

Top-level `<cyh-flow> auto` is the explicit exception to choosing a minimal or separately confirmed contract: its invocation delegates selection and requires every applicable review and test lane defined by [auto.md](auto.md). Determine applicability from the affected behavior and project contract, not from current tool or environment availability, then execute every required lane that is safe and currently authorized. Record that derived matrix as the user-selected contract for the convergence phase. Do not omit a lane merely because it is slow; if an applicable required lane cannot run without new authorization, an unavailable environment, destructive action, or an external mutation, keep the Goal incomplete and report the blocker.

The user may add, replace, or remove required lanes during the Goal. Treat that as an explicit evidence-contract revision: preserve the earlier results as history, record the new requirement and its effective target, and evaluate completion only against the current contract. Do not reinterpret an observation, suggestion, or exploratory diagnostic as a contract revision without clear user intent.

If the user did not specify evidence lanes, or explicitly delegated the choice, propose the smallest risk-appropriate set and state it before relying on it. Ask for confirmation only when different choices would materially change the work, side effects, cost, or meaning of completion; otherwise proceed with the disclosed set. Additional lanes may be recommended, but they become completion requirements only after the user accepts them. Report unexecuted lanes as limitations rather than pretending they were covered.

Evidence selection controls which lanes must be actively executed; it does not authorize ignoring a concrete finding encountered elsewhere while repairing or tracing the selected flow. Any supported, actionable, in-scope finding actually discovered enters the ledger and blocks finding zero until repaired, rejected with evidence, explicitly moved out of scope by the user, or otherwise resolved under the Goal contract.

## Parallel evidence execution

For the baseline and every recheck round, decompose the selected evidence contract and independent impact surfaces into bounded subagent tasks, use the maximum useful concurrency, and refill available slots with the next ready lane. Assign separate agents to independent code, test, contract, log, platform, security, performance, browser, or device evidence only when their targets and runtime resources do not conflict. Each agent returns the fixed target it examined, procedure and evidence, findings, unverified areas, and any invalidated downstream lanes.

Maintain one mutually exclusive repair writer and one coordinator-owned finding ledger. Evidence agents remain read-only against the shared repository; the coordinator verifies, deduplicates, and records their results before the writer repairs them. When a selected lane has its own stronger topology, such as four-lens review, use that protocol. Serialize agents that would otherwise operate the same browser target, simulator, device, database, cache, build output, or external environment.

Define “finding zero” as zero supported, actionable, in-scope findings remaining in the ledger, the initiating failure accounted for, and every user-required evidence lane passing or producing no supported finding on the final target. It is not a claim that the software is universally defect-free. A blocked required lane or material unverified result prevents completion unless the user explicitly revises the Goal contract.

The Goal preserves ordinary authorization boundaries. Browser, simulator, device, API, database, scan, and load-test actions may have side effects; use only the environment and actions the user authorized. Never treat a local repair as proof that a remote branch, PR, deployment, simulator build, browser session, or business workflow was updated.

## Build the baseline and finding ledger

Execute the selected evidence lanes against the starting target far enough to establish a trustworthy baseline. The ledger records stable ID, evidence lane, severity, location or journey step, trigger, observable impact, evidence, repair direction, target identifier, and status. Findings may originate from:

- code review and requirement or contract analysis;
- unit, integration, end-to-end, build, lint, type, or other automated checks;
- simulator, emulator, real-device, accessibility, or platform-specific flows;
- browser journeys, API behavior, network evidence, and Web acceptance;
- runtime logs, observability, recovery, security, performance, CI, or business evidence.

Add only reproducible or independently supported findings. Keep unrelated baseline failures separate, and keep blocked findings open rather than hiding them. The initiating failure must be reproduced when safe, tied to trustworthy evidence, or disposed of with a documented causal explanation; an empty ledger is not completion when the original problem remains unexplained.

When the selected lane is full code review, load [review.md](review.md) and use its four independent live specialist reviewers, master recheck, and evidence-bounded clean gate. When browser automation is selected, use the installed `cyh-browser-skill` through the active host mapping; ordinary static public research is not browser acceptance. For simulator or device testing, prefer the project's established tooling and official or vendor-maintained capabilities. Do not write production data or external systems without separate authorization.

## Repair and recheck loop

Use one mutually exclusive writer for the entire Goal. Parallel agents inspect code, analyze logs, exercise non-conflicting evidence lanes, or review the current target, but they remain read-only against the shared repository and must not share writer ownership.

Repeat:

1. Verify each new claim and consolidate duplicates by root cause; reject unsupported claims with a reason.
2. Repair supported findings in dependency order with the smallest coherent root-cause correction that satisfies the real contract.
3. Run focused rechecks inside the user-required evidence lanes after each coherent change and separate introduced failures from the baseline. Do not automatically add routine unit, type, lint, build, review, browser, or device checks that the user did not select. An extra diagnostic may run only when needed to understand or repair the selected flow; it does not become a completion lane without user acceptance, although any concrete in-scope defect it proves must still enter the ledger.
4. Inspect the complete current target, including intentional untracked deliverables.
5. Rerun every required evidence lane whose prior result could have been invalidated. Do not reuse a clean review, passing simulator run, browser result, benchmark, or test result from before the relevant change.
6. Add newly discovered supported findings to the ledger and continue until the latest complete round leaves none open.

The mix may change between rounds when evidence points elsewhere: a reviewer finding may require a simulator reproduction, a browser failure may require code review, or a performance regression may require profiling. Such diagnostics help resolve the Goal but do not become new completion requirements unless the user accepts them or they are necessary to validate an existing required lane.

Do not impose an arbitrary round limit while measurable progress continues. If findings recur, fixes oscillate, or a round makes no net progress, stop patching symptoms, expand the root-cause trace, strengthen regression evidence, and change strategy. If progress still requires a product decision, unavailable environment, new permission, destructive action, or external mutation, report the exact blocker and keep the Goal incomplete.

## Completion gate

Mark the Goal complete only when:

- the ledger contains zero supported open findings;
- the initiating failure has before/after evidence or another accepted causal resolution;
- every user-required evidence lane was rerun as needed and passes on the final target;
- the latest selected discovery or recheck pass produces no new supported finding after the final repair;
- all requested subagents and test runs finished and their results were inspected;
- the final diff contains no unintended files, credentials, generated noise, debug residue, or unreviewed behavior;
- local versus remote, build, simulator/device, browser, deployment, and business states are reported separately.

Report completion as “zero supported findings within the Goal scope and user-selected evidence lanes,” followed by the rounds, repairs, evidence executed, final target, delivery state, and any non-required lane that remains unverified. Never weaken the stopping condition because the work is slow or difficult.
