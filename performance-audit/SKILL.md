---
name: performance-audit
description: Multi-agent white-box performance and resource usage audit. Finds redundant computation, memory waste, algorithm inefficiencies, missing caching opportunities, and excessive resource usage across any codebase.
metadata:
  short-description: Comprehensive multi-agent performance audit
---

# Skill: performance-audit

Multi-agent performance audit orchestrator. Spawns parallel specialist
agents to audit every performance surface of a codebase — redundant work,
memory usage, algorithm efficiency, caching opportunities, resource
proportionality, startup latency, rendering bottlenecks, database query
efficiency, and build/bundle bloat. Each agent reads source code, traces
data/control flow, and produces actionable findings.

## When to use

Use when the user asks to "audit performance", "find bottlenecks",
"optimize this codebase", "check resource usage", "performance review",
or references `/performance-audit`. Works on any codebase with source
code access (white-box only).

## Arguments

- `--target <path>` — path to the codebase to audit (default: current working directory)
- `--focus <domain,...>` — comma-separated list of domains to audit (default: all). Valid domains: `redundancy`, `memory`, `algorithm`, `caching`, `io`, `concurrency`, `startup`, `rendering`, `database`, `build`
- `--scope <path,...>` — comma-separated list of specific files or directories to audit within the target (default: entire repo)
- `--report <path>` — output path for the final report (default: `{target}/PERFORMANCE-AUDIT-REPORT.md`)
- `--severity <critical|high|medium|low|info>` — minimum severity to include in report (default: `info`)

## Example invocations

Audit the current repo (all domains):
```
/performance-audit
```

Audit specific directories:
```
/performance-audit --scope src/api,src/services
```

Focus on specific domains:
```
/performance-audit --focus redundancy,caching,memory
```

Focus on UI and database performance:
```
/performance-audit --focus rendering,database,startup
```

Audit a different project:
```
/performance-audit --target ~/projects/my-app --focus algorithm,io
```

## Audit Domains & Agents

The orchestrator spawns one agent per domain. All agents run in parallel.
Each agent reads source code and produces structured findings.

| Agent | Domain | Focus |
|---|---|---|
| **Redundant Work** | `redundancy` | Repeated calculations, duplicate logic across call paths, unnecessary re-computation, N+1 patterns, redundant I/O or network calls |
| **Memory & Allocation** | `memory` | Unnecessary copies, unbounded growth, leak patterns, oversized data structures, excessive allocation in hot paths |
| **Algorithm & Complexity** | `algorithm` | Suboptimal algorithmic complexity, wrong data structure choices, unnecessary sorting, brute-force where better approaches exist |
| **Caching & Batching** | `caching` | Missing memoization, repeated expensive operations with same inputs, unbatched I/O, lazy-loading opportunities, computation/space tradeoffs |
| **I/O & Resources** | `io` | Excessive disk/network operations, synchronous I/O on hot paths, uncompressed payloads, resource handle leaks, over-fetching, disproportionate resource usage, energy/battery waste |
| **Concurrency** | `concurrency` | Missed parallelism, unnecessary serialization, lock contention, thread/task over-creation, blocking in async contexts |
| **Startup & Initialization** | `startup` | Slow launch sequences, eager loading, heavy module-level init, sequential boot of independent subsystems, deferred loading opportunities |
| **Rendering & UI Performance** | `rendering` | Excessive redraws, layout thrashing, animation jank, large view hierarchies, missing virtualization, main thread congestion |
| **Database & Query Performance** | `database` | Missing indexes, N+1 queries, full table scans, connection pool misconfiguration, inefficient pagination, ORM-generated query bloat |
| **Build & Bundle Performance** | `build` | Oversized bundles, missing code splitting, tree-shaking failures, duplicate dependencies, unoptimized assets, slow CI/CD pipelines |

## Language References

Language-specific performance patterns are stored as reference files.
During reconnaissance, the orchestrator detects the project's languages
and loads the relevant references to include in agent prompts.

Available references:
- [references/lang-swift.md](references/lang-swift.md) — Swift, SwiftUI, iOS/macOS
- [references/lang-python.md](references/lang-python.md) — Python, Django, Flask, FastAPI, pandas
- [references/lang-javascript-typescript.md](references/lang-javascript-typescript.md) — JavaScript, TypeScript, React, Node.js
- [references/lang-go.md](references/lang-go.md) — Go
- [references/lang-rust.md](references/lang-rust.md) — Rust, Tokio
- [references/lang-java-kotlin.md](references/lang-java-kotlin.md) — Java, Kotlin, Spring, JVM
- [references/lang-c-cpp.md](references/lang-c-cpp.md) — C, C++

When a project uses multiple languages, load all relevant references.

When a project uses a language without a dedicated reference file (e.g., PHP, Ruby, C#/.NET, Dart/Flutter, Elixir/Erlang, Scala), agents should still apply the general checklist items. Language-specific references improve precision but are not required. Contributions of new reference files are welcome.

## Workflow

### Phase 0: Reconnaissance

Before spawning specialist agents, the orchestrator performs a quick
reconnaissance pass:

```
1. Identify the tech stack:
   - Languages (package files: Package.swift, package.json,
     requirements.txt, go.mod, Cargo.toml, pom.xml, etc.)
   - Frameworks (SwiftUI, React, Django, Spring, etc.)
   - Build system (Xcode, webpack, CMake, Gradle, etc.)
2. Map the architecture:
   - Entry points: main functions, request handlers, UI entry,
     event loops, queue consumers
   - Hot paths: request handling chains, render loops, data
     processing pipelines, frequently called utilities
   - Data flow: input -> processing -> storage -> output
   - Concurrency model: threads, async/await, actors, GCD,
     goroutines, coroutines
3. Determine scope:
   - If --scope is specified, limit file discovery to those paths
   - Otherwise, scan the full repo (exclude vendored/generated code)
   - Identify the largest/most complex modules as priority targets
4. Classify code paths by execution frequency:
   - HOT: per-request, per-frame, per-event (runs thousands/millions
     of times)
   - WARM: per-session, per-page-load, per-operation (runs
     tens/hundreds of times)
   - COLD: per-startup, per-deploy, per-configuration-change (runs
     once or rarely)
   Write this classification into the recon summary so agents can
   calibrate severity: the same inefficiency in a HOT path is CRITICAL
   but in a COLD path may be INFO.
5. Load language-specific references:
   - Read the appropriate references/lang-*.md files based on
     detected languages
   - These will be included in each agent's prompt
6. Write a RECON-SUMMARY.md in the report directory with findings
7. Determine which agents to spawn based on --focus
```

### Phase 1: Parallel Agent Execution

Spawn all applicable agents simultaneously. Each agent receives:
- The recon summary (including hot/warm/cold path classification)
- The target path and scope
- Language-specific performance patterns from reference files
- Its specific audit checklist (see Agent Briefs below)

Each agent produces a findings file:
`{report-dir}/findings-{domain}.md`

### Phase 2: Cross-cutting Analysis

After all agents complete, the orchestrator:

```
1. Collect all findings from Phase 1
2. Identify cross-cutting patterns:
   - A redundancy finding + a caching finding on the same code path
     -> compound recommendation (cache to eliminate the redundancy)
   - An I/O finding + a concurrency finding on the same path
     -> compound recommendation (parallelize the I/O)
   - A startup finding + a caching finding
     -> compound recommendation (cache config to speed up boot)
   - A rendering finding + a memory finding
     -> compound recommendation (reduce allocations to fix jank)
   - A database finding + a redundancy finding
     -> compound recommendation (batch queries to eliminate N+1)
   - Multiple agents flagging the same code region
     -> indicates a systemic design issue, not just point fixes
3. For compound findings, spawn a brief Synthesis agent to:
   - Draft a unified recommendation that addresses multiple issues
   - Estimate combined impact
   - Suggest implementation approach
```

### Phase 3: Report Generation

```
1. Merge all findings into a single report
2. Deduplicate (multiple agents may find the same issue from
   different angles)
3. Assign final impact ratings:
   - CRITICAL: O(n^2)+ on large data, memory leak, blocking main
     thread, resource exhaustion, missing index on high-traffic query
   - HIGH: Significant redundant work, missing caching on hot path,
     wrong data structure causing 10x+ slowdown, N+1 queries on
     large collections, startup blocking on deferrable work
   - MEDIUM: Unnecessary allocations, suboptimal but functional
     algorithms, unbatched I/O, excessive re-renders, oversized
     bundles
   - LOW: Minor inefficiencies, style issues with perf implications,
     pre-allocation opportunities, build-time optimizations
   - INFO: Best-practice suggestions, potential future bottlenecks,
     monitoring recommendations
4. Sort findings by impact (critical first)
5. Write the final report to --report path
6. Print a summary table to the conversation
```

## Agent Briefs

Each agent below receives its brief as the prompt when spawned. The
orchestrator prefixes every brief with the recon summary, target info,
and language-specific reference content.

---

### Agent: Redundant Work (`redundancy`)

**Objective:** Find places where the same work is done more than once —
computations repeated unnecessarily, data fetched multiple times, logic
duplicated across code paths.

**Checklist:**

1. **Repeated function calls with identical arguments:**
   - Trace call sites of expensive functions (DB queries, API calls,
     complex calculations, file reads)
   - Check if the same function is called with the same arguments
     multiple times within a request/render/event cycle
   - Check if results could be computed once and threaded through

2. **Duplicate logic across code paths:**
   - Find near-identical code blocks that compute the same value
   - Check if the same data transformation is applied in multiple
     places (e.g., formatting, validation, parsing)
   - Look for "normalize then process" patterns where normalization
     repeats

3. **N+1 patterns:**
   - ORM/database: iterating a collection and querying per item
   - API calls: fetching related resources one by one
   - File system: reading files one by one when batch read is possible
   - UI: re-computing derived state per list item when it could be
     computed once for the collection

4. **Unnecessary re-computation on state change:**
   - UI frameworks: recomputing the entire view when only a subset
     changed
   - Recalculating derived data on every access instead of caching
     on mutation
   - Rebuilding entire data structures when only a part was modified

5. **Redundant validation/parsing:**
   - Input validated at multiple layers with identical checks
   - Data parsed from string -> object multiple times
   - Type conversions repeated across function boundaries

**Output:** For each finding, include the two (or more) locations where
work is duplicated, how frequently the duplication occurs (per request?
per frame? per startup?), and an estimated reduction if fixed.

---

### Agent: Memory & Allocation (`memory`)

**Objective:** Find unnecessary memory usage — objects retained too long,
unnecessary copies, oversized data structures, unbounded growth, and
allocation patterns that create GC/ARC pressure.

**Checklist:**

1. **Unnecessary copies:**
   - Data passed by value when reference/borrow would work
   - Deep copies where shallow copies or references suffice
   - String copies in loops (concatenation patterns)
   - Collection copies (mapping to new array when in-place is safe)

2. **Oversized data structures:**
   - Loading entire datasets when only a subset is needed
   - Storing full objects when only IDs or keys are needed
   - Retaining raw data after processing (keeping both raw and parsed)
   - Using rich data types for simple data (class/struct where a
     primitive would do)

3. **Unbounded growth:**
   - Collections that grow without eviction (caches, logs, history)
   - Event listeners/observers that accumulate without removal
   - Closures capturing scope in long-lived callbacks
   - Circular references preventing cleanup (ARC retain cycles,
     reference cycles in GC'd languages)

4. **Allocation in hot paths:**
   - Object creation inside tight loops
   - Temporary allocations that could be reused across iterations
   - String formatting in logging/debug code that runs even when
     disabled
   - Autoboxing of primitives in typed contexts

5. **Data structure sizing:**
   - Collections initialized without capacity hints when size is known
   - Hash maps/sets with poor load factor configuration
   - Sparse arrays or maps where a denser representation works

**Output:** For each finding, estimate the memory impact (bytes per
instance x instance count), frequency (per request? per frame? total
lifetime?), and suggested fix.

---

### Agent: Algorithm & Complexity (`algorithm`)

**Objective:** Find algorithmic inefficiencies — suboptimal time
complexity, wrong data structure choices, unnecessary work in loops.

**Checklist:**

1. **Suboptimal time complexity:**
   - Nested loops over the same or related collections (O(n^2) or worse)
   - Linear search where hash lookup would work
   - Repeated sorting of the same data
   - Scanning an entire collection to find/check membership
   - Quadratic string operations (index-based access on UTF-8/UTF-16)

2. **Wrong data structure:**
   - Array/list used for frequent membership tests (should be set)
   - Array used for frequent key-value lookup (should be map/dict)
   - Sorted collection maintained via sort-on-insert when a binary
     tree/heap would maintain order naturally
   - Dense integer-keyed map where an array would work
   - Linked list where array (cache locality) would be faster

3. **Unnecessary work in loops:**
   - Loop-invariant computation inside the loop body
   - Sorting/filtering inside a loop when it could happen once before
   - Computing the same derived value on each iteration
   - Conditional checks that are constant for all iterations

4. **Suboptimal search/sort:**
   - Sorting to find min/max (O(n log n) vs O(n))
   - Full sort when only top-k needed (should use partial sort/heap)
   - Linear search on sorted data (should be binary search)
   - Custom sort where the language's built-in sort is better tuned

5. **Mathematical shortcuts missed:**
   - Computing all combinations when a formula exists
   - Iterative approaches where closed-form solutions apply
   - Brute force search where pruning/dynamic programming applies
   - Recomputing cumulative/aggregate values from scratch instead
     of maintaining incrementally

**Output:** For each finding, state the current complexity, the
achievable complexity, the data size it operates on (if determinable),
and the concrete change needed.

---

### Agent: Caching & Batching (`caching`)

**Objective:** Identify opportunities to trade space for time — caching
to avoid re-computation, batching to reduce overhead, lazy evaluation to
defer unnecessary work, precomputation to shift cost.

**Checklist:**

1. **Memoization opportunities:**
   - Pure or near-pure functions called repeatedly with the same
     arguments (same inputs -> same output)
   - Expensive derivations from immutable data (formatting dates,
     computing hashes, rendering templates)
   - Recursive functions with overlapping subproblems

2. **Result caching:**
   - API/DB results that are fetched multiple times within a session
     or request cycle
   - Configuration/settings read from disk/DB on every access
   - Static reference data (country codes, enum mappings) loaded
     fresh each time instead of cached on first load

3. **Batching opportunities:**
   - Multiple individual I/O operations (DB queries, API calls, file
     reads) that could be combined into batch operations
   - Event processing one-at-a-time where batch processing would
     amortize overhead
   - Individual network round-trips for related data

4. **Lazy evaluation:**
   - Expensive computations performed eagerly but not always used
     (computed on init but only read in some code paths)
   - Full data loading when only metadata is needed initially
   - Constructing large objects that may be discarded without use
   - Eager joins/includes of data that isn't always accessed

5. **Precomputation:**
   - Values computed repeatedly at runtime that could be computed at
     build time, startup, or deployment
   - Lookup tables that could replace runtime computation
   - Indexes/materialized views that could accelerate frequent queries

6. **Invalidation and staleness:**
   - When suggesting caches, note the invalidation strategy needed
   - Flag existing caches that appear to lack invalidation (stale data
     risk)
   - Identify natural cache boundaries (request scope, session scope,
     global scope)

**Output:** For each opportunity, estimate the hit rate (how often the
cached value would be reused), the cost of the operation being cached
(time/resources), the cache scope and invalidation approach, and
trade-offs (memory cost of the cache).

---

### Agent: I/O & Resources (`io`)

**Objective:** Find excessive or inefficient I/O operations, resource
leaks, disproportionate resource usage, and opportunities to reduce
external interactions.

**Checklist:**

1. **Excessive I/O:**
   - File reads/writes more frequent than necessary
   - Network calls that could be eliminated or combined
   - Database queries that fetch more data than used
     (SELECT * when only specific columns needed)
   - Logging at verbose levels in production code paths

2. **Synchronous I/O on hot paths:**
   - Blocking file/network I/O on main thread / UI thread / request
     thread
   - Serialized I/O that could be parallelized
   - I/O inside loops that could be batched before/after the loop

3. **Resource leaks:**
   - File handles opened but not closed (or not closed on error paths)
   - Database connections not returned to pool
   - Network connections not properly closed
   - Temporary files not cleaned up

4. **Over-fetching and under-utilizing:**
   - Fetching entire objects/records when only a few fields are needed
   - Loading paginated data all at once
   - Downloading resources that may not be displayed/used
   - Fetching data that's already available locally

5. **Resource proportionality:**
   - Does the resource usage make sense for what the software does?
   - Thread/goroutine/task counts: are they proportional to workload?
   - Memory usage: is it reasonable for the data being processed?
   - Disk usage: temporary files, logs, caches — are they bounded?
   - Network: is the number of connections/requests proportional?

6. **Compression and encoding:**
   - Large payloads transferred without compression
   - Inefficient serialization formats (verbose JSON where binary
     would suit)
   - Image/media resources not appropriately sized or compressed
   - Base64-encoded binary data in JSON (33% overhead)

7. **Energy & battery efficiency (mobile/laptop relevant):**
   - Background task scheduling: frequent wake-ups, timers with short
     intervals, polling instead of push notifications
   - Location/sensor polling: continuous GPS updates when
     significant-change monitoring would suffice, sensors left active
     when not needed
   - Network radio management: frequent small network requests that
     prevent the radio from entering low-power state (batch requests
     instead)
   - Screen wake locks held longer than necessary
   - Unnecessary background refresh or sync operations
   - CPU-intensive work (image processing, ML inference) not deferred
     to charging/idle state when non-urgent

**Output:** For each finding, estimate the I/O savings (fewer ops, less
data transferred, reduced latency), the resource leak risk, and
implementation complexity of the fix.

---

### Agent: Concurrency (`concurrency`)

**Objective:** Find missed opportunities for parallelism, unnecessary
serialization, contention points, and concurrency anti-patterns.

**Checklist:**

1. **Missed parallelism:**
   - Independent operations executed sequentially that could run
     concurrently (independent API calls, independent computations,
     independent file operations)
   - Sequential await/then chains where concurrent execution is safe
   - Map/transform operations on collections that could be parallelized

2. **Unnecessary serialization:**
   - Global locks/mutexes protecting data that could be partitioned
   - Single-threaded bottlenecks in otherwise concurrent pipelines
   - Shared queues with high contention when per-worker queues would
     reduce contention
   - Over-synchronization: locking more data or for longer than needed

3. **Contention points:**
   - Hot locks: mutexes held during expensive operations
   - Reader-writer lock candidates: data read frequently, written
     rarely, but protected by exclusive lock
   - False sharing: per-thread data on the same cache line
   - Atomic operations that could be batched or reduced

4. **Thread/task lifecycle:**
   - Creating threads/goroutines/tasks per item instead of using pools
   - Leaked threads/tasks that never terminate
   - Unbounded task spawning without backpressure
   - Blocking operations inside non-blocking contexts (blocking in
     async, heavy computation in UI thread)

5. **Synchronization overhead:**
   - Lock acquisition in hot paths where lock-free alternatives exist
   - Excessive use of channels/queues for simple state sharing
   - Condition variable patterns that could use simpler constructs
   - Context/cancellation not propagated (orphaned work continues
     after requester gives up)

**Output:** For each finding, describe the current execution model, the
proposed concurrent model, estimated speedup (if parallelizing) or
reduced contention (if removing bottleneck), and risks (race conditions,
ordering requirements).

---

### Agent: Startup & Initialization (`startup`)

**Objective:** Find unnecessary work during application startup, slow
initialization sequences, and opportunities to defer or parallelize
boot-time operations.

**Checklist:**

1. **Heavy module-level / top-level initialization:**
   - Loading large files, making network calls, compiling regexes,
     parsing configs at import/require/init time
   - Static initializers that run before main() or app entry
   - Module-scoped constants computed from expensive operations

2. **Eager loading of deferred-use resources:**
   - Data or services loaded at startup that aren't needed until much
     later (or may never be needed in a given session)
   - Pre-fetching all reference data when only a subset is ever used
   - Initializing optional features/plugins unconditionally

3. **Sequential initialization of independent subsystems:**
   - Independent services, caches, or connections initialized one
     after another when they could be parallelized
   - Await chains at startup where concurrent initialization is safe
   - Database migrations or schema checks blocking app readiness

4. **Import chain depth / module graph analysis:**
   - Deep import trees where each import triggers more initialization
   - Circular imports causing repeated or delayed initialization
   - Transitive imports pulling in large dependency subtrees

5. **Lazy module loading opportunities:**
   - Dynamic imports, autoloading, or conditional requires that could
     replace eager top-level imports
   - Feature-flagged code paths whose dependencies are loaded even
     when the feature is disabled
   - Platform-specific code loaded on all platforms

6. **Class/struct static initializers doing expensive work:**
   - Database connections, file I/O, or cryptographic setup in static
     init blocks
   - Global singleton initialization that triggers cascading setup
   - Service locator / dependency injection container assembly overhead

7. **Splash screen / time-to-interactive analysis:**
   - What happens between process start and first user-visible content?
   - Work that blocks the first frame/render/response
   - Assets or data that must be loaded before the UI can appear

8. **Plugin/extension loading:**
   - Plugin discovery and loading that blocks startup when it could
     be deferred
   - Extensions registered synchronously when lazy registration would
     work
   - Plugin validation/verification at startup vs. on first use

9. **Configuration parsing and validation:**
   - Config files parsed and validated on every restart when results
     could be cached across restarts
   - Environment variable processing that does redundant work
   - Schema validation of static configs that rarely change

10. **Service registration / DI container setup:**
    - Dependency injection container scanning all types at startup
    - Service registration that instantiates services eagerly when
      lazy instantiation is available
    - Health checks or readiness probes that trigger premature
      initialization of downstream services

**Output:** For each finding, describe what work is happening at startup,
how long it likely takes (if estimable), whether it can be deferred,
parallelized, or cached, and the expected improvement to time-to-ready
or time-to-interactive.

---

### Agent: Rendering & UI Performance (`rendering`)

**Objective:** Find UI rendering bottlenecks — excessive redraws, layout
thrashing, animation jank, and large view hierarchies that degrade
perceived performance and responsiveness.

**Checklist:**

1. **Excessive view/component re-renders:**
   - Unnecessary state changes triggering re-renders (cover React,
     SwiftUI, Flutter, Vue, and other UI frameworks)
   - Missing shouldComponentUpdate, React.memo, useMemo, or
     equivalent optimization
   - State stored at too high a level, causing subtree re-renders
   - SwiftUI body recomputation due to unnecessary @State/@Published
     changes

2. **Layout thrashing:**
   - Reading layout properties then writing styles in alternation,
     forcing the layout engine to recalculate repeatedly
   - DOM reads interleaved with DOM writes in a loop
   - Measuring view dimensions during batch updates

3. **Expensive computation in the render/paint path:**
   - Formatting, filtering, or sorting inside the view body or render
     method
   - Complex string interpolation or date formatting per render
   - Allocating closures or objects inside the render path

4. **Large or deeply nested view hierarchies:**
   - Deeply nested view trees that slow diffing/reconciliation
   - Flat structures with hundreds of siblings
   - Unnecessary wrapper views/components adding depth without purpose

5. **Missing virtualization for long lists:**
   - No LazyVStack/LazyHStack (SwiftUI), react-window/react-virtuoso
     (React), RecyclerView (Android), or equivalent
   - Rendering all items in a long list instead of only visible items
   - Custom scroll implementations that don't recycle views

6. **Animation performance:**
   - Animations not running on the compositor thread
   - JavaScript-driven animations where CSS transitions or Core
     Animation would be smoother
   - Animating layout-triggering properties (width, height, top, left)
     instead of transform/opacity
   - Animation callbacks doing expensive work

7. **Render-blocking resources:**
   - Synchronous script loading blocking first paint
   - CSS in the critical path that could be deferred
   - Font loading causing flash of invisible/unstyled text

8. **Image/media rendering:**
   - Uncompressed images loaded at full resolution when displayed at
     thumbnail size
   - Missing image caching or duplicate image decoding
   - Images decoded on the main thread
   - Video/media auto-loading when off-screen

9. **Forced synchronous layouts:**
   - Measuring DOM/view dimensions during batch updates
   - Querying computed styles inside update loops
   - Layout reads that force pending style recalculations

10. **Scroll performance:**
    - Heavy scroll event handlers without throttling/debouncing
    - Lack of passive event listeners on scroll/touch handlers
    - Complex views inside scroll containers without recycling

11. **Off-screen rendering:**
    - Preparing views/components that aren't visible and may never
      become visible
    - Pre-rendering content far outside the viewport
    - Shadow/blur effects triggering off-screen render passes

12. **Main thread congestion:**
    - Non-UI work executing on the main/UI thread, blocking user
      interaction
    - Long-running computations not dispatched to background threads
    - Synchronous network or file I/O on the UI thread

**Output:** For each finding, describe the rendering bottleneck, which
framework/platform it applies to, estimated frame drops or jank impact,
and the specific fix (with code pattern if applicable).

---

### Agent: Database & Query Performance (`database`)

**Objective:** Find database-level performance issues — missing indexes,
inefficient queries, N+1 patterns, connection mismanagement, and schema
design problems that cause slow reads or writes.

**Checklist:**

1. **Missing indexes:**
   - Code that filters, sorts, or joins on columns that likely lack
     indexes (identify from ORM queries, raw SQL, or query builder
     calls)
   - Composite index opportunities for multi-column WHERE clauses
   - Foreign key columns used in JOINs without indexes

2. **Full table scans:**
   - Queries without WHERE clauses on large tables
   - WHERE clauses on unindexed columns
   - LIKE queries with leading wildcards ('%term')
   - Function calls on indexed columns in WHERE (breaking index usage)

3. **SELECT * patterns:**
   - Fetching all columns when only a subset is needed
   - ORM default behavior loading all fields
   - Queries returning columns that are never accessed in code

4. **N+1 queries:**
   - Iterating a collection and querying per item (ORM lazy loading,
     GraphQL resolvers, API calls per row)
   - Detecting ORM lazy-load patterns that generate per-item queries
   - Template/view code triggering queries inside loops

5. **Inefficient pagination:**
   - OFFSET-based pagination on large tables (should use cursor/keyset
     pagination)
   - COUNT(*) queries for total pages on large tables
   - Fetching all results and paginating in application code

6. **Over-joining:**
   - Queries that JOIN more tables than needed for the result
   - JOINing the same table multiple times
   - LEFT JOINs where INNER JOINs would suffice (or vice versa)
   - Cartesian products from missing JOIN conditions

7. **Missing query result limits:**
   - Queries that could return unbounded result sets
   - Missing LIMIT clauses on user-facing queries
   - Aggregations on unbounded data without pagination

8. **Connection pool sizing:**
   - Too few connections causing queuing
   - Too many connections causing database overload
   - Missing pool configuration entirely (new connection per query)
   - Connection pool exhaustion from leaked connections

9. **Transaction scope:**
   - Transactions held open during non-database work (API calls,
     computation), blocking connection return to pool
   - Long-running transactions causing lock contention
   - Missing transactions where atomicity is required

10. **Expensive aggregations:**
    - COUNT, SUM, GROUP BY on large tables without materialized views
      or summary tables
    - DISTINCT on large result sets
    - Subqueries in SELECT that execute per row

11. **Schema design for read patterns:**
    - Write-optimized schema serving read-heavy workloads (or vice
      versa)
    - Missing denormalization for frequently joined data
    - Over-normalization causing excessive JOINs for common queries

12. **ORM-generated query quality:**
    - Checking what SQL the ORM actually generates (may include
      unnecessary subqueries, poor JOIN order)
    - ORM eager-loading pulling more data than needed
    - ORM query builder producing inefficient SQL

13. **Repeated identical queries within a single request/render cycle:**
    - Same data fetched multiple times in the same request
    - Missing request-scoped query result caching
    - Middleware or interceptors triggering redundant queries

**Output:** For each finding, identify the query or pattern, the table(s)
and estimated row counts involved, the performance impact (with query
plan analysis if inferable), and the recommended fix (index, query
rewrite, schema change, caching).

---

### Agent: Build & Bundle Performance (`build`)

**Objective:** Find build-time and bundle-size issues — oversized
bundles, missing code splitting, inefficient asset pipelines, and
compilation bottlenecks that slow development iteration or bloat deployed
artifacts.

**Checklist:**

1. **Bundle size analysis:**
   - Identify the largest modules/dependencies in the final bundle
   - Check for large utility libraries imported for a single function
   - Detect vendored code that could be loaded from a CDN or package
     manager

2. **Missing code splitting:**
   - Monolithic bundles where route-based or feature-based splitting
     would reduce initial load
   - All routes/pages bundled together when lazy loading is available
   - Admin or rarely-used features included in the main bundle

3. **Tree-shaking failures:**
   - Side-effect-heavy imports that prevent dead code elimination
     (e.g., `import _ from 'lodash'` vs
     `import debounce from 'lodash/debounce'`)
   - Barrel files (index.ts re-exports) defeating tree shaking
   - CommonJS modules in an ESM build preventing tree shaking

4. **Duplicate dependencies:**
   - The same library bundled at multiple versions (check lockfiles
     for version duplication)
   - Identical functionality provided by multiple libraries
   - Forked dependencies that could be unified

5. **Unminified or uncompressed production assets:**
   - JavaScript/CSS not minified in production builds
   - Missing gzip/brotli compression configuration
   - Development-mode code included in production bundles
   - Console.log/debug statements left in production

6. **Source maps in production:**
   - Full source maps shipped to users (exposes source code, adds
     download size)
   - Source maps not properly configured for error monitoring
   - Inline source maps in production bundles

7. **Asset loading strategy:**
   - Missing preload/prefetch hints for critical assets
   - Render-blocking scripts that could be deferred or async
   - Critical CSS not inlined, non-critical CSS not deferred

8. **Image optimization:**
   - Large uncompressed images in the build output
   - Missing responsive image variants (srcset)
   - No WebP/AVIF conversion for supported browsers
   - Icons not consolidated into sprite sheets or icon fonts

9. **Font loading:**
   - Large font files with unused glyphs (font subsetting needed)
   - Flash of invisible/unstyled text (FOIT/FOUT)
   - Multiple font formats when modern formats suffice
   - Fonts loaded from third-party origins adding DNS lookup time

10. **Build-time computation:**
    - Work done at build time that should be cached (repeated code
      generation, type checking unchanged files)
    - Missing incremental compilation
    - Unnecessary full rebuilds when partial rebuilds would suffice

11. **CI/CD pipeline efficiency:**
    - Redundant build steps in the pipeline
    - Missing build caching (node_modules, derived data, Docker layers)
    - Running full test suite when only docs changed
    - Sequential pipeline stages that could run in parallel

12. **Binary size (native apps):**
    - Unused linked frameworks or libraries
    - Debug symbols in release builds
    - Bitcode overhead where not required
    - Dead code not stripped from final binary
    - Unused resources (images, strings, assets) included in the app
      bundle

**Output:** For each finding, describe the size or time impact (bundle
KB/MB, build seconds/minutes), the specific dependency or configuration
causing the issue, and the recommended fix with expected improvement.

---

## Report Format

The final report follows this structure:

```markdown
# Performance Audit Report

**Target:** {target path}
**Date:** {date}
**Languages:** {detected languages}
**Audited domains:** {list}
**Scope:** {full repo | specific paths}

## Executive Summary

{2-3 paragraph overview: what was audited, key performance concerns,
overall efficiency assessment, top recommendations}

### Impact Distribution

| Severity | Count |
|---|---|
| CRITICAL | N |
| HIGH | N |
| MEDIUM | N |
| LOW | N |
| INFO | N |

### Top Recommendations

{Numbered list of the 3-5 highest-impact changes, each with a one-line
description and estimated benefit}

## Critical Findings

### [P-001] {Title}

- **Impact:** CRITICAL
- **Confidence:** CONFIRMED / LIKELY / POSSIBLE
- **Domain:** {redundancy/memory/algorithm/caching/io/concurrency/startup/rendering/database/build}
- **Location:** {file:line}
- **Description:** {what the inefficiency is}
- **Current behavior:** {what happens now, with complexity/cost}
- **Recommended fix:** {specific change with code outline if helpful}
- **Estimated benefit:** {quantified improvement where possible}

## High Findings
{same format as critical}

## Medium Findings
{same format}

## Low Findings
{same format}

## Informational
{same format}

## Cross-cutting Recommendations

{Compound findings that span multiple domains — e.g., "cache the result
of X to eliminate both the redundant computation (P-003) and the
repeated I/O (P-007)"}

## Measurement & Validation

{For the top findings, suggest specific ways to measure the actual impact:
- Profiling approaches: which profiler to use, which code path to profile
- Benchmark suggestions: what to measure before and after a fix
- Instrumentation points: where to add metrics/timers to track real-world impact
- Load/stress testing: scenarios that would surface the identified bottlenecks

This section helps the team validate findings with data rather than
relying solely on static analysis.}

## Methodology

{domains audited, approach taken, language references used, limitations}
```

### Confidence Levels

Each finding includes a confidence field to indicate how certain the
analysis is:

- **CONFIRMED:** Static analysis proves the issue — the code clearly
  exhibits the inefficiency (e.g., nested loops over the same collection,
  missing index on a filtered column, synchronous I/O on the main thread).
- **LIKELY:** The pattern strongly suggests the issue, but runtime
  behavior may vary (e.g., a function appears pure and called repeatedly,
  but memoization benefit depends on argument distribution; an N+1 pattern
  exists but the collection size is unknown).
- **POSSIBLE:** Heuristic match — the code pattern is suspicious but
  needs profiling to confirm (e.g., a loop body may be expensive but
  iteration count is dynamic; a query may cause a full table scan
  depending on data distribution and database query planner behavior).

---

## Rules

1. **Read-only audit.** Agents analyze code but do NOT modify it. The
   report recommends changes; the user decides what to implement.

2. **Parallel execution.** All domain agents run in parallel. The
   orchestrator waits for all to complete before cross-cutting analysis.

3. **Evidence everything.** Every finding must include:
   - Specific file and line location(s)
   - Description of the inefficiency
   - Estimated impact (quantified when possible)
   - Concrete recommended fix
   - Confidence level (CONFIRMED, LIKELY, or POSSIBLE)

4. **Severity must be justified.** CRITICAL and HIGH findings need a
   clear argument for impact — "this is O(n^2) and n can be large" is
   justified; "this could be faster" is not.

5. **Language-specific awareness.** Agents MUST reference the loaded
   language reference files and check for language-specific patterns.
   Generic advice ("consider caching") without grounding in the actual
   code is not acceptable.

6. **Deduplicate across agents.** Multiple agents may flag the same code
   from different angles. The orchestrator deduplicates in the final
   report, keeping the most actionable write-up and noting which domains
   identified it.

7. **No premature optimization advice.** Don't flag code that runs once
   at startup or rarely-used code paths with the same severity as hot
   path issues. Context matters — frequency x cost = impact. Use the
   hot/warm/cold path classification from recon to calibrate severity.

8. **Recon informs agents.** The reconnaissance summary identifies hot
   paths, entry points, architecture, and path frequency classification.
   Agents should prioritize HOT paths over WARM, and WARM over COLD.
   Code that runs once at startup is less important than code that runs
   per-request or per-frame.

9. **Fail gracefully.** If an agent can't fully analyze a code region
   (e.g., dynamic dispatch makes call tracing impossible), note the
   limitation and move on rather than guessing.

10. **Scope boundaries.** Only analyze code within --target and --scope.
    Note dependencies and external services as context but don't audit
    third-party library internals.

## Orchestrator Implementation

The orchestrator (main conversation) executes this sequence:

```
1. PARSE ARGUMENTS
   - Validate --target exists (or use cwd)
   - Validate --scope paths exist within target
   - Determine domains to audit based on --focus
     (valid: redundancy, memory, algorithm, caching, io, concurrency,
      startup, rendering, database, build)

2. RECONNAISSANCE (Phase 0)
   - Detect languages and frameworks
   - Map architecture and hot paths
   - Classify code paths as HOT / WARM / COLD
   - Load language-specific references from references/lang-*.md
   - Produce RECON-SUMMARY.md (including path classification)

3. SPAWN AGENTS (Phase 1)
   - For each domain in --focus (default: all 10 domains):
     - Spawn an agent with:
       - subagent_type: "general-purpose"
       - The appropriate Agent Brief from above
       - Recon summary content (including hot/warm/cold classification)
       - Language-specific reference content
       - Target path and scope
       - Instruction to write findings to findings-{domain}.md
       - Instruction to assign confidence (CONFIRMED/LIKELY/POSSIBLE)
         to every finding
   - All agents run in parallel (use multiple Agent tool calls in one
     message)

4. CROSS-CUTTING ANALYSIS (Phase 2)
   - Read all findings-{domain}.md files
   - Identify compound findings across domains
   - Spawn Synthesis agent if compound findings exist

5. GENERATE REPORT (Phase 3)
   - Merge, deduplicate, and sort findings
   - Generate the final report (including Measurement & Validation
     section for top findings)
   - Print summary table to conversation

6. CLEANUP
   - Remove intermediate findings files (keep final report only)
   - Send the report file to the user
```

## Agent Spawning Details

When spawning each domain agent, use:
- `subagent_type: "general-purpose"` for all agents
- Include the full agent brief from the relevant section above
- Prefix the prompt with the recon summary and language reference content
- Include explicit instructions about output file path
- Inform agents they are READ-ONLY — no code modifications
- Instruct agents to assign a confidence level (CONFIRMED / LIKELY /
  POSSIBLE) to every finding

The orchestrator MUST spawn all Phase 1 agents in a SINGLE message
with multiple `Agent` tool calls so they run concurrently. Do NOT
spawn them sequentially.
