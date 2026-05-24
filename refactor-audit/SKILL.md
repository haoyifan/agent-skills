---
name: refactor-audit
description: Multi-agent code quality audit — finds duplication, bandaid accumulation, poor modularity, wrong abstractions, naming/clarity issues, type safety gaps, test quality problems, data model smells, and concurrency anti-patterns. Produces a prioritized refactoring action plan with concrete code references.
metadata:
  short-description: Multi-agent refactoring opportunity audit
---

# Skill: refactor-audit

Multi-agent code quality audit orchestrator. Spawns parallel specialist
agents to find concrete refactoring opportunities across a codebase —
duplication, accumulated bandaids, SRP violations, wrong abstractions,
unclear naming, cross-module coupling, type safety gaps, test quality
issues, data model smells, and concurrency anti-patterns. Produces a
prioritized action plan where each recommendation includes specific
file:line references, before/after sketches, and effort estimates.

## When to use

Use when the user asks to "audit code quality", "find refactoring
opportunities", "simplify this codebase", "clean up the code", "reduce
complexity", "find duplication", "improve modularity", or references
`/refactor-audit`. Works on any codebase in any language.

## Arguments

- `--target <path>` — path to the codebase to audit (default: current working directory)
- `--focus <domain,...>` — comma-separated list of domains to audit (default: all). Valid domains: `duplication`, `functions`, `modules`, `errors`, `naming`, `architecture`, `types`, `tests`, `data-model`, `concurrency`
- `--report <path>` — output path for the final report (default: `{target}/REFACTOR-AUDIT-REPORT.md`)
- `--depth <shallow|standard|deep>` — audit depth (default: `standard`). `shallow` skips vendored/generated code and limits to top-level modules. `deep` traces data flows across module boundaries and analyzes git history for bandaid patterns.

## Example invocations

Audit the current repo:
```
/refactor-audit
```

Audit a specific directory, focused on duplication and architecture:
```
/refactor-audit --target ./src --focus duplication,architecture
```

Deep audit with custom report path:
```
/refactor-audit --target ./my-app --depth deep --report ./reports/quality.md
```

Audit type safety and test quality:
```
/refactor-audit --focus types,tests
```

## Audit Domains & Agents

The orchestrator spawns one agent per domain. All agents run in parallel.
Each agent audits the codebase through a specific lens and produces
structured findings.

| Agent | Domain | Focus |
|---|---|---|
| **Duplication & Extraction** | `duplication` | Copy-pasted code, repeated patterns, similar-but-slightly-different implementations that should be unified |
| **Function & Method Quality** | `functions` | Long functions, too many parameters, mixed abstraction levels, deep nesting, side effects, feature envy |
| **Module & Class Design** | `modules` | SRP violations, god classes/modules, poor cohesion, tight coupling, missing or wrong boundaries |
| **Error Handling & Robustness** | `errors` | Inconsistent error strategies, swallowed exceptions, bandaid try/catch, null returns, missing edge cases |
| **Naming & Clarity** | `naming` | Misleading names, magic numbers, comments compensating for bad code, dead code, unclear intent, configuration sprawl |
| **Cross-Module Architecture** | `architecture` | Interface bloat, unnecessary indirection, data flow complexity, accumulated bandaids across boundaries, module merge/split opportunities, dependency direction violations |
| **Type Safety & API Contracts** | `types` | Overly permissive types, stringly-typed APIs, missing annotations, inconsistent API shapes, leaky abstractions, type coercion pitfalls |
| **Test Quality** | `tests` | Empty assertions, implementation-coupled tests, missing test boundaries, flaky patterns, dead test code, missing edge case coverage |
| **Data Model & Schema Quality** | `data-model` | Unjustified denormalization, missing constraints, naming inconsistencies, orphaned fields, schema-code drift, missing indexes |
| **Concurrency & Async Patterns** | `concurrency` | Callback hell, race conditions, mismatched async patterns, missing cancellation, unstructured concurrency, thread safety issues |

## Language References

Language-specific refactoring patterns are stored as reference files.
During reconnaissance, the orchestrator detects the project's languages
and loads the relevant references to include in agent prompts.

Available references (loaded from this skill's `references/` directory):
- [references/lang-swift.md](references/lang-swift.md) — Swift, SwiftUI, iOS/macOS
- [references/lang-python.md](references/lang-python.md) — Python, Django, Flask, FastAPI, pandas
- [references/lang-javascript-typescript.md](references/lang-javascript-typescript.md) — JavaScript, TypeScript, React, Node.js
- [references/lang-go.md](references/lang-go.md) — Go
- [references/lang-rust.md](references/lang-rust.md) — Rust, Tokio
- [references/lang-java-kotlin.md](references/lang-java-kotlin.md) — Java, Kotlin, Spring, JVM
- [references/lang-c-cpp.md](references/lang-c-cpp.md) — C, C++

When a project uses multiple languages, load all relevant references.
Reference files can be added at `references/lang-*.md` and are loaded
during reconnaissance.

## Workflow

### Phase 0: Reconnaissance

Before spawning specialist agents, the orchestrator maps the codebase
to build shared context:

```
1. Identify the codebase structure:
   - Languages and frameworks (package files, build configs)
   - Directory layout and module boundaries
   - Entry points (main files, route definitions, CLI parsers)
   - Dependency graph between internal modules (imports/requires)
2. Compute basic metrics:
   - LOC per module/directory (identify largest modules)
   - File count per directory
   - Number of exports/public APIs per module
3. If --depth is deep:
   - Analyze git log for churn hotspots: files changed most
     frequently, files frequently changed together (coupling)
   - Identify bandaid commit patterns: commits with messages like
     "fix", "patch", "workaround", "hack", "hotfix" concentrated
     in specific files or modules
4. Identify generated/vendored code to exclude:
   - node_modules, vendor, dist, build, .generated, protobuf output
   - Files with "DO NOT EDIT" or "auto-generated" headers
5. Load language-specific references:
   - Read the appropriate references/lang-*.md files based on
     detected languages
   - Include reference content in agent prompts
6. Write RECON-SUMMARY.md in the report directory with:
   - Module map (directory → purpose, LOC, file count)
   - Dependency graph (which modules import which)
   - Hotspot analysis (if deep)
   - Exclusion list (generated/vendored paths)
7. Determine which agents to spawn based on --focus
```

### Phase 1: Parallel Agent Execution

Spawn all applicable agents simultaneously. Each agent receives:
- The recon summary (module map, dependency graph, metrics)
- The target path
- Its specific audit checklist (see Agent Briefs below)
- Language-specific reference content (if available)
- Instruction to write findings to `{report-dir}/findings-{domain}.md`

Each agent produces a findings file with concrete, actionable entries.

### Phase 2: Cross-Reference & Prioritization

After all agents complete, the orchestrator:

```
1. Read all findings-{domain}.md files
2. Deduplicate: multiple agents may flag the same code from different
   angles (e.g., functions agent flags a 200-line function, modules
   agent flags the same class as a god class). Keep the most detailed
   write-up and note which domains identified it.
3. Identify refactoring clusters: groups of findings that resolve
   with a single refactoring effort. For example:
   - 4 duplication findings + 1 module finding → "Extract a shared
     utility module" (one action resolves 5 findings)
   - 3 function findings in the same class + 1 SRP violation →
     "Split class into focused components" (one action resolves 4)
4. Score each finding/cluster:
   - Impact: how much complexity/risk does this remove?
     (HIGH / MEDIUM / LOW)
   - Effort: how much work to implement?
     (S = hours, M = 1-2 days, L = 3-5 days, XL = 1+ week)
   - Priority = Impact ÷ Effort (high-impact/low-effort first)
5. Assign priority tiers:
   - P0 (do first): HIGH impact, S/M effort — quick wins
   - P1 (do soon): HIGH impact, L effort — or MEDIUM impact, S effort
   - P2 (plan for): HIGH impact, XL effort — or MEDIUM impact, M/L
   - P3 (consider): LOW impact or XL effort
```

### Phase 3: Report Generation

```
1. Write the final report with:
   - Executive summary (top 5 recommendations, overall assessment)
   - Findings grouped by priority tier (P0 first)
   - Each finding: current state, proposed change, affected files,
     effort estimate
   - Refactoring clusters highlighted as compound wins
   - Metrics summary (total findings by domain, priority distribution)
2. Remove intermediate findings files
3. Print summary table and top recommendations to conversation
```

## Agent Briefs

Each agent below receives its brief as the prompt when spawned. The
orchestrator prefixes every brief with the recon summary, target path,
and language-specific reference content.

---

### Agent: Duplication & Extraction (`duplication`)

**Objective:** Find duplicated code, repeated patterns, and
similar-but-slightly-different implementations that should be unified
into shared abstractions.

**Principles:** DRY (Don't Repeat Yourself), but with judgment — not
every similarity warrants extraction. The test is: if the logic changes,
would you need to update it in multiple places? If yes, it's a real
duplication problem.

**Checklist:**

1. **Exact and near-exact duplicates:**
   - Blocks of 5+ lines that appear in multiple places with only
     superficial differences (variable names, string literals)
   - Copy-pasted functions or methods across files
   - Identical or nearly identical class/struct definitions
   - Repeated configuration blocks (routes, middleware chains, schema
     definitions)

2. **Structural duplication:**
   - Functions that follow the same template but vary in one dimension
     (e.g., `processOrderEmail`, `processShippingEmail`,
     `processReturnEmail` — same structure, different content)
   - Switch/case or if/else chains where each branch follows the same
     pattern (candidates for strategy pattern or data-driven approach)
   - Repeated validate-transform-persist pipelines across different
     entity types

3. **Cross-module duplication:**
   - Utility functions reimplemented in multiple modules instead of
     shared (string formatting, date handling, validation helpers)
   - Similar data transformation logic in different layers
     (controller, service, repository all doing overlapping transforms)
   - Multiple implementations of the same business rule in different
     code paths (e.g., pricing logic in cart AND checkout AND invoice)

4. **Test duplication:**
   - Test setup code repeated across test files (candidate for shared
     fixtures or test helpers)
   - Test cases that are nearly identical (candidate for parameterized
     tests or table-driven tests)

**For each finding, include:**
- All locations where the duplication occurs (file:line for each)
- The duplicated pattern (show a representative example)
- How the instances differ (if near-duplicates)
- Suggested extraction: what to name it, where to put it, what
  parameters it needs
- Estimated lines saved

---

### Agent: Function & Method Quality (`functions`)

**Objective:** Find functions that are too long, do too many things,
mix abstraction levels, have too many parameters, or cause hidden
side effects.

**Principles (from Clean Code):**
- Functions should do one thing, do it well, do it only
- Functions should be small — ideally under 20-30 lines
- One level of abstraction per function
- Fewer arguments are better (0-2 ideal, 3 acceptable, 4+ suspect)
- No side effects — a function named `checkPassword` should not
  also initialize the session
- Command-query separation: a function should either do something
  or answer something, not both
- Don't return null — throw, return empty collection, or use Option

**Checklist:**

1. **Long functions (>30 lines of logic):**
   - Functions that do multiple sequential things that could be
     extracted into named steps
   - Functions with multiple levels of nested conditionals or loops
   - Functions where you need to scroll to understand them

2. **Too many parameters (>3):**
   - Functions with long parameter lists (candidate for parameter
     object or builder pattern)
   - Boolean flag parameters that change function behavior
     (candidate for two separate functions)
   - Functions where callers pass `null`/`undefined`/`None` for
     several parameters

3. **Mixed abstraction levels:**
   - A function that mixes high-level orchestration ("process the
     order") with low-level details ("parse the date string with
     this regex")
   - Business logic interleaved with I/O operations, logging, or
     metrics instrumentation

4. **Deep nesting (>3 levels):**
   - Nested if/else chains that can be flattened with early returns
     (guard clauses)
   - Nested loops that can be extracted into helper functions
   - Arrow-shaped code (indentation grows then shrinks)

5. **Side effects and hidden coupling:**
   - Functions that modify global state or instance variables not
     obvious from the name
   - Functions that write to files, databases, or external systems
     as a side effect of what appears to be a pure computation
   - Functions that depend on or modify hidden shared state

6. **Feature envy:**
   - Functions that access data from another class/module more than
     their own — they probably belong in that other class/module

**For each finding, include:**
- Function location (file:line)
- Function name and current line count
- What specifically is wrong (too long, too many args, mixed levels, etc.)
- Concrete suggestion: how to split, what to extract, what to rename
- Sketch of the refactored structure (names of extracted functions,
  new signatures)

---

### Agent: Module & Class Design (`modules`)

**Objective:** Find modules and classes that violate the Single
Responsibility Principle, have poor cohesion, tight coupling, or
wrong boundaries.

**Principles (from Clean Code and SOLID):**
- Single Responsibility Principle: a class/module should have one,
  and only one, reason to change
- Classes should be small — not by line count, but by responsibility count
- High cohesion: everything in a module should be related to its
  central purpose
- Loose coupling: modules should depend on abstractions, not concrete
  implementations
- Package by feature, not by layer (prefer `user/` over `controllers/`,
  `services/`, `repositories/` when it reduces cross-cutting)

**Checklist:**

1. **God classes/modules (multiple responsibilities):**
   - Classes with 10+ public methods spanning different concerns
   - Files over 500 lines (not a hard rule, but a signal)
   - Classes whose name includes "Manager", "Handler", "Processor",
     "Service", "Helper", "Utils" with a broad grab-bag of methods
   - Classes where methods cluster into groups that don't interact
     with each other (sign they should be separate classes)

2. **Poor cohesion:**
   - Modules where half the methods don't use half the instance
     variables (sign the class is doing two things)
   - Files that import from many unrelated modules
   - Directories with files that have little to do with each other

3. **Tight coupling:**
   - Modules that reach deep into another module's internals
     (violating Law of Demeter: `a.getB().getC().doThing()`)
   - Circular dependencies between modules
   - Changes to one module that routinely require changes to another
     (use git history if --depth deep)
   - Classes that take many other concrete classes as constructor
     parameters instead of interfaces/protocols

4. **Missing boundaries:**
   - Monolithic files that should be split into multiple focused files
   - Business logic mixed into framework-specific code (controllers,
     handlers, middleware) instead of being in pure domain modules
   - Shared mutable state accessed from multiple modules without
     a clear owner

5. **Over-engineering:**
   - Abstraction layers that add indirection without adding value
     (a "service" that just calls through to a "repository" with
     no additional logic)
   - Interface/abstract class with only one implementation and no
     plausible second implementation
   - Factory patterns, strategy patterns, or decorator patterns
     used where a simple function call would suffice

**For each finding, include:**
- Module/class location (file:line)
- Current responsibilities (list what it does)
- Which responsibilities should be separated
- Proposed split: new module/class names and what goes where
- Dependencies that would need updating

---

### Agent: Error Handling & Robustness (`errors`)

**Objective:** Find inconsistent error handling, swallowed exceptions,
bandaid try/catch blocks, and fragile code paths.

**Principles (from Clean Code):**
- Use exceptions rather than error codes
- Write the try/catch first — it defines a scope boundary
- Don't return null — throw, return empty collection, or use
  Option/Maybe/Result types
- Don't pass null
- Each exception should provide enough context to determine the
  source and location of the error
- Catch specific exceptions, not generic ones

**Checklist:**

1. **Swallowed exceptions:**
   - Empty catch blocks or catch blocks with only a log statement
     and no re-throw or recovery
   - `catch (Exception e)` or `except Exception` that silently
     converts failures into default values
   - Ignoring return values from functions that can fail

2. **Inconsistent error strategies:**
   - Some functions throw exceptions while similar functions return
     error codes or null — inconsistent within the same module
   - Mixed error patterns: callbacks with `(err, result)` alongside
     Promises alongside async/await in the same module
   - Some errors logged, others thrown, others returned — no clear
     convention

3. **Bandaid error handling:**
   - Multiple nested try/catch blocks wrapping the same operation
     at different levels (sign of fixing symptoms instead of root
     cause)
   - Retry loops without backoff or limit
   - `if (x != null && x.y != null && x.y.z != null)` chains
     (sign of upstream code that should guarantee structure)
   - Defensive null checks everywhere instead of fixing the source
     that produces nulls

4. **Missing error handling:**
   - Async operations without error handling (unhandled promise
     rejections, unchecked futures)
   - File/network/database operations without error handling
   - Parsing operations that assume valid input without validation
   - Resource cleanup missing in error paths (no finally/defer/using)

5. **Error message quality:**
   - Generic messages ("An error occurred", "Something went wrong")
   - Missing context (which operation failed, what input caused it,
     what state was expected)
   - Errors that expose internal details to end users (stack traces,
     SQL queries, file paths)

6. **Null/undefined abuse:**
   - Functions that return null to indicate "not found" AND "error"
     (ambiguous)
   - Optional parameters that are null by default when an empty
     collection or default object would be clearer
   - Null checks far from the source (the null travels through
     many layers before being checked)

**For each finding, include:**
- Location (file:line)
- Current error handling code (or lack thereof)
- What can go wrong (the specific failure modes)
- Suggested fix: what pattern to use, where to handle it, what
  message to provide

---

### Agent: Naming & Clarity (`naming`)

**Objective:** Find misleading names, magic numbers, comments that
compensate for bad code, dead code, unclear intent, and configuration
sprawl.

**Principles (from Clean Code):**
- Names should reveal intent — the name should tell you why it
  exists, what it does, and how it's used
- Avoid disinformation — don't call something a "list" unless it's
  actually a list
- Make meaningful distinctions — `data` vs `info` vs `value` are
  interchangeable noise words
- Use pronounceable, searchable names
- Don't encode type or scope in names (no Hungarian notation, no
  `m_` prefixes in modern languages)
- Comments are a failure to express yourself in code — clean code
  needs few comments

**Checklist:**

1. **Misleading or vague names:**
   - Generic names: `data`, `info`, `result`, `item`, `thing`,
     `tmp`, `temp`, `val`, `obj`, `manager`, `handler`, `processor`
     without qualification
   - Names that lie: a function named `getUser` that also modifies
     state, a variable named `count` that holds a flag
   - Abbreviations that aren't universal: `ctx` is fine, `cpt` for
     "checkpoint" is not
   - Names that differ by only a number or suffix (`data1`/`data2`,
     `processOld`/`processNew`)

2. **Magic numbers and strings:**
   - Literal numbers in conditions or calculations without
     explanation (`if (retries > 3)`, `timeout = 86400`)
   - String literals used as enum values or type discriminators
     scattered across the code instead of defined as constants
   - Status codes, permission bits, or config values hardcoded
     in business logic

3. **Comments compensating for bad code:**
   - A block comment explaining what a complex function does
     (extract the block into a well-named function instead)
   - Comments that describe what the next line does
     (`// increment counter` before `counter++`)
   - Comments that are stale or wrong (say one thing, code does
     another)
   - Commented-out code (should be deleted — git remembers)

4. **Dead code:**
   - Unreachable code after return/throw/break
   - Functions/methods/classes that are never called or imported
   - Feature flags or conditional branches for features that
     shipped long ago
   - Imports that are unused
   - Variables that are assigned but never read

5. **Unclear control flow:**
   - Boolean parameters that make call sites unreadable:
     `process(order, true, false, true)` — what do the booleans mean?
   - Complex boolean expressions that should be extracted into
     a named variable or function
   - Negated conditions that are hard to reason about
     (`if (!isNotEmpty)`)

6. **Configuration sprawl:**
   - Hardcoded configuration values scattered across source files
     (URLs, timeouts, feature thresholds, connection limits)
   - Inconsistent environment variable usage (some config from env
     vars, some from files, some hardcoded, no clear pattern)
   - Missing validation of configuration at startup (invalid config
     values cause runtime errors deep in the application instead of
     fast-failing at boot)
   - Config format inconsistency across the project (some YAML,
     some JSON, some env vars, some .properties)

**For each finding, include:**
- Location (file:line)
- Current name/code
- Why it's unclear (what a reader would misunderstand)
- Suggested rename or refactoring

---

### Agent: Cross-Module Architecture (`architecture`)

**Objective:** Find system-level simplification opportunities that
span module boundaries — interface bloat, unnecessary indirection,
accumulated bandaids across boundaries, data flow complexity, and
opportunities to merge or split modules.

This agent takes the broadest view. Module-internal issues are found
by the other agents; this agent focuses on the relationships and
protocols between modules.

**Principles:**
- The best architecture maximizes the number of decisions not made
- Minimize the surface area of interfaces between modules
- Data should flow through the fewest hops possible
- When bandaids accumulate at a boundary, the boundary is in the
  wrong place
- If two modules always change together, they should probably be
  one module
- If half a module changes independently from the other half,
  it should probably be two modules

**Checklist:**

1. **Interface bloat:**
   - Interfaces/APIs between modules with many methods, most of
     which are only used by one caller (the interface is a dumping
     ground, not a contract)
   - DTOs / data transfer objects that carry many fields through
     layers, with each layer only using a few
   - Adapters, wrappers, or facades that add no value — just
     rename methods or pass through

2. **Unnecessary indirection:**
   - Call chains where A calls B calls C calls D, and each
     intermediary adds no logic (just passes through)
   - Abstraction layers that exist "for future flexibility" but
     have one implementation and no plan for a second
   - Event/message systems used for what should be direct function
     calls (overengineered decoupling)

3. **Accumulated bandaids across boundaries:**
   - Patterns where module A works around a limitation in module B's
     interface by doing pre-processing or post-processing that
     really belongs in B (or signals B's interface is wrong)
   - "Compatibility shims" or "adapter layers" that grew over time
     as the modules diverged from their original contract
   - Multiple callers of the same API each doing the same
     pre/post-processing (the API should internalize that logic)
   - Commit history (if --depth deep): files from different modules
     that are always changed together — sign of a leaky abstraction

4. **Data flow complexity:**
   - Data that passes through many layers of transformation between
     source and destination
   - The same data fetched multiple times because modules don't
     trust each other's transformations
   - Bidirectional data flow between modules (A reads from B,
     B reads from A — circular dependency)
   - Shotgun surgery: a single logical change requires edits
     across 5+ files in different modules

5. **Module merge/split opportunities:**
   - Two small modules that always change together and share most
     of their dependencies (merge them)
   - One large module where half the code has completely different
     dependencies and change patterns from the other half (split it)
   - A "utils" or "helpers" or "common" module that's become a
     dumping ground — each function likely belongs in the module
     that uses it, or in a focused utility module

6. **Layer violations:**
   - Presentation/controller layer containing business logic
   - Business logic layer making direct database calls (bypassing
     the data access layer)
   - Domain objects aware of serialization formats, HTTP status
     codes, or UI concerns
   - Test code depending on internal implementation details
     instead of public interfaces

7. **Dependency direction violations:**
   - Dependencies pointing outward (domain/business logic importing
     from I/O, framework, or presentation layers) instead of inward
   - Core domain modules depending on specific database drivers,
     HTTP libraries, or UI frameworks — should depend on
     abstractions/ports
   - Application layer directly accessing infrastructure without
     going through defined ports/adapters
   - Shared kernel or domain events that leak infrastructure concerns

**For each finding, include:**
- All modules/files involved (file:line for key locations)
- Current interaction pattern (how the modules communicate now)
- What's wrong (bloat, indirection, bandaids, coupling, etc.)
- Proposed change: new module boundaries, simplified interfaces,
  merged/split modules
- Estimated scope of change (which files/modules are affected)

---

### Agent: Type Safety & API Contracts (`types`)

**Objective:** Find overly permissive types, stringly-typed APIs,
missing type annotations, inconsistent API shapes, and leaky
abstractions in public interfaces.

**Context:** Type safety issues compound — a single `any` at a
module boundary can erase type information for everything downstream.
This agent focuses on places where stronger typing would prevent bugs,
improve IDE support, and make refactoring safer. In dynamically typed
languages, focus on missing annotations that make code harder to
understand and on stringly-typed patterns that should use structured
types.

**Checklist:**

1. **Overly permissive types:**
   - Uses of `any`/`Any`/`object`/`id`/`interface{}` where specific
     types exist or could be defined
   - Type assertions/casts that bypass the type system without
     justification
   - Generic containers (`Dict[str, Any]`, `Map<String, Object>`,
     `[String: Any]`) used where a struct/class/interface would
     provide compile-time safety

2. **Stringly-typed APIs:**
   - String comparisons for control flow where enums, discriminated
     unions, or algebraic types should be used
     (`if (status === "active")` instead of `if (status === Status.Active)`)
   - Magic string keys in dictionaries that represent structured data
   - String concatenation to build structured data (SQL, HTML, JSON,
     URLs) instead of using typed builders or template systems

3. **Missing type annotations:**
   - Functions in dynamically typed languages with no type hints
     where the parameter/return types are non-obvious
   - Closure/lambda parameters with inferred types that are unclear
     from context
   - Public API functions without documented or annotated types

4. **Inconsistent API shapes:**
   - Endpoints or functions that return different shapes for similar
     data (`{data, error}` vs `{result, status}` vs raw values)
   - Nullable fields used inconsistently (same field required in
     one response, optional in another)
   - Mixed conventions for expressing absence (null vs undefined vs
     empty string vs missing key)

5. **Leaky abstractions in public interfaces:**
   - Internal implementation details exposed in return types or
     parameters (database row objects leaked to callers, framework
     types in public APIs)
   - Public types that force callers to understand private
     implementation choices
   - Return types that change meaning based on internal state

6. **Type coercion pitfalls:**
   - Implicit type conversions that silently change behavior
     (`0 == ""` truthy/falsy comparisons used for control flow)
   - Numeric types used where booleans are intended (or vice versa)
   - String-to-number conversions without validation

7. **Union types vs polymorphism:**
   - Union types or optional parameters used where polymorphism or
     method overloads would be clearer and safer
   - Functions with many optional parameters that represent distinct
     use cases (should be separate functions or a builder)

8. **Missing or incorrect generic constraints:**
   - Generic types without bounds that accept anything when they
     should be constrained (`<T>` where `<T extends Serializable>`
     is needed)
   - Generic code that internally casts to a specific type (the
     generic is a lie)
   - Missing variance annotations where they would prevent misuse

**For each finding, include:**
- Location (file:line)
- Current type or type-unsafe pattern
- What bugs or confusion this enables
- Suggested type improvement (specific type, enum definition,
  interface shape)
- Scope of impact (how many downstream consumers benefit)

---

### Agent: Test Quality (`tests`)

**Objective:** Find tests that provide false confidence — tests that
don't assert anything meaningful, tests coupled to implementation
details, missing test boundaries, flaky patterns, and dead test code.

**Principles:**
- Tests exist to verify behavior, not to exercise code paths
- A test that can't fail is worse than no test (false confidence)
- Tests should survive refactoring — if behavior doesn't change,
  tests shouldn't break
- Test the contract, not the implementation
- Fast tests run often; slow tests get skipped

**Checklist:**

1. **Empty or meaningless assertions:**
   - Tests that run code but never check results, or only check
     that it doesn't throw
   - Assertions on implementation artifacts rather than behavior
     (asserting a mock was called with specific args instead of
     asserting the output)
   - Tests that assert `true === true` or equivalent tautologies
   - Tests where the expected value is derived from the same code
     being tested (circular assertion)

2. **Implementation-coupled tests:**
   - Mock-heavy tests that break when internals are refactored
     even though behavior hasn't changed
   - Tests that assert on internal method call order or count
   - Tests that reach into private state to verify
   - Tests that reproduce the implementation logic to compute
     expected values

3. **Missing test boundaries:**
   - No integration tests (only unit tests mocking everything) —
     nothing verifies that modules work together
   - No unit tests (only slow end-to-end tests) — feedback loop
     is too slow, failures are hard to diagnose
   - Missing contract tests at module boundaries

4. **Flaky test patterns:**
   - Time-dependent tests (using real clocks, `sleep`, `Date.now()`)
   - Order-dependent tests (test B fails if test A doesn't run first)
   - Network-dependent tests without mocking or test servers
   - Filesystem-dependent tests using hardcoded paths or shared
     temp directories
   - Tests with race conditions (async operations without proper
     waiting)

5. **Dead test code:**
   - Tests behind feature flags for features that shipped long ago
   - Commented-out tests
   - Tests with `skip`/`xit`/`xdescribe`/`@Disabled`/`@Ignore`
     with no tracking issue
   - Test helper functions that are never called

6. **Unclear test names:**
   - Test names that don't describe the expected behavior or
     scenario (`test1`, `testHelper`, `shouldWork`)
   - Missing "given/when/then" or "arrange/act/assert" structure
     that makes it unclear what's being tested

7. **Hidden test setup:**
   - Shared fixtures far from the test that make it hard to
     understand what's being tested
   - `beforeAll`/`setUp` blocks that configure state for dozens
     of tests with different needs
   - Test inheritance hierarchies that obscure the actual setup

8. **Missing edge case coverage:**
   - Critical business logic with only happy path tested
   - No tests for error paths, boundary values, empty inputs,
     or concurrent access
   - Missing regression tests for previously fixed bugs

9. **Snapshot test abuse:**
   - Snapshot tests that are blindly updated without review
   - Snapshots of large structures where small meaningful changes
     are buried in noise
   - Snapshots used where specific assertions would be clearer
     and more resilient

10. **Oversized test files:**
    - Test files that are significantly larger than the code they
      test (sign of overcomplicated test setup or testing
      implementation rather than behavior)
    - Test helpers that are more complex than the production code

**For each finding, include:**
- Test location (file:line)
- Test name and what it claims to test
- What's wrong (no assertion, implementation-coupled, flaky, etc.)
- Suggested fix: what to assert instead, how to decouple, how to
  make deterministic
- Severity: does this test provide false confidence (HIGH) or is
  it merely suboptimal (MEDIUM/LOW)?

---

### Agent: Data Model & Schema Quality (`data-model`)

**Objective:** Find data model and schema issues — unjustified
denormalization, missing constraints, naming inconsistencies, orphaned
fields, schema-code drift, and structural problems that make the data
layer fragile or confusing.

**Principles:**
- The schema is the most stable part of many systems — get it right
- Constraints at the schema level are cheaper than validation in
  application code
- Naming consistency reduces cognitive load across the entire stack
- Every field should have a clear writer and reader — orphaned fields
  are a sign of incomplete cleanup
- The ORM/model should be the source of truth, not a rough
  approximation of the actual database

**Checklist:**

1. **Unjustified denormalization:**
   - Same data stored in multiple places with no sync mechanism
   - Cached/computed fields without a clear invalidation strategy
   - Duplicated references that can drift out of sync (e.g., storing
     both `userId` and `userName` when username can change)

2. **Missing schema constraints:**
   - Nullable columns that should be NOT NULL (the application
     always requires them)
   - Missing unique constraints on fields that must be unique
     (emails, slugs, external IDs)
   - Missing foreign keys where referential integrity matters
   - Missing check constraints for bounded values (status enums,
     positive amounts, valid ranges)

3. **Naming inconsistencies:**
   - Mixed naming conventions across models (snake_case vs
     camelCase, plurals vs singulars, `userId` vs `user_id`)
   - Inconsistent relationship naming (some `authorId`, some
     `created_by`, some `writer`)
   - Table/collection names that don't match the model/class names
     they map to

4. **Orphaned fields:**
   - Model/schema properties that are written but never read
   - Fields that are read but never written (always null/default)
   - Columns added for a feature that was later removed
   - Fields that are only used in dead code paths

5. **Schema-code drift:**
   - The ORM/model definition doesn't match what the database
     actually enforces (nullable in code, NOT NULL in DB, or
     vice versa)
   - Migrations that have been applied but the model code wasn't
     updated (or vice versa)
   - Default values defined in the application that should be
     database defaults (or vice versa)

6. **Over-normalization:**
   - Excessive joins required for common read patterns
   - Lookup tables with two columns that change less often than
     the code is deployed
   - Normalized structures that force N+1 query patterns in
     practice

7. **Missing indexes:**
   - Fields used in WHERE clauses, ORDER BY, or JOIN conditions
     that lack indexes (detectable from query patterns in code)
   - Composite queries that would benefit from compound indexes
   - Indexes that exist but don't match actual query patterns

8. **Polymorphic association anti-patterns:**
   - Generic relation patterns that sacrifice type safety and
     referential integrity (`commentable_type` + `commentable_id`)
   - Single-table inheritance with many nullable columns specific
     to subtypes
   - JSON/JSONB columns used as a schema escape hatch for what
     should be structured relational data

9. **God models:**
   - Models with too many fields (20+ columns is a signal)
   - Models that represent multiple concepts conflated into one
     table
   - Models with fields that cluster into groups with different
     lifecycles or access patterns

10. **Temporal data issues:**
    - Missing `created_at`/`updated_at` timestamps
    - No soft-delete pattern where audit trail or undo is needed
    - Timestamps stored without timezone information
    - No versioning or history tracking for data that changes and
      where history matters

**For each finding, include:**
- Model/table/schema location (file:line)
- Current schema or field definition
- What's wrong (missing constraint, orphaned field, naming, etc.)
- Suggested fix: the specific constraint, rename, or restructuring
- Risk assessment: what bugs or data integrity issues this enables

---

### Agent: Concurrency & Async Patterns (`concurrency`)

**Objective:** Find concurrency anti-patterns, mismatched async
styles, race conditions, missing cancellation/cleanup, and thread
safety issues.

**Principles:**
- Prefer structured concurrency: every async task should have a
  clear owner and lifecycle
- Use the codebase's predominant async pattern consistently — don't
  mix callbacks, promises, and async/await without reason
- Shared mutable state is the root of most concurrency bugs — prefer
  message passing, immutable data, or explicit synchronization
- Every async operation should handle cancellation and errors
- Fire-and-forget is almost always wrong — someone should observe
  the result or error

**Checklist:**

1. **Callback hell / deeply nested async:**
   - Deeply nested promise chains or completion handlers that
     should be flattened with async/await or reactive patterns
   - Pyramid of doom: 3+ levels of nested callbacks
   - Manual promise chaining where async/await would be clearer

2. **Race conditions:**
   - Shared mutable state modified in async flows without
     synchronization
   - Check-then-act patterns without atomicity (TOCTOU:
     `if (exists) { use(it) }` where `it` could be removed between
     check and use)
   - Multiple async operations reading and writing the same state
     concurrently

3. **Mismatched async patterns:**
   - Callbacks alongside async/await alongside
     Combine/RxJS/Reactor alongside raw threads in the same module
   - Wrapping callback APIs in promises in some places but not
     others
   - Inconsistent use of the codebase's chosen concurrency model

4. **Missing cancellation or cleanup:**
   - Async operations that run to completion even when the result
     is no longer needed (user navigated away, request timed out,
     parent task cancelled)
   - Missing disposal/cleanup of subscriptions, listeners, or
     observers
   - Resources acquired in async flows without guaranteed release

5. **Unstructured concurrency:**
   - Fire-and-forget async tasks with no error handling or
     lifecycle management
   - `Task { }` / `go func()` / `Thread { }` / `setTimeout` with
     no way to cancel or observe completion
   - Background work spawned without joining or awaiting

6. **Unnecessary async:**
   - Async operations that should be synchronous (awaiting something
     that's already resolved, wrapping sync code in async for no
     reason)
   - Functions marked `async` that never actually await anything
   - Promise/Future wrapping of synchronous computation

7. **Missing timeouts:**
   - Potentially blocking async operations without
     timeout/deadline (network calls, lock acquisition, queue
     operations)
   - Unbounded waits that could hang the application
   - Retry loops without maximum duration or attempt limits

8. **Thread safety issues:**
   - Mutable state shared across concurrent contexts without
     proper synchronization (locks, actors, serial queues,
     atomic operations)
   - Collections modified while being iterated from another thread
   - Lazy initialization without thread-safe patterns in
     concurrent contexts

9. **Unwrapped callback APIs:**
   - Callback-based APIs that should be wrapped in modern async
     abstractions for the codebase's style
   - Delegate patterns used where closures/async would reduce
     boilerplate and improve locality
   - Event emitter patterns that would be clearer as async
     streams or reactive observables

**For each finding, include:**
- Location (file:line)
- Current async/concurrency pattern
- What can go wrong (race condition, resource leak, hang, etc.)
- Suggested fix: the specific pattern, synchronization primitive,
  or restructuring
- Severity: can this cause data corruption or deadlock (HIGH),
  resource leak (MEDIUM), or is it a style/consistency issue (LOW)?

---

## Findings File Format

Each agent writes its findings to `{report-dir}/findings-{domain}.md`
using this format:

```markdown
# Findings: {Domain Name}

**Agent:** {domain}
**Target:** {target path}
**Files analyzed:** {count}
**Findings:** {count}

## F-{domain}-001: {Short title}

- **Impact:** HIGH / MEDIUM / LOW
- **Effort:** S / M / L / XL
- **Confidence:** CONFIRMED / LIKELY / POSSIBLE
- **Location(s):** {file:line, file:line, ...}
- **Description:** {What's wrong and why it matters}
- **Current code:**
  ```{lang}
  {representative snippet showing the problem}
  ```
- **Suggested change:**
  ```{lang}
  {sketch of improved code or structure}
  ```
- **Rationale:** {Why this change makes the code better — reference
  the specific principle violated}

## F-{domain}-002: {next finding}
...
```

- **Confidence:** CONFIRMED (read the code and this is definitely an issue), LIKELY (pattern matches but context might justify it), POSSIBLE (can't fully trace the data flow or the issue depends on runtime behavior)

## Report Format

The final report follows this structure:

```markdown
# Refactor Audit Report

**Target:** {target path}
**Date:** {date}
**Depth:** {shallow / standard / deep}
**Audited domains:** {list}

## Executive Summary

{2-3 paragraphs: overall code health assessment, key problem areas,
top 5 recommended actions. Be direct — "The codebase has significant
duplication in X" not "There may be opportunities to explore..."}

### Findings Distribution

| Domain | Findings | HIGH | MEDIUM | LOW |
|---|---|---|---|---|
| Duplication | N | N | N | N |
| Functions | N | N | N | N |
| Modules | N | N | N | N |
| Errors | N | N | N | N |
| Naming | N | N | N | N |
| Architecture | N | N | N | N |
| Types | N | N | N | N |
| Tests | N | N | N | N |
| Data Model | N | N | N | N |
| Concurrency | N | N | N | N |
| **Total** | **N** | **N** | **N** | **N** |

## P0: Quick Wins (High Impact, Low Effort)

### [R-001] {Recommendation title}

- **Priority:** P0
- **Impact:** HIGH
- **Effort:** S
- **Domains:** {which agents identified this}
- **Resolves:** {list of finding IDs this addresses}
- **Location(s):** {file:line references}
- **Current state:** {what exists now}
- **Proposed change:** {specific refactoring action}
- **Affected files:** {list of files that need changes}

## P1: Do Soon
{same format}

## P2: Plan For
{same format}

## P3: Consider
{same format}

## Refactoring Clusters

{Groups of findings that resolve with a single refactoring effort.
Each cluster lists its member findings and the unifying action.}

### Cluster: {descriptive name}

- **Findings resolved:** F-dup-003, F-mod-001, F-arch-002
- **Single action:** {the one refactoring that resolves all of them}
- **Net complexity reduction:** {estimated lines removed, modules
  simplified, interfaces narrowed}
```

## Rules

1. **Concrete references only.** Every finding must include file:line
   references and code snippets. "Consider applying SRP" is not a
   finding. "Split UserService (src/services/user.ts:1-450, handles
   auth + profile + billing) into AuthService, ProfileService, and
   BillingService" is a finding.

2. **Parallel execution.** All domain agents run in parallel. The
   orchestrator spawns all agents in a SINGLE message with multiple
   Agent tool calls. Do NOT spawn them sequentially.

3. **Judge, don't dogmatize.** Not every long function needs splitting.
   Not every duplication needs extracting. A 40-line function that
   reads clearly is fine. Two 3-line blocks that happen to look
   similar don't need a shared abstraction. The agents should apply
   judgment: would this change actually make the code simpler and
   more maintainable, or is it refactoring theater?

4. **Read the code, don't just scan it.** Agents must read the actual
   code to understand context. A function that appears too long might
   be a reasonable state machine. A class with many methods might have
   high cohesion. Pattern-match cautiously and verify by reading.

5. **Deduplicate across agents.** Multiple agents will flag the same
   code from different angles. The orchestrator deduplicates in Phase
   2, keeping the most detailed write-up and noting which domains
   identified it.

6. **Clusters over individual fixes.** The most valuable output is
   refactoring clusters — groups of findings that collapse into a
   single action. The orchestrator should actively look for these in
   Phase 2.

7. **Exclude generated code.** Skip vendored dependencies, generated
   files, build output, and migration files (unless migrations contain
   hand-written logic). The recon phase identifies these.

8. **Before/after sketches.** For HIGH-impact findings, include a code
   sketch showing the proposed improvement — not a complete
   implementation, but enough to show the shape of the change.

9. **Effort estimates are honest.** Don't underestimate. If a
   refactoring requires updating 30 call sites, that's effort L or
   XL, not S. Include the ripple effects in the estimate.

10. **Fail gracefully.** If an agent encounters files it can't parse
    or modules it can't understand, it should note what it skipped and
    continue. Report what was and wasn't analyzed.

11. **Respect existing architecture decisions.** Some patterns that
    look like over-engineering may exist for good reasons (regulatory
    compliance, performance requirements, plugin architecture). Flag
    them as findings but note "verify intent with team" when the
    pattern might be deliberate.

12. **Language-specific awareness.** Agents MUST reference the loaded
    language reference files and check for language-specific patterns.
    A pattern that's idiomatic in one language may be an anti-pattern
    in another.

## Orchestrator Implementation

The orchestrator (Manager) executes this sequence:

```
1. PARSE ARGUMENTS
   - Validate --target exists (or use cwd)
   - Set depth, focus, and report path
   - Create report directory if needed

2. RECONNAISSANCE (Phase 0)
   - Run recon as described above
   - Produce RECON-SUMMARY.md
   - Detect languages and frameworks
   - Load language-specific references from references/lang-*.md
   - If the codebase is very small (<500 LOC), consider whether a
     multi-agent audit is warranted — for tiny codebases, a single
     agent pass may be more appropriate

3. SPAWN AGENTS (Phase 1)
   - For each domain in --focus (default: all 10 domains):
     - Spawn an agent with:
       - subagent_type: "general-purpose"
       - The appropriate Agent Brief from above
       - Recon summary content
       - Language-specific reference content
       - Target path
       - Instruction to write findings to findings-{domain}.md
   - All agents MUST be spawned in a SINGLE message with multiple
     Agent tool calls so they run concurrently

4. CROSS-REFERENCE & PRIORITIZE (Phase 2)
   - Read all findings-{domain}.md files
   - Deduplicate across agents
   - Identify refactoring clusters
   - Score and assign priority tiers

5. GENERATE REPORT (Phase 3)
   - Write the final report to --report path
   - Print summary table and top 5 recommendations to conversation

6. CLEANUP
   - Remove intermediate findings files (keep final report only)
   - Remove RECON-SUMMARY.md
   - Print report location
```

## Agent Spawning Details

When spawning each domain agent, use:
- `subagent_type: "general-purpose"` for all agents
- Include the full agent brief from the relevant section above
- Prefix the prompt with the recon summary and language reference content
- Include explicit instructions about output file path and the
  findings file format (including the Confidence field)
- Include the target path

The orchestrator MUST spawn all Phase 1 agents in a SINGLE message
with multiple `Agent` tool calls so they run concurrently. Do NOT
spawn them sequentially.
