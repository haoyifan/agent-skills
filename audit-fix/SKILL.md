---
name: audit-fix
description: Verify an audit report's findings against the actual codebase, then implement valid fixes in parallel with one clean commit per item. Cross-validates all fixes afterward. Works with refactor-audit, performance-audit, and security-audit reports.
metadata:
  short-description: Verify and implement audit report findings
---

# Skill: audit-fix

Generic audit report executor. Reads a report produced by any audit
skill (refactor-audit, performance-audit, security-audit), verifies
each finding against the actual codebase, implements valid fixes in
parallel (one clean commit per fix), and cross-validates all changes
when done.

## When to use

Use when the user asks to "fix the audit findings", "implement the
report", "apply the audit recommendations", "fix the refactor report",
"apply security fixes", "implement the performance fixes", or
references `/audit-fix`. Requires an existing audit report file.

## Arguments

- `--report <path>` — path to the audit report (required). Accepts reports from refactor-audit, performance-audit, or security-audit.
- `--target <path>` — path to the codebase (default: current working directory)
- `--filter <severity|priority>` — minimum severity or priority to fix (default: all). Examples: `--filter P0,P1` for refactor reports, `--filter critical,high` for security/performance reports.
- `--dry-run` — verify findings and produce a fix plan, but don't implement changes
- `--skip <id,...>` — comma-separated finding IDs to skip (e.g., `--skip R-003,P-007`)
- `--only <id,...>` — comma-separated finding IDs to fix (fix only these, ignore the rest)

## Example invocations

Fix all findings from a refactor audit:
```
/audit-fix --report ./REFACTOR-AUDIT-REPORT.md
```

Fix only critical and high security findings:
```
/audit-fix --report ./SECURITY-AUDIT-REPORT.md --filter critical,high
```

Dry run to see what would be fixed:
```
/audit-fix --report ./PERFORMANCE-AUDIT-REPORT.md --dry-run
```

Fix specific items:
```
/audit-fix --report ./REFACTOR-AUDIT-REPORT.md --only R-001,R-004,R-007
```

## Workflow

### Phase 0: Report Ingestion & Verification

Before fixing anything, verify the report against the actual codebase.
Audit reports are a snapshot in time — code may have changed since the
report was generated.

```
1. PARSE THE REPORT
   - Detect report type from content (refactor/performance/security)
   - Extract all findings with their metadata:
     - Finding ID (R-001, P-001, C-001, etc.)
     - Title and description
     - Severity/priority and confidence
     - File:line location(s)
     - Current code / problem description
     - Suggested fix / recommended change
     - Affected files list
     - Domain (which audit agent produced this)
   - For refactor reports, also extract:
     - Refactoring clusters (multiple findings resolved by one change)
     - Effort estimates (S/M/L/XL)
   - Apply --filter, --skip, and --only to narrow the working set

2. VERIFY EACH FINDING
   For each finding in the working set, read the actual code at the
   referenced location(s) and classify:

   - VALID: the issue exists as described, the location is correct,
     and the suggested fix is applicable
   - STALE: the code has changed since the report — the issue may
     still exist but the location or details are wrong. Attempt to
     find the current location of the code and re-verify.
   - ALREADY_FIXED: the issue has been resolved since the report
     was generated (code no longer exhibits the problem)
   - INVALID: the finding is incorrect — the code does not have the
     issue described (false positive from the audit), or the
     suggested fix would introduce a bug
   - RISKY: the finding is valid but the suggested fix is too risky
     to apply automatically (could break functionality, requires
     manual testing, or touches critical security code). Flag for
     manual review.
   - NEEDS_CONTEXT: can't determine validity without more context
     (the issue depends on runtime behavior, external systems, or
     business requirements not visible in the code)

   For each finding, read enough surrounding code to understand
   context — don't just check if the referenced line exists. A
   finding about a function being too long requires reading the
   entire function. A finding about missing error handling requires
   understanding the error model of the module.

3. PRODUCE VERIFICATION SUMMARY
   Print a summary table to the conversation:

   | Status | Count | Finding IDs |
   |--------|-------|-------------|
   | VALID | N | R-001, R-003, ... |
   | STALE | N | R-005 |
   | ALREADY_FIXED | N | R-002 |
   | INVALID | N | R-008 |
   | RISKY | N | R-004 |
   | NEEDS_CONTEXT | N | R-009 |

   For INVALID and RISKY findings, explain WHY in 1-2 sentences.
   For STALE findings, note the current location if found.

   If --dry-run is set, stop here and print the fix plan without
   implementing.
```

### Phase 1: Fix Planning

After verification, plan the execution order for VALID findings.

```
1. IDENTIFY INDEPENDENT vs DEPENDENT FIXES
   Two fixes are DEPENDENT if:
   - They modify the same file in overlapping regions
   - One fix changes a function signature that another fix calls
   - One fix moves or renames code that another fix references
   - They belong to the same refactoring cluster

   Two fixes are INDEPENDENT if:
   - They touch completely different files
   - They touch the same file but in non-overlapping regions with
     no shared symbols
   - Their changes don't affect each other's correctness

2. GROUP REFACTORING CLUSTERS
   For refactor-audit reports, respect the cluster groupings from
   the report. A cluster is multiple findings resolved by a single
   refactoring action — these become ONE commit, not multiple.

   For other report types, identify natural groupings:
   - Multiple findings in the same function/class that are best
     addressed together
   - A security fix that requires changes in multiple locations to
     be effective (e.g., adding parameterized queries everywhere
     a raw SQL pattern appears)

3. ORDER BY PRIORITY
   - Refactor reports: P0 → P1 → P2 → P3
   - Security reports: CRITICAL → HIGH → MEDIUM → LOW → INFO
   - Performance reports: CRITICAL → HIGH → MEDIUM → LOW → INFO
   Within the same priority, CONFIRMED findings come before LIKELY
   or POSSIBLE.

4. BUILD THE EXECUTION PLAN
   Group fixes into parallel batches:
   - Batch 1: all independent P0/CRITICAL fixes (run in parallel)
   - Batch 2: all independent P1/HIGH fixes (run after batch 1)
   - Continue until all fixes are scheduled
   - Dependent fixes within the same batch are serialized within
     a single agent

   Print the execution plan:
   - How many batches
   - How many parallel agents per batch
   - Which findings each agent will fix
   - Estimated total commits
```

### Phase 2: Parallel Fix Execution

Execute the fix plan batch by batch. Each batch runs all its agents
in parallel. Wait for a batch to complete before starting the next.

```
For each batch:
  For each independent fix group in the batch:
    Spawn an agent with:
    - subagent_type: "general-purpose"
    - The finding(s) to fix (full description, location, suggested fix)
    - The target path
    - Explicit instructions (see Fix Agent Brief below)

  Wait for ALL agents in the batch to complete.
  Verify no merge conflicts between agents' changes.
  If conflicts exist, resolve them before proceeding to next batch.
```

### Phase 3: Cross-Validation

After all fixes are implemented, spawn validation agents to verify
the changes.

```
1. SPAWN VALIDATION AGENTS (in parallel)
   Divide the completed fixes into groups and spawn one validation
   agent per group. Each agent receives:
   - The list of findings that were fixed
   - The git diff for the relevant commits
   - Instructions to validate (see Validation Agent Brief below)

2. COLLECT VALIDATION RESULTS
   Each validation agent reports:
   - PASS: the fix correctly resolves the finding
   - PARTIAL: the fix addresses the core issue but misses an edge
     case or related location
   - FAIL: the fix doesn't resolve the issue, or introduces a
     regression
   - REGRESSION: the fix introduces a new problem not present
     before

3. HANDLE FAILURES
   For PARTIAL findings:
   - Note what's missing and flag for follow-up
   For FAIL or REGRESSION findings:
   - Revert the specific commit
   - Note the failure reason
   - Flag for manual implementation

4. PRODUCE FINAL SUMMARY
   Print results to conversation:

   | Finding | Fix Status | Validation | Commit |
   |---------|-----------|------------|--------|
   | R-001 | Implemented | PASS | abc1234 |
   | R-003 | Implemented | PASS | def5678 |
   | R-004 | Skipped (RISKY) | — | — |
   | R-005 | Implemented | PARTIAL | ghi9012 |
   | R-008 | Skipped (INVALID) | — | — |

   Followed by:
   - Total findings in report: N
   - Verified valid: N
   - Implemented: N
   - Validated PASS: N
   - Validated PARTIAL: N (with details)
   - Validated FAIL: N (with details)
   - Skipped (INVALID/ALREADY_FIXED/RISKY/NEEDS_CONTEXT): N
```

## Agent Briefs

### Fix Agent Brief

Each fix agent receives this brief, prefixed with the specific
finding(s) it needs to implement.

```
You are implementing a specific fix from an audit report. Your job
is to make a clean, minimal code change that resolves the finding
without introducing regressions.

RULES:

1. ONE COMMIT PER FINDING (or per cluster if multiple findings are
   grouped). The commit should be atomic — all changes for this
   finding in one commit, no changes for other findings mixed in.

2. MINIMAL CHANGES. Fix exactly what the finding describes. Don't
   refactor surrounding code, don't add features, don't "improve"
   unrelated code you happen to see. If the finding says "extract
   this duplicated block into a function," extract it and nothing
   more.

3. PRESERVE BEHAVIOR. The fix should not change observable behavior
   unless that's explicitly the point (e.g., a security fix that
   changes error responses, a performance fix that changes from
   synchronous to asynchronous). If you're refactoring, the tests
   should still pass without modification.

4. MATCH THE CODEBASE STYLE. Use the same formatting, naming
   conventions, import style, and patterns as the surrounding code.
   Don't impose a different style because you think it's better.

5. COMMIT MESSAGE FORMAT. Use this format:
   ```
   <type>: <short description of what changed>

   Resolves: <finding-ID(s)>
   Domain: <audit domain>

   <1-2 sentence explanation of why this change was needed and
   what it fixes>

   Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
   ```

   Where <type> is one of:
   - refactor: code quality improvements (from refactor-audit)
   - perf: performance improvements (from performance-audit)
   - security: security fixes (from security-audit)
   - fix: bug fixes discovered during audit

6. VERIFY BEFORE COMMITTING. After making changes:
   - Read the modified code to verify it's correct
   - Check that imports/references are updated if you moved/renamed
     anything
   - Verify no syntax errors by scanning the code
   - If tests exist and can be run quickly, run them

7. HANDLE UNCERTAINTY. If the suggested fix from the report seems
   wrong or incomplete after reading the actual code:
   - Implement a better fix if you're confident
   - Note what you changed differently and why in the commit message
   - If you're not confident, skip the finding and report why

8. DON'T BREAK OTHER FIXES. Be aware that other agents are fixing
   other findings in parallel. Don't modify files or functions that
   are outside your finding's scope. If your fix requires changes
   to code that another finding also touches, note the conflict
   and make only your part of the change.
```

### Validation Agent Brief

Each validation agent receives this brief, along with the findings
and their diffs.

```
You are cross-validating fixes applied from an audit report. For
each fix, you need to determine if it correctly resolves the
reported finding without introducing regressions.

For each fix you're validating:

1. READ THE ORIGINAL FINDING. Understand what the audit reported
   as the problem, where it was, and what fix was suggested.

2. READ THE DIFF. Review the actual code change that was made.
   Check:
   - Does the change address the root cause, not just the symptom?
   - Is the change complete? (All affected locations updated,
     not just some?)
   - Is the change correct? (No logical errors, no typos, no
     missing imports?)
   - Does it match the codebase's style and conventions?

3. CHECK FOR REGRESSIONS. Look at the surrounding code and ask:
   - Could this change break any callers of the modified code?
   - Does it change function signatures, return types, or error
     behavior that other code depends on?
   - Does it modify shared state or configuration that affects
     other modules?
   - For security fixes: does the fix introduce a different
     vulnerability?
   - For performance fixes: does the fix trade one bottleneck for
     another?
   - For refactoring: does the change preserve all existing behavior?

4. VERIFY COMPLETENESS. For findings that span multiple locations:
   - Were ALL locations addressed, or only some?
   - If the finding was about duplication, is the duplication
     actually eliminated (not just reduced)?
   - If the finding was about missing error handling, are ALL
     error paths covered?

5. CHECK CROSS-FIX INTERACTIONS. If multiple fixes touch related
   code:
   - Do they conflict or create inconsistencies?
   - Did one fix undo or invalidate another fix?
   - Are there merge artifacts or duplicated changes?

6. RUN TESTS if available and quick to run. Report results.

REPORT for each fix:
- Finding ID
- Verdict: PASS / PARTIAL / FAIL / REGRESSION
- If not PASS: specific explanation of what's wrong or missing
- If REGRESSION: describe the new issue introduced
```

## Report Type Detection

The skill auto-detects the report type from content:

| Report Type | Detection Pattern |
|---|---|
| refactor-audit | Contains "Refactor Audit Report" or P0/P1/P2/P3 priority tiers, or finding IDs like `R-NNN` or `F-{domain}-NNN` |
| performance-audit | Contains "Performance Audit Report" or finding IDs like `P-NNN`, or severity levels (CRITICAL/HIGH/MEDIUM/LOW/INFO) with performance domains |
| security-audit | Contains "Security Audit Report" or finding IDs like `C-NNN`/`H-NNN`/`M-NNN`/`L-NNN`, or references vulnerability types (SQLi, XSS, SSRF, etc.) |

When the report type is ambiguous, ask the user.

## Rules

1. **Verify before fixing.** Never implement a fix without first
   reading the actual code at the referenced location. Audit reports
   can contain false positives, stale references, and incorrect
   suggestions. Phase 0 is not optional.

2. **One commit per finding.** Each fix is an atomic commit. This
   makes it easy to revert individual changes if a fix causes
   problems. The only exception is refactoring clusters — multiple
   related findings resolved by a single action become one commit.

3. **Parallel when independent, serial when dependent.** Fixes that
   touch different code areas run in parallel for speed. Fixes that
   overlap are serialized to avoid conflicts. Don't sacrifice
   correctness for parallelism.

4. **Minimal changes.** Fix agents must resist the urge to "improve"
   code beyond what the finding describes. Scope creep in fixes
   makes cross-validation harder and increases regression risk.

5. **Cross-validate everything.** Every implemented fix gets
   validated by a different agent than the one that implemented it.
   This catches bugs, incomplete fixes, and regressions that the
   implementing agent might miss.

6. **Revert on failure.** If cross-validation finds a FAIL or
   REGRESSION, revert the commit rather than trying to fix the fix.
   Flag it for manual implementation. Recursive fix attempts
   compound errors.

7. **Preserve the report.** Don't modify or delete the original
   audit report. The report is the source of truth and audit trail.

8. **Security fixes are special.** For security-audit findings:
   - CRITICAL and HIGH findings with CONFIRMED confidence should
     be prioritized above all other work
   - Be extra careful with security fixes — a "fix" that doesn't
     fully resolve the vulnerability is worse than no fix (it
     creates false confidence)
   - Never commit code that could introduce a new vulnerability
     while fixing another

9. **Test when possible.** If the project has a test suite, run it
   after each batch of fixes. If tests fail, identify which fix
   caused the failure and revert it.

10. **Report transparency.** The final summary must honestly report
    what was fixed, what was skipped, and what failed. Don't
    overstate success — a PARTIAL validation means the fix is
    incomplete, not done.

## Orchestrator Implementation

The orchestrator (main conversation) executes this sequence:

```
1. PARSE ARGUMENTS
   - Validate --report exists and is readable
   - Validate --target exists (or use cwd)
   - Parse --filter, --skip, --only constraints

2. REPORT INGESTION (Phase 0, step 1)
   - Read the report file
   - Detect report type
   - Extract all findings with metadata
   - Apply filters to get working set

3. VERIFICATION (Phase 0, step 2)
   - For each finding in working set:
     - Read the code at referenced location(s)
     - Classify as VALID/STALE/ALREADY_FIXED/INVALID/RISKY/NEEDS_CONTEXT
   - This step can be parallelized: spawn verification agents that
     each handle a subset of findings
   - Print verification summary table

4. FIX PLANNING (Phase 1)
   - If --dry-run, stop after printing the plan
   - Build dependency graph between fixes
   - Group into parallel batches
   - Print execution plan

5. FIX EXECUTION (Phase 2)
   - For each batch:
     - Spawn fix agents in parallel (one per independent fix group)
     - Wait for all agents in batch to complete
     - Verify no conflicts
     - Proceed to next batch

6. CROSS-VALIDATION (Phase 3)
   - Spawn validation agents in parallel
   - Collect results
   - Revert any FAIL/REGRESSION commits
   - Print final summary table

7. FINAL SUMMARY
   - Print overall statistics
   - List any findings that need manual attention
   - Note any reverted fixes
```

## Agent Spawning Details

**Verification agents** (Phase 0):
- `subagent_type: "general-purpose"`
- Each receives a subset of findings to verify
- READ-ONLY — no code modifications
- Returns classification for each finding with explanation

**Fix agents** (Phase 2):
- `subagent_type: "general-purpose"`
- Each receives specific finding(s) to implement
- Includes the full Fix Agent Brief
- Includes the finding description, location, and suggested fix
- Includes the target path
- Must create exactly one commit per finding (or per cluster)

**Validation agents** (Phase 3):
- `subagent_type: "general-purpose"`
- Each receives a group of implemented fixes with their diffs
- Includes the full Validation Agent Brief
- Includes the original finding descriptions
- READ-ONLY — validates but does not modify code
- Returns verdict per fix (PASS/PARTIAL/FAIL/REGRESSION)

All agents within a phase are spawned in a SINGLE message with
multiple Agent tool calls so they run concurrently. Batches within
Phase 2 are sequential (wait for batch N to complete before starting
batch N+1).
