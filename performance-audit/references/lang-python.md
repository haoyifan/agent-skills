# Python Performance Patterns

## GIL & Concurrency

- **CPU-bound work in threads**: Python's GIL means `threading` does not parallelize CPU-bound work. Use `multiprocessing`, `concurrent.futures.ProcessPoolExecutor`, or C extensions for CPU-intensive tasks. Threads are only beneficial for I/O-bound work.
- **Async without actual concurrency**: using `async/await` but calling synchronous blocking functions (e.g., `requests.get`, `time.sleep`, file I/O without `aiofiles`) blocks the entire event loop.
- **`asyncio.gather` vs sequential awaits**: multiple independent `await` calls that could run concurrently should use `asyncio.gather()` or `asyncio.TaskGroup`.

## Memory & Allocation

- **Large list comprehensions instead of generators**: `[x for x in huge_iterable]` materializes the entire list in memory. Use generator expressions `(x for x in huge_iterable)` when only iterating once.
- **String concatenation in loops**: `result += string` in a loop is O(n²) due to immutable string copying. Use `"".join(parts)` or `io.StringIO`.
- **Global mutable default arguments**: `def func(items=[])` shares the list across calls — this is a correctness bug that also causes unbounded memory growth.
- **Holding references in module-level collections**: module-level dicts/lists used as registries grow unboundedly if entries are never removed. Consider `weakref.WeakValueDictionary`.
- **Pandas `.copy()` abuse or neglect**: unnecessary `.copy()` doubles memory; missing `.copy()` causes `SettingWithCopyWarning` and silent mutation of original DataFrames.
- **Loading entire files into memory**: `file.read()` or `pd.read_csv()` on huge files — use chunked reading (`pd.read_csv(chunksize=...)`, line-by-line iteration, or memory-mapped files).
- **`__slots__` for data-heavy classes**: classes with many instances (millions) waste memory on per-instance `__dict__`. Adding `__slots__` eliminates the dict overhead.

## Computation & Algorithms

- **Quadratic `in` checks on lists**: `if x in large_list` is O(n). Convert to a `set` for O(1) lookups when checking membership repeatedly.
- **Repeated DataFrame operations**: calling `.groupby()`, `.merge()`, or `.apply()` multiple times on the same data with the same parameters — cache the result.
- **`apply()` instead of vectorized ops**: `df.apply(lambda row: row['a'] + row['b'], axis=1)` is orders of magnitude slower than `df['a'] + df['b']`. Use numpy/pandas vectorized operations.
- **Unnecessary re-compilation of regex**: `re.search(pattern, string)` compiles the pattern on every call. Use `re.compile(pattern)` and reuse the compiled object.
- **Quadratic nested loops over data structures**: double loops over lists where a dict/set lookup would suffice.
- **Sorting when only min/max needed**: `sorted(items)[0]` or `sorted(items)[-1]` is O(n log n) when `min()`/`max()` is O(n). For top-k, use `heapq.nsmallest`/`heapq.nlargest`.

## I/O & Resources

- **N+1 queries in ORM loops**: iterating over a queryset and accessing related objects inside the loop triggers a query per row. Use `select_related()` / `prefetch_related()` (Django) or `joinedload()` (SQLAlchemy).
- **Unbatched database inserts**: inserting rows one at a time in a loop instead of `bulk_create()` / `executemany()` / `COPY`.
- **Missing connection pooling**: creating a new DB connection per request instead of using a pool (SQLAlchemy `create_engine` with pool, Django's `CONN_MAX_AGE`).
- **Synchronous HTTP calls in a loop**: sequential `requests.get()` calls that could use `asyncio` + `aiohttp`, `concurrent.futures`, or batch APIs.
- **Logging format strings**: `logging.debug(f"data: {expensive_repr()}")` evaluates the f-string even when debug logging is disabled. Use `logging.debug("data: %s", data)` for lazy formatting.
- **Unclosed file handles / connections**: relying on garbage collection to close files/sockets instead of using `with` statements or explicit `.close()`.

## Caching

- **Missing `@functools.lru_cache`/`@functools.cache`**: pure functions called repeatedly with the same arguments (especially recursive functions like Fibonacci, tree traversals) should be memoized.
- **Unbounded caches**: `@lru_cache` without `maxsize` (or `@cache`) grows without bound — fine for small key spaces, dangerous for large/unbounded ones.
- **Caching unhashable arguments**: trying to cache functions that take lists or dicts — convert to tuples/frozensets or use a manual cache with serialized keys.
- **Module-level computation**: expensive operations at import time (loading large files, making API calls, heavy computation) execute on every import and slow down startup.

## Python-Specific Gotchas

- **`datetime.now()` in default arguments**: evaluated once at definition time, not at each call — stale timestamps.
- **Deep copy vs shallow copy confusion**: `copy.deepcopy()` on objects with complex graphs is extremely slow. Verify whether a shallow copy suffices.
- **`isinstance` checks in hot loops**: use structural patterns or polymorphism instead of repeated type checking.
- **Unpacking large iterables**: `a, *rest = huge_list` materializes `rest` as a full list.
