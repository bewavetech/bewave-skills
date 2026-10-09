# Execute

**Goal:** turn the plan into green, committed code one task at a time, or one wave at a time in parallel, without scope creep and without losing the trail.

## Before the first task

1. Confirm the plan is approved (MEDIUM+), or that the inline plan was stated (LOW).
2. Run the `full` gate once on the untouched tree. If the baseline is already red, report it and agree how to proceed before changing anything. Otherwise your task gates cannot tell your failures from pre-existing ones.
3. Decide inline vs. sub-agents for each wave ([sub-agents.md](sub-agents.md)).

## Task cycle

For each task, in wave order:

### 1. Orient

State three lines, in chat or in your scratch reasoning:

- **Assumptions:** anything you are taking as given. If one is shaky, check it now.
- **Surface:** the files from `Touches`, adjusted if reading the code shows otherwise.
- **Proof:** the tests from the task and the gate level.

Mark the task `[~] in progress` in `plan.md` (MEDIUM+). This is the only place status lives.

### 2. Tests first where they come from the spec

Write the task's SPEC, CONTRACT and INVARIANT tests from the spec before implementing, and see them fail for the right reason (tests that only cover behavior an earlier task already built pass at once; that is fine, say so). Write CHARACTERIZATION tests **before** touching legacy code, and see them pass. Write a bug fix's REGRESSION test first, and see it fail. Rules and depth: [testing.md](testing.md).

### 3. Implement

Write the minimum code that satisfies the task's ACs and makes its tests pass.

- **Simplicity.** Choose the simplest design that passes the tests: plain functions and data before classes, hierarchies, patterns or generics. No abstraction before a second real use (a third for extraction of shared code), no interface with one implementation, no config flags, plugin points, caches or retries nobody asked for, no handling for impossible states. Duplication of two or three lines beats a premature abstraction.
- **Surgical.** Touch only what the task needs. Match the existing style even where you would choose differently. Do not "improve" adjacent code. Remove only what your own change orphaned.
- **Reuse.** Extend the components and libraries already in the project before writing new ones or adding dependencies.
- **Good practices, in proportion.** Intention-revealing names; small, single-purpose functions; early returns over deep nesting; validate at system boundaries (user input, external calls), trust internal code; errors handled where the spec names them, not blanket try/catch; no dead code, commented-out code or stray TODOs; follow the language and framework idioms already in use.

### 4. Gate

Run the task's gate command from Verification Commands. A non-zero exit means stop, fix, re-run. The runner decides, not your judgment. Confirm the affected suites' test counts did not drop.

### 5. Review the diff once

One consolidated pass:

- Adequacy review ([testing.md](testing.md)), scaled to the task's risk.
- Every changed line traces to the task. No drive-by edits. Look for overengineering: an abstraction with one use, an unneeded parameter or layer, speculative generality, code a standard library or existing helper already covers. Remove it, then re-gate.
- Does reality still match the spec? If not, raise an amendment now ([amendments.md](amendments.md)), not after the commit.
- Task risk MEDIUM+ with non-trivial new branching: run the mutations due ([testing.md](testing.md#discrimination-mutation-testing)).

### 6. Record and commit

Mark the task `[x] done` in `plan.md` and commit. The status update goes **in the same commit** that completes the task, so a crash between the two can never make resume redo finished work. The SHA is optional; `git log` already has it.

## Commits are logical units

A commit is one coherent, revertible, green change with an honest message. That is often one task, but not always.

| Situation | Commits |
| --- | --- |
| A normal behavioral task | One commit |
| A task that needs a preparatory refactor | Refactor commit (behavior unchanged, gate green), then the behavior commit |
| A task including a schema migration | Migration commit, then the behavior commit, so the migration can be reviewed and reverted on its own |
| Several tiny LOW tasks touching the same lines | One commit that names all of them |
| A large task | Several commits, each green, the last one marking the task done |

Rules:

- **Every commit passes at least the quick gate** (bisectable history). **Never mix** refactoring with behavior change, formatting with logic, or unrelated tasks.
- **Conventional Commits 1.0.0:** `type(scope): imperative lowercase description`, no trailing period, header ≤ 72 characters. Types: `feat fix refactor perf test docs build ci chore style`. Breaking changes use `!` plus a `BREAKING CHANGE:` footer.
- Reference task and AC IDs in the body when it helps a reviewer (`Covers CPN-03, CPN-04 (T2)`).
- Validate: `python3 <skill-dir>/scripts/check_commit.py --message "<msg>"`. It can also be installed as a `commit-msg` hook if the project does not already manage hooks: `ln -sf <skill-dir>/scripts/check_commit.py .git/hooks/commit-msg`.
- Follow the project's own commit conventions when they differ; they take precedence.

## After each wave

Run the `full` gate on the integrated result. Fix integration failures before starting the next wave. When parallel workers were used, the orchestrator does this after merging ([sub-agents.md](sub-agents.md)).

## Scope guardrail

You will notice things worth fixing. Do not fix them in this task.

- Bug outside the task → tell the user, or add it to `plan.md` → Deferred.
- Improvement idea → `plan.md` → Deferred (or `context.md` → Deferred Ideas when it exists).
- Needed for this task's ACs → it is in scope. If it changes behavior the spec did not foresee, it is an amendment.

The test: "Is this required by the ACs this task covers?" If not, don't touch it.

## Blast radius

Approvals authorize **local** edits and commits only. Stop and get an explicit go-ahead for that specific action before:

- `git push`, force-push, opening or merging PRs (unless the user already asked for exactly that)
- deploys, releases, publishing packages
- migrations or writes against shared, staging or production data
- sending messages, emails, webhooks or any external side effect
- deleting branches, files outside the task, or data

At CRITICAL, every irreversible step from the plan's Rollback is approved individually when it runs, with the rollback restated.

## Failure handling

- Gate red after three honest attempts at the same failure → stop and report what you tried and what you suspect. Do not thrash.
- A dependency task turns out wrong → fix it as its own commit referencing that task, then continue.
- Blocked by an external factor (credentials, a service down) → record it in the Handoff and tell the user.

## After the last task

Run the full gate (or cite the last green full gate at the current `HEAD`), then go straight to [verify.md](verify.md). Verification is part of finishing, not a separate request.
