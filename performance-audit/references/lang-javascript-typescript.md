# JavaScript / TypeScript Performance Patterns

## Memory & GC

- **Event listener leaks**: adding event listeners (DOM, EventEmitter, WebSocket) without removing them on cleanup. In React, missing cleanup in `useEffect` return. In Node.js, listeners accumulating on long-lived emitters.
- **Closure-captured scope**: closures in long-lived callbacks (timers, event handlers) capture their enclosing scope, preventing GC of all variables in that scope — even ones the closure doesn't use (engine-dependent).
- **Detached DOM nodes**: removing DOM elements while JS still holds a reference (in a variable, cache, or event handler) prevents GC of the entire subtree.
- **Unbounded in-memory caches**: `Map`/`Object` used as caches without eviction. Use `WeakMap` for object-keyed caches, or implement LRU eviction for string-keyed ones.
- **Large string retention**: holding references to small substrings of very large strings may retain the entire original string in some engines (V8 has mostly fixed this, but it persists in edge cases with `slice`).
- **Buffer/ArrayBuffer accumulation**: in Node.js, allocating `Buffer` objects in loops without releasing references causes memory spikes outside the V8 heap (not visible in heap snapshots).
- **`setInterval` without `clearInterval`**: intervals that fire indefinitely, especially if they accumulate closures or data.

## Computation & Algorithms

- **Unnecessary re-renders (React)**: components re-rendering due to new object/array/function references created on every render. Fix with `useMemo`, `useCallback`, or `React.memo` — but only when profiling confirms the re-render is expensive.
- **Inline object/array creation in JSX props**: `style={{ color: 'red' }}` or `items={[1,2,3]}` creates a new reference every render, defeating `React.memo`.
- **Quadratic DOM manipulation**: reading layout properties (`offsetHeight`, `getBoundingClientRect`) and then writing styles in a loop causes layout thrashing — batch reads and writes separately.
- **Repeated `Array.find`/`Array.includes` on large arrays**: convert to `Set` or `Map` for O(1) lookups.
- **JSON parse/stringify for deep clone**: `JSON.parse(JSON.stringify(obj))` is slow and drops functions, `undefined`, `Date` objects. Use `structuredClone()` or targeted spread.
- **Regex in hot loops without precompilation**: `new RegExp(pattern)` inside a loop compiles on every iteration. Define the regex once outside.
- **`Array.reduce` for simple transformations**: `reduce` for building objects/arrays is harder to optimize than a `for` loop and often less readable — profile before assuming it's fine.

## React / Frontend-Specific

- **Missing dependency arrays in hooks**: `useEffect(() => {...})` without deps runs on every render. `useMemo(() => expensive(), [])` with wrong deps recomputes unnecessarily.
- **State updates triggering cascading renders**: setting state in `useEffect` that triggers another `useEffect` creates render cascades. Derive state instead of syncing it.
- **Large context providers**: a single Context with a large object causes all consumers to re-render when any property changes. Split contexts by update frequency.
- **Unvirtualized long lists**: rendering thousands of DOM nodes for lists. Use `react-window`, `react-virtuoso`, or CSS `content-visibility: auto`.
- **Bundle size**: importing entire libraries (`import _ from 'lodash'`) instead of specific functions (`import debounce from 'lodash/debounce'`). Tree-shaking only works with ES module imports.
- **Synchronous `localStorage` access in render path**: `localStorage.getItem` is synchronous and can be slow — cache on mount, not on every render.

## Node.js / Server-Specific

- **Blocking the event loop**: CPU-intensive operations (JSON parsing large payloads, crypto, image processing, large sorts) in request handlers block all concurrent requests. Use `worker_threads` or offload to a queue.
- **Synchronous fs operations**: `fs.readFileSync`, `fs.writeFileSync` in server request handlers. Use `fs.promises` or callback-based APIs.
- **Unbatched database operations**: `await Promise.all(items.map(item => db.insert(item)))` sends N individual queries. Use bulk insert operations.
- **Missing connection pooling**: creating new DB/Redis connections per request instead of using a pool.
- **N+1 queries in GraphQL resolvers**: resolving a list field where each item triggers a separate DB query. Use DataLoader pattern for batching.
- **Stream backpressure ignored**: piping streams without handling backpressure (`readable.pipe(writable)` handles it, but manual `read`/`write` loops often don't).
- **Excessive middleware**: middleware that runs on every request but is only needed for specific routes (auth checks, body parsing, logging) — mount selectively.

## Async Patterns

- **Sequential awaits for independent operations**: `const a = await fetchA(); const b = await fetchB();` should be `const [a, b] = await Promise.all([fetchA(), fetchB()])`.
- **`await` in loops**: `for (const item of items) { await process(item); }` processes items sequentially. If independent, batch with `Promise.all` (with concurrency limits if needed).
- **Unhandled promise rejections accumulating**: promises without `.catch()` or try/catch leak — and in Node.js, can crash the process.
- **Creating Promises unnecessarily**: `async` functions already return promises — `return new Promise(resolve => resolve(value))` inside an `async` function is redundant.

## TypeScript-Specific

- **Excessive type computation at build time**: deeply recursive conditional types, large union types (100+ members), and complex mapped types slow the TypeScript compiler significantly. This doesn't affect runtime but impacts developer iteration speed.
- **`enum` vs `const enum` vs union types**: regular `enum` generates runtime code (an object with reverse mappings). `const enum` or string union types (`type Status = 'a' | 'b'`) are zero-cost at runtime.
