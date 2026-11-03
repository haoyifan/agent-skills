---
name: one-clean-implementation
description: Use when a previous investigation produced a list of related problems and the fix must converge on a single canonical implementation used by every call site — triggers include "fix all the things you found one by one", "one and only one clean implementation", "architecturally clean fix, not a bandaid", "have reviewer agents review it independently", and "babysit the PR until it's merged".
metadata:
  short-description: Converge findings into one canonical implementation, review-gated, driven to merge
---

# Skill: one-clean-implementation

Takes a list of findings that share a root cause (duplicated logic,
divergent copies of the same behavior, accumulated per-site bandaids),
converges them into **exactly one** implementation that every call site
uses, gets the design and the diff reviewed by **independent** agents
who verify facts themselves, and drives the PR to merge.

The deliverable is not "N findings patched." It is "one
implementation exists, every caller uses it, the old paths are gone,
and the PR is merged."

## When to use

Use when the user says any of:
- "work on all the things you found one by one to fix this"
- "one and only one clean implementation used by all the places"
- "I want an architecturally clean fix, not a bandaid"
- "take as much time as you want to refactor to prepare"
- "have reviewer agents review the proposal / the fix"
- "reviewers should be independent and verify facts themselves"
- "babysit until the PR is merged"

Also use when you have just produced an investigation whose findings
are N symptoms of one missing abstraction.

**Do not use when:**
- The findings live in a written audit report file → use `audit-fix`
  (per-finding minimal commits, no convergence requirement).
- It is a single localized bug with one call site → just fix it.
- The right answer genuinely is N independent fixes with nothing in
  common → say so and fix them; don't manufacture an abstraction.

## Arguments

- `--findings <path|inline>` — the findings list. Defaults to the
  findings produced earlier in this conversation.
- `--target <path>` — repo/codebase root (default: cwd)
- `--reviewers <n>` — independent reviewers per gate (default: 3)
- `--propose-only` — stop after the reviewed proposal; do not implement
- `--no-merge` — stop after the PR is opened and green; do not merge

## Workflow

### Phase 0 — Build the coverage ledger

Nothing may be silently dropped. Before any design work:

```
1. ENUMERATE every finding as an explicit row with an ID (F-001, ...),
   even if you produced them yourself five minutes ago. Findings that
   exist only in prose get forgotten.

2. RE-VERIFY EACH ONE against the current code. Findings from an
   earlier agent (or an earlier you) are hypotheses, not facts. Open
   the file. Read the surrounding code, not just the cited line.
   Classify: VALID / STALE (moved — record new location) /
   ALREADY_FIXED / INVALID (false positive, say why).

3. PRINT the ledger. Every row carries a status and, later, a
   resolution. This table is reprinted at the end; a finding with no
   resolution is an unfinished task, not an acceptable omission.
```

### Phase 1 — Find the one implementation

```
1. INVENTORY THE VARIANTS. Grep the whole repo for every existing
   implementation of the behavior — including the near-misses that
   look different (different names, inlined copies, a helper that
   wraps a copy, a test-only duplicate). Record file:line for each.

2. INVENTORY THE CALL SITES. Every caller of every variant. This list
   is the migration checklist; incompleteness here is the single most
   common way this work fails.

3. DIFF THE SEMANTICS. Where variants disagree (error handling,
   edge-case behavior, defaults, ordering, timeouts), write down each
   disagreement explicitly. Every disagreement is a decision: which
   behavior is correct, and is any caller depending on the other one?
   Unresolvable disagreements are escalation candidates (see below).

4. NAME THE OWNER. One module/type/function that will own this
   behavior. If you cannot state in one sentence what it owns and what
   it does not, the abstraction is wrong — keep looking.
```

### Phase 2 — Written proposal

Write the proposal to a file before writing any implementation code.
Required contents:

- **Root cause** — the one structural reason all findings exist.
- **Canonical design** — the owner, its interface, its invariants.
- **Why this and not the alternatives** — including why the local
  bandaid was rejected, and the honest cost of the clean fix.
- **Variant table** — every existing implementation → deleted /
  becomes a thin delegate / kept (with justification).
- **Call-site migration table** — every call site → how it changes.
- **Preparatory refactors** — the mechanical moves that must land
  first so the real change is small and reviewable. Taking extra
  refactoring steps to make the final change clean is expected, not
  scope creep.
- **Test plan** — what proves the convergence, including a test that
  fails if a second implementation reappears where practical.
- **Rollout / compatibility** — migration, flags, back-compat. Any
  shim must have a named removal condition.
- **Findings coverage** — F-ID → which part of the design resolves it.
- **Open questions for the user** — see Escalation.

### Phase 3 — Independent review of the proposal

Spawn `--reviewers` agents **in a single message** so they run
concurrently. Each gets the Reviewer Independence Contract plus the
Proposal Reviewer Brief. Give them the proposal and the repo — never
your summary of the code.

```
Collect verdicts → reconcile:
  BLOCKER  → must be resolved before implementation
  MAJOR    → resolve or record an explicit accepted-risk with reasoning
  MINOR/NIT → fold in if cheap

Disagreements between reviewers are resolved by reading the code
yourself, not by majority vote.

Revise the proposal, then RE-REVIEW with fresh agents. Repeat until a
round returns zero BLOCKERs. Do not start implementing during a review
round.
```

### Phase 4 — Implement

```
1. LAND PREPARATORY REFACTORS FIRST, as separate commits. Pure moves
   and renames stay pure — no behavior change mixed into a move
   commit.

2. BUILD THE CANONICAL IMPLEMENTATION with its tests.

3. MIGRATE EVERY CALL SITE from the Phase 1 checklist. Tick them off
   individually.

4. DELETE THE OLD IMPLEMENTATIONS. Not deprecated, not left "for
   safety", not kept because a test still uses it — delete, and fix
   the test. If something genuinely must stay, it is a delegate with
   no logic of its own.

5. PROVE THE CONVERGENCE. Grep for the old symbols and paths. Zero
   remaining implementations, or the phase is not done.

6. RUN THE TESTS, the linter, and the formatter the repo actually
   uses. Read the output.
```

### Phase 5 — Independent review of the diff

Fresh agents — never the ones who wrote the code, never the ones who
reviewed the proposal. Same single-message fan-out. Each gets the
Reviewer Independence Contract plus the Implementation Reviewer Brief,
the diff, the proposal, and the original findings ledger.

Reconcile exactly as in Phase 3: fix BLOCKERs, re-review with fresh
agents, repeat until a round is clean.

### Phase 6 — Babysit to merge

```
1. If the repo has its own PR-driving skill or documented merge
   process (change manifests, CODEOWNERS, merge queue, admin-merge
   rules), FOLLOW IT — it wins over this phase.

2. Open the PR. Body states: root cause, what is now canonical, what
   was deleted, findings covered, how it was reviewed.

3. Monitor CI to completion. A failure is investigated, not retried
   blindly.

4. Address human and bot review comments. Push fixes; re-run the
   Phase 5 review if the change is substantive.

5. Rebase as main moves. Re-check CI after every rebase.

6. Merge only when CI is green and required approvals exist. Verify
   the merge landed (the PR is closed and the commit is on main)
   before reporting it merged.

7. Do not go idle while the PR is open. Poll, or wait on the checks —
   "waiting for CI" is not a stopping point.
```

### Phase 7 — Final report

Reprint the coverage ledger with resolutions:

| ID | Finding | Status | Resolved by | Verified |
|---|---|---|---|---|
| F-001 | ... | FIXED | canonical `X::do()` + 4 call sites migrated | reviewer R2 confirmed |
| F-003 | ... | INVALID | false positive — code already did this | — |

Then state plainly: implementations before → after, call sites
migrated, code deleted, tests added, PR number and merge state,
anything deliberately left out and why.

## Reviewer Independence Contract

Prepend this to **every** reviewer agent's prompt.

```
You are an independent reviewer. The author's claims are hypotheses,
not evidence. Your job is to verify them yourself.

1. VERIFY, DON'T TRUST. For every claim — "all call sites migrated",
   "the old path is gone", "tests cover this", "behavior is
   unchanged" — go find out yourself. Open the files. Grep the repo.
   Run the tests and read the output. If you did not check it, you may
   not agree with it.

2. THE AUTHOR'S SUMMARY IS NOT INPUT. Nothing in their description
   counts as a fact about the code. Where the summary and the code
   disagree, the code wins and that disagreement is itself a finding.

3. EVERY FINDING NEEDS EVIDENCE: file:line, or the exact command you
   ran and what it printed. No evidence, no finding.

4. NO RUBBER STAMPS. If you report no issues, you must still list
   what you checked and how you checked it — the greps you ran, the
   files you read, the tests you executed. An approval with no
   verification trail is a failed review.

5. SAY SO WHEN YOU CANNOT VERIFY. "Could not verify X because Y" is a
   valid and useful result. Guessing is not.

6. SEVERITY: BLOCKER (ship-stopping: incorrect, incomplete
   convergence, regression, missing migration) / MAJOR (real problem,
   arguable timing) / MINOR / NIT.
```

### Proposal Reviewer Brief

```
Review this design proposal against the actual codebase.

1. IS THE ROOT CAUSE RIGHT? Read the findings and the code. Would this
   design actually eliminate all of them, or only the symptoms cited?

2. IS THE INVENTORY COMPLETE? Independently grep for other
   implementations and other call sites of this behavior. Missing
   variants and missing callers are BLOCKERs. Assume the author's list
   is incomplete until your own search agrees with it.

3. IS THE ABSTRACTION RIGHT? Does the proposed owner have one clear
   responsibility? Does it force unrelated cases through one path? Is
   it over-general — parameters and hooks that exist for hypothetical
   callers? Both wrong-abstraction directions are findings.

4. DOES ANYTHING SURVIVE THAT SHOULDN'T? Any variant kept, any
   compatibility shim without a removal condition, any call site with a
   special case — challenge it.

5. WHAT BREAKS? Semantic differences between the old variants that
   callers depend on. Data, persistence, wire, or config compatibility.
   Concurrency and failure modes.

6. IS IT TESTABLE, and does the test plan actually prove convergence?

7. WHAT IS MISSING ENTIRELY that a careful engineer would require?

Verdict per point, with severity and evidence.
```

### Implementation Reviewer Brief

```
Review this diff against the proposal, the findings, and the codebase.

1. CONVERGENCE, VERIFIED BY YOU. Grep for every old symbol, function,
   file, and pattern the proposal said would be deleted. Any survivor
   is a BLOCKER. Count the implementations that exist now — it must be
   exactly one.

2. MIGRATION COMPLETENESS. Independently enumerate the call sites of
   this behavior in the post-change tree. Every one must go through
   the canonical path. Search for callers the author may not have
   listed — including tests, scripts, generated code, and other
   languages/services in the repo.

3. FINDINGS COVERAGE. For each original finding, locate the code that
   resolves it and confirm it does. A finding "handled by the general
   design" without a concrete resolution is not resolved.

4. CORRECTNESS. Behavior preserved where it should be, and changed
   deliberately where it should be. Edge cases from the old variants
   that the new one drops. Error handling, concurrency, resource
   lifetimes, ordering.

5. DIFF HYGIENE. Are the pure moves actually pure? Is unrelated change
   smuggled in? Does the code match the repo's existing style?

6. TESTS. Run them. Do they exercise the new path, or only pass? Would
   they fail if the convergence regressed?

7. LEFTOVERS. Dead code, stale comments, stale docs, unused imports,
   TODOs pointing at the thing that was just deleted.

Verdict per point, with severity and evidence.
```

## Escalation — when to stop and ask the user

Ask, in one message, with a recommendation attached — then keep working
on everything that does not depend on the answer:

- Two variants disagree semantically and the correct behavior is a
  product decision, not a code decision.
- The clean fix requires a schema/API/wire change, a data migration,
  or a coordinated deploy.
- The blast radius crosses a team, service, or repo boundary the user
  did not have in scope.
- A finding, if fixed properly, contradicts a documented decision.
- Reviewers disagree on a BLOCKER and the code does not settle it.
- The convergence would require breaking an external contract.

Do not escalate to avoid work, and do not silently narrow scope
instead of escalating.

## Rules

1. **One implementation at the end.** Exactly one. Verified by grep,
   not by belief. This is the definition of done.
2. **Every finding gets a resolution row.** Fixed, or invalid with a
   reason. "Follow-up PR" is not a resolution unless the user agreed.
3. **Delete, don't deprecate.** Old paths are removed in this change.
   A shim requires a named removal condition.
4. **No per-call-site special cases.** A caller that "needs" a variant
   means the abstraction is wrong. Redesign, don't branch.
5. **Refactor freely to make the change clean.** Preparatory
   refactoring is part of the job, in its own commits. Purity of move
   commits is not optional.
6. **Reviewers are independent and fresh.** Never review your own
   work. Never reuse a proposal reviewer for the diff. Never hand a
   reviewer your summary in place of the code.
7. **Design is reviewed before it is built.** No implementation during
   an open review round.
8. **Evidence before assertion.** Ran the tests? Show the output.
   Claim convergence? Show the grep. Claim merged? Show the closed PR
   on main.
9. **Repo process wins.** Local merge governance overrides Phase 6.
10. **Report honestly.** Partial is partial. Anything skipped is named
    in the final report with the reason.

## Red flags — stop, you are rationalizing

| Thought | Reality |
|---|---|
| "This one call site is special, I'll leave it" | Then the abstraction is wrong. Fix the design, not the exception. |
| "I'll keep the old function for compatibility" | Compatibility without a removal condition is a second implementation. |
| "I'll converge the rest in a follow-up PR" | Two implementations shipped. That was the bug. |
| "The reviewer approved it" (given your summary) | They reviewed your prose, not the code. Re-review with the real diff. |
| "Reviewers found nothing, so it's clean" | An approval with no verification trail is a failed review, not a pass. |
| "Tests pass, so it works" | Tests pass on both implementations. Grep for the old one. |
| "The findings list was mine, I don't need to re-verify" | Past-you is another agent. Re-verify against current code. |
| "Refactoring first is scope creep" | The user explicitly asked for it. Bandaids are the scope violation. |
| "It's basically done, I'll report it merged" | Verify the PR is closed and the commit is on main. |
| "CI is running, I'll stop here" | Babysitting means through the merge, not up to it. |

## Completion checklist

- [ ] Every finding has a resolution row in the final ledger
- [ ] Exactly one implementation remains — proven by grep output
- [ ] Every call site migrated — enumerated, not assumed
- [ ] Old implementations deleted; any shim has a removal condition
- [ ] Proposal reviewed by independent agents, zero BLOCKERs on the
      final round
- [ ] Diff reviewed by different independent agents, zero BLOCKERs on
      the final round
- [ ] Tests, lint, and format run — output read
- [ ] Repo-specific PR requirements satisfied
- [ ] CI green, PR merged, merge verified on main
- [ ] Final report lists what was deliberately left out and why
