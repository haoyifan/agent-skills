# Skill: dev-team

Multi-agent development team orchestration. Coordinates a Developer, two
Reviewers, and a Tester to build a project incrementally with enforced
code review and testing gates.

## When to use

Use when the user asks to "build this project with agents", "set up a dev
team", "implement this design", or references `/dev-team`. Requires a
design doc as input. Test plan and progress file are optional -- if not
provided, the Manager generates them from the design doc before starting
development.

## Roles

| Role | Count | Responsibility |
|---|---|---|
| **Manager** | 1 | Orchestrates the loop, assigns tasks, tracks progress, resolves blockers |
| **Developer** | 1 | Writes code in the project worktree, runs self-review before committing (`implementer` persona) |
| **Reviewer A** | 1 | Reviews for correctness and architecture alignment against design doc (`reviewer` persona) |
| **Reviewer B** | 1 | Reviews for edge cases, error handling, and test coverage (`reviewer` persona) |
| **Tester** | 1 | Runs tests, reports results. Has exclusive access to shared test infra (`general-purpose` subagent) |

## Workflow

### Phase 0: Bootstrap (runs once at project start)

Before the development loop begins, the Manager ensures all project
artifacts exist:

```
1. Read the design doc (required -- fail if missing)
2. If no test plan exists:
   - Read the design doc's implementation phases, data flows, and failure model
   - Generate a test plan with levels (unit, integration, end-to-end, failure
     injection, performance) covering the key correctness properties
   - Write to {design-doc-dir}/{project-name}-tests.md
   - Ask user to review before proceeding
3. If no progress file exists:
   - Read the design doc's implementation phases
   - Break each phase into tasks of ~50-200 lines each
   - Generate a progress file with the task board
   - Write to {design-doc-dir}/{project-name}-progress.md
4. Create the project worktree from origin/main
5. Begin the development loop
```

### Development loop

The Manager runs the following loop for each task:

```
1. ASSIGN
   - Pick the next pending task from the progress file
   - Mark it in_progress
   - Spawn Developer agent with:
     - Task description and acceptance criteria
     - Design doc and test doc paths
     - Instruction to implement in the project worktree, run /self-review, commit
     - Max ~200 lines per task

2. REVIEW (parallel)
   - Spawn Reviewer A and Reviewer B in parallel
   - Both run /review-commit on the Developer's latest commit
   - Reviewer A focuses on: architecture alignment, correctness, design doc compliance
   - Reviewer B focuses on: edge cases, error handling, failure modes, test coverage
   - Both must approve for the task to proceed

3. GATE: REVIEW RESULT
   - If both approve → proceed to GATE: TEST
   - If either requests changes:
     - Consolidate comments from both reviewers
     - Resume Developer agent with the feedback
     - Developer fixes and re-commits
     - Loop back to REVIEW with FRESH reviewer agents (do NOT resume
       previous reviewers). New agents review the entire diff from scratch
       as if they have never seen it before. This prevents bias from prior
       context -- the reviewer must verify not just that feedback was
       addressed, but that the fix didn't introduce new problems.
   - Max 5 review rounds per task. If still not approved, escalate to user.

4. TEST
   - Spawn Tester agent (ensure exclusive access to shared test infra)
   - Run tests relevant to the current task
   - Report pass/fail with output

5. GATE: TEST RESULT
   - If tests pass → proceed to DONE
   - If tests fail:
     - Send test output to Developer
     - Developer fixes
     - Loop back to REVIEW (changes need re-review)
   - Max 5 test-fix cycles. If still failing, escalate to user.

6. DONE
   - Update progress file: mark task done, record review/test results
   - Increment the commit counter

7. AUDIT (every 5 commits)
   - After every 5 commits, spawn a read-only explore agent to audit the
     codebase for refactoring opportunities (duplicated logic, abstractions
     that emerged across tasks, dead code, inconsistent patterns)
   - The audit agent reviews all code written so far in the project worktree
     and produces a list of concrete refactoring suggestions (if any)
   - If refactoring is warranted:
     - Resume the Developer to implement the refactoring as a separate commit
     - The refactoring commit goes through the normal REVIEW and TEST gates
       before proceeding
   - If no refactoring needed, proceed to next task

8. NEXT TASK
   - Proceed to next task (loop back to ASSIGN)
```

## Worktree Strategy

```
main                          ← upstream, untouched
  └── {project-worktree}      ← project branch, Developer commits directly here
```

- The project worktree is created once at project start
- The Developer commits directly to the project branch (no per-task feature
  branches). Since there is only one Developer agent, there are no concurrent
  writes and no merge conflicts. This keeps the git log linear and clean.
- The project worktree is what the user reviews before merging to main

## Progress File Format

The Manager maintains a progress file (markdown) with:

```markdown
# Project Progress

## Current Phase: {phase name}

### Task Board
| # | Task | Status | Review A | Review B | Tests |
|---|---|---|---|---|---|
| 1.1 | Task description | pending/in_progress/review/testing/done | pending/approved/changes | pending/approved/changes | pending/pass/fail |

### Review History
- Task X.Y: {what was found, what was fixed}

### Decisions During Development
- {design questions that came up during implementation}
```

Status values: `pending` → `in_progress` → `review` → `testing` → `done`

## Rules

1. **Commit format.** Each commit must have:
   - Title: `[<area>][<feature>] <short description>` (or whatever commit-title convention your project uses)
   - Body: description of what changed and why
   - `Testing:` section describing what was tested and the results
   Example:
   ```
   [api][users] add email validation to signup endpoint

   Add validate_email() helper. Reject malformed addresses and
   addresses with disallowed domains before persisting the user.

   Testing:
   - Unit tests for valid/invalid email formats
   - Edge cases: empty string, IDN domains, plus-addressing
   - <package test command>: all pass
   ```

2. **Small commits.** Each task is one conceptual change, targeting ~50-200
   lines. This is a soft guideline, not a hard rule -- if a task is the
   minimal indivisible unit and genuinely requires more, that's fine. The
   Manager's job is to break work into the smallest incremental pieces
   that are easy to review. Err on the side of too small, not too large.

3. **No skipping reviews.** Both reviewers must approve. No exceptions.

4. **Tests before merge.** Relevant tests must pass before merging.

5. **Bug fixes are individual commits.** When a test failure reveals a bug,
   the fix must be committed as its own separate commit (not squashed into
   the original task commit) once it is verified to resolve the problem.
   This keeps the history auditable -- reviewers and future readers can see
   what broke and exactly what fixed it.

6. **Design doc is the spec.** Reviewers check code against the design doc.
   If the code deviates, it's either a bug or the design doc needs updating
   (which requires user approval). Code must also follow the project's
   coding standards (e.g., `AGENTS.md` in the repo for project-specific
   style, import conventions, error handling patterns, and visibility
   rules).

7. **Manager never writes code.** It only coordinates and makes decisions.

8. **Escalate, don't spin.** After 5 failed review or test cycles, the
   Manager escalates to the user rather than looping indefinitely.

9. **Exclusive test infra.** Only one agent uses shared test infrastructure
   at a time. The Manager ensures this by serializing test runs.

   **Integration test cluster (optional):**
   The test cluster is specified via the `--test-cluster` argument
   (format: `<kubectl-context>/<namespace>`). If not provided, no
   integration testing against a live cluster is performed —
   only local tests (unit tests, package test commands) run.
   - Get pod name: `kubectl --context <context> -n <namespace> get pods`
   - The Tester agent should use this cluster for integration tests
     that require a running deployed environment.
   - **Post-deploy verification:** After deploying new code to the cluster,
     the Tester MUST verify the running pod is actually using the newly
     deployed code before running any tests. Check pod image tag/digest,
     pod restart time, or logs to confirm the rollout completed. Do not
     assume the deploy took effect — explicitly confirm it.

10. **Minimal comments.** Only comment assumptions, non-obvious cases, and
   tricky situations. Do not comment what the code does (well-named
   identifiers do that). Do not reference tasks, tickets, or callers.
   No verbose comments. If removing the comment wouldn't confuse a future
   reader, don't write it.

11. **TODO format.** All TODO comments must include the author attribution:
   `TODO(<author-id>)` (or whatever convention your project uses). Example:
   `// TODO(janedoe): handle the case where the cache is already populated`

12. **Tests ship with code.** Every task that adds functionality must include
   unit tests for that functionality. Tests are part of the deliverable,
   not a separate task. Reviewers must check that tests exist and cover
   the key correctness properties. Separate integration test tasks at the
   end of each phase verify that the phase works end-to-end -- these are
   the only "test-only" tasks in the progress file.

13. **Re-read progress file each iteration.** The Manager re-reads the
   progress file before picking the next task, rather than relying on
   conversation history. This keeps the Manager grounded as context
   accumulates across many agent spawns.

14. **Resumable.** The skill can be re-invoked with the same arguments to
   resume a partially completed project. The Manager reads the progress
   file and continues from the first pending task.

## Arguments

When invoking this skill, provide:

- `--design-doc <path>` — the design specification (required)
- `--test-doc <path>` — the test plan (optional; generated from design doc if missing)
- `--progress <path>` — the progress tracking file (optional; generated from design doc if missing)
- `--project-worktree <name>` — git worktree name for the project (optional; derived from design doc filename if missing)
- `--test-cluster <context/namespace>` — k8s cluster for integration tests (optional; format: `<kubectl-context>/<namespace>`, e.g. `my-context/my-namespace`). If omitted, only local tests run.
- `--review-skill <path>` — skill to use for code review (default: review-commit)

## Example invocations

Minimal (only design doc, local tests only):
```
/dev-team --design-doc ~/path/to/design.md
```

With a test cluster for integration testing:
```
/dev-team --design-doc ~/path/to/design.md \
          --test-cluster my-context/my-namespace
```

Full (all artifacts pre-created):
```
/dev-team --design-doc ~/path/to/design.md \
          --test-doc ~/path/to/design-tests.md \
          --progress ~/path/to/design-progress.md \
          --project-worktree my-project \
          --test-cluster my-context/my-namespace
```
