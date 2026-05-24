# Go Performance Patterns

## Memory & Allocation

- **Excessive heap allocations in hot paths**: use `go build -gcflags='-m'` or `go test -bench -benchmem` to identify escape analysis failures. Variables that escape to the heap unnecessarily (returned pointers, captured by closures, interface conversions) add GC pressure.
- **Slice pre-allocation**: `append` in a loop without pre-allocating (`make([]T, 0, expectedCap)`) causes repeated reallocations and copies as the underlying array grows.
- **String ↔ `[]byte` conversions**: each conversion allocates. In hot paths, work with `[]byte` consistently or use `unsafe.String`/`unsafe.SliceData` (Go 1.20+) when the data won't be mutated.
- **Map pre-allocation**: `make(map[K]V)` without a size hint grows incrementally. Use `make(map[K]V, expectedSize)` when the size is known.
- **Pointer-heavy data structures**: structs with many pointer fields increase GC scan time. Value types and flat structs are GC-friendlier.
- **`sync.Pool` for temporary objects**: frequently allocated and discarded objects (buffers, temporary structs) in hot paths benefit from `sync.Pool` to reuse allocations.
- **Small object allocation in loops**: creating many small objects (including small slices, maps, closures) inside tight loops generates GC pressure. Reuse or pre-allocate outside the loop.
- **`fmt.Sprintf` in hot paths**: `Sprintf` allocates — use `strconv.Itoa`, `strconv.AppendInt`, or `strings.Builder` for performance-critical string construction.

## Computation & Algorithms

- **Interface method calls in tight loops**: interface dispatch has overhead (indirect call + possible cache miss). For performance-critical inner loops, use concrete types or type-assert once before the loop.
- **Reflection in hot paths**: `reflect` package operations are slow (100x+ overhead). Avoid in request handling or data processing paths. Use code generation or type switches instead.
- **Unnecessary `defer` in tight loops**: `defer` has a small per-call overhead. In loops that execute millions of times, call cleanup directly instead.
- **Map iteration order randomization**: Go randomizes map iteration — if code depends on sorted keys, sort once and iterate the sorted slice.
- **Repeated `strings.Contains`/`strings.HasPrefix`**: for checking against many patterns, build a map or use `strings.Replacer` / compiled regex instead of N separate checks.
- **Channel over-use for synchronization**: channels have overhead vs. `sync.Mutex` or `sync.RWMutex` for simple mutual exclusion. Use channels for communication, mutexes for state protection.

## Concurrency

- **Goroutine leaks**: goroutines blocked on channel operations, `select`, or I/O that never completes accumulate forever. Always ensure goroutines have a termination path (context cancellation, done channels).
- **Unbounded goroutine spawning**: `go func()` per incoming request or per item in a large loop can spawn millions of goroutines. Use a worker pool or `semaphore.Weighted`.
- **Lock contention**: a single `sync.Mutex` protecting a hot data structure accessed by many goroutines. Consider sharding, `sync.RWMutex` (if reads dominate), or lock-free patterns with `sync/atomic`.
- **`sync.WaitGroup` misuse**: calling `wg.Add` inside the goroutine instead of before `go func()` creates a race condition.
- **Context propagation**: not passing `context.Context` through call chains prevents cancellation from propagating, leaving goroutines and I/O operations running after the caller gives up.

## I/O & Resources

- **Unbuffered I/O**: reading/writing files or network connections byte-by-byte without `bufio.Reader`/`bufio.Writer`. Default `os.File` operations are unbuffered.
- **HTTP client reuse**: creating a new `http.Client` (or using `http.DefaultClient` without tuning) per request loses connection pooling. Share a configured client with appropriate timeouts and transport settings.
- **Missing `resp.Body.Close()`**: not closing HTTP response bodies leaks connections from the pool, eventually exhausting available file descriptors.
- **Database connection pool tuning**: `sql.DB` defaults may not suit your workload. Set `SetMaxOpenConns`, `SetMaxIdleConns`, `SetConnMaxLifetime` based on expected concurrency and DB limits.
- **JSON encoding/decoding**: `encoding/json` uses reflection and is relatively slow. For high-throughput paths, consider `encoding/gob`, Protocol Buffers, or libraries like `easyjson`/`sonic` that generate code.
- **`io.ReadAll` on large responses**: reads the entire body into memory. For large payloads, stream-process with `io.Reader`/`json.Decoder`.
- **Logging in hot paths**: structured logging libraries (`zap`, `zerolog`) are fast but not free. Avoid logging per-item in tight loops — log aggregates or sample.

## Build & Binary

- **Dead code inclusion**: unused dependencies and code are excluded by the linker, but unused C dependencies via cgo are not. Audit cgo usage.
- **`-race` detector in production**: the race detector adds 5-10x overhead and significant memory usage. Use only in testing and CI.
- **PGO (Profile-Guided Optimization)**: Go 1.21+ supports PGO. Collect CPU profiles from production and feed them to the compiler for 2-7% throughput improvements on hot paths.
