# Go Refactoring Patterns

## Sync Operations in Async/Concurrent Context (Critical)

- **Blocking calls inside goroutines meant for concurrency**: performing synchronous I/O (file reads, network calls, database queries) inside a goroutine without timeouts or context cancellation. Always pass and respect `context.Context` — a blocked goroutine without cancellation leaks forever.
- **`time.Sleep` for synchronization**: using `time.Sleep` to wait for goroutines instead of `sync.WaitGroup`, channels, or `errgroup.Group`. Sleep-based synchronization is fragile and slow.
- **Blocking channel operations without `select`/`context`**: a bare `ch <- val` or `<-ch` with no `select` + `ctx.Done()` branch blocks forever if the other side disappears. Always provide a cancellation path.
- **Synchronous HTTP handlers doing blocking work**: an HTTP handler that calls a slow external service synchronously without a timeout ties up a server goroutine. Use `http.Client` with `context.Context` and deadline.
- **`sync.Mutex` held across I/O boundaries**: acquiring a lock, then doing network/disk I/O, then releasing — holds the lock far longer than necessary and serializes concurrent work. Restructure to copy data under the lock, release, then do I/O.
- **CGo calls blocking goroutine scheduling**: CGo calls block the OS thread, not just the goroutine. Heavy CGo usage can exhaust the thread limit (`GOMAXPROCS`). Use a worker pool for CGo-heavy work.

## Type Safety & Stringly-Typed Code

- **`string` for domain values**: `func CreateUser(name, email, role string)` — all three parameters are interchangeable at the call site. Define distinct types: `type Email string`, `type Role string`.
- **Enum values as strings**: `status := "active"` with comparisons scattered through the code. Define typed constants: `type Status int` with `const (Active Status = iota; Inactive; Suspended)`.
- **`map[string]interface{}` as a data structure**: if the keys and value types are known, use a struct. Reserve `map[string]interface{}` (or `map[string]any`) for truly dynamic data like unmarshaled JSON with unknown schema.
- **`interface{}` / `any` parameters**: accepting `any` defeats the type system. Use generics (Go 1.18+) or specific interfaces. If `any` is unavoidable (e.g., marshaling), constrain it as close to the boundary as possible.
- **Untyped numeric constants for different domains**: `timeout := 30` and `retries := 30` are both `int` but semantically different. Use `type Duration time.Duration` or at minimum distinct named constants.
- **`[]byte` passed everywhere without validation**: raw bytes flowing through multiple layers without being parsed into a typed structure at the boundary. Parse once at the edge, pass the structured type internally.
- **Stringly-typed IDs**: `userID string`, `orderID string` are silently interchangeable. Define `type UserID string`, `type OrderID string` — the compiler catches mix-ups.

## Error Handling

- **Ignored errors**: `result, _ := SomeFunc()` or calling a function that returns an error without capturing it. Every error must be handled or explicitly documented as intentionally ignored (and even then, log it).
- **Bare `if err != nil { return err }`**: propagating errors without context makes debugging painful. Use `fmt.Errorf("doing X: %w", err)` to wrap with context while preserving the error chain.
- **`log.Fatal` / `os.Exit` in library code**: these terminate the process — only acceptable in `main()`. Libraries should return errors and let the caller decide.
- **Error sentinel comparison with `==`**: `if err == sql.ErrNoRows` breaks when errors are wrapped. Use `errors.Is(err, sql.ErrNoRows)`.
- **Type-asserting errors with direct cast**: `if e, ok := err.(*MyError)` doesn't unwrap. Use `errors.As(err, &e)`.
- **Errors in deferred functions silently dropped**: `defer file.Close()` ignores the error from `Close()`. Capture it: `defer func() { if cerr := file.Close(); cerr != nil { ... } }()`. Especially important for writable files and database transactions.
- **Panicking in library code**: `panic` for recoverable errors forces callers into `recover()` gymnastics. Return errors instead. Reserve `panic` for truly unrecoverable programmer errors.
- **Overly broad error types**: a single `AppError` type used across the entire application. Scope error types to packages — a `storage` package shouldn't return `httpError`.

## Package Structure & Build

- **Oversized packages with high internal coupling**: a single `pkg/` directory with 50 files that all import each other. Split along domain boundaries. Smaller packages with clear APIs compile faster and are easier to test.
- **Circular imports**: Go forbids circular package imports, so developers work around them with `interface{}` or by dumping everything into one package. This is a sign the package boundaries are wrong — restructure using dependency inversion (define interfaces in the consumer package).
- **`internal/` overuse**: putting everything in `internal/` prevents reuse across modules. Only internalize what genuinely shouldn't be consumed externally.
- **Package-level `init()` functions**: `init()` runs implicitly at import time, creates hidden dependencies, complicates testing, and makes import order matter. Prefer explicit initialization functions that callers invoke.
- **Unnecessary dependencies inflating build time**: `go mod tidy` removes unused deps, but deps used for a single convenience function add disproportionate compile time. Evaluate whether a 3-line function replaces a dependency.
- **Large generated files in hot packages**: protobuf-generated code or other codegen in a frequently-changed package causes repeated recompilation. Isolate generated code in its own package.

## Interface Design

- **Premature interface definition**: defining interfaces before there are multiple implementations. In Go, interfaces are defined by the consumer, not the producer. Define interfaces where they're used, not where they're implemented.
- **Fat interfaces**: an interface with 10+ methods is hard to implement and hard to mock. Split into focused interfaces — `io.Reader`, `io.Writer`, `io.Closer` not `io.ReadWriteCloser` everywhere.
- **Returning concrete types, accepting interfaces**: functions should accept the minimal interface they need and return concrete types. `func Process(r io.Reader)` not `func Process(f *os.File)`.
- **Empty interface parameters for "flexibility"**: `func Do(opts ...interface{})` — use functional options pattern or a typed config struct instead.
- **Interface pollution in package APIs**: exporting interfaces for every type "for testing." Only export interfaces that serve a real abstraction — test fakes can use unexported interfaces or concrete types.

## Concurrency Patterns

- **Goroutine leaks**: goroutines blocked on channels, `select`, or I/O without a cancellation path accumulate. Every goroutine must have a clear shutdown signal.
- **Unbounded goroutine spawning**: `for _, item := range items { go process(item) }` with 100K items. Use `errgroup.Group` with `SetLimit()` or a worker pool.
- **Shared state without synchronization**: accessing a map, slice, or struct field from multiple goroutines without a mutex. Go's race detector (`-race`) catches this — ensure CI runs with `-race`.
- **`sync.WaitGroup.Add` inside the goroutine**: creates a race between `Add` and `Wait`. Always call `wg.Add(1)` before `go func()`.
- **Channel of channels**: `chan chan Result` patterns are almost always overcomplicated. Simplify to a single channel with a response field or use `errgroup`.
- **Missing `select` default for non-blocking operations**: if a channel send/receive should be non-blocking, use `select` with a `default` case rather than checking `len(ch)`.

## Naming & Idioms

- **Stuttering package names**: `user.UserService`, `config.ConfigManager`. In Go, the package name qualifies — use `user.Service`, `config.Manager`.
- **Getter methods with `Get` prefix**: Go convention omits `Get` — use `user.Name()` not `user.GetName()`. Exception: protobuf-generated code.
- **Unexported types returned from exported functions**: confusing API — if a function is exported, its return type should be exported or be a standard library type.
- **`util` / `helpers` / `common` packages**: these are dumping grounds. Move functions to the package that uses them, or name the package after what it does (`retry`, `httputil`).
- **Unused receiver names**: `func (s *Service) method()` where `s` is never used — use `_` as the receiver name to signal it, or question whether it should be a method at all.
- **MixedCaps for acronyms**: Go convention is `ID` not `Id`, `URL` not `Url`, `HTTP` not `Http` in exported names.

## Testing

- **Tests in the same package testing private details**: testing unexported functions couples tests to implementation. Use `package foo_test` (external test package) to test the public API — it catches broken interfaces.
- **Table-driven tests without subtests**: `for _, tc := range cases { ... }` without `t.Run(tc.name, ...)` makes failure output unreadable and prevents running individual cases.
- **Test helpers not using `t.Helper()`**: helper functions that call `t.Fatal` / `t.Error` report the wrong line number. Always start test helpers with `t.Helper()`.
- **Global state between tests**: package-level variables modified by tests and not reset cause order-dependent failures. Use `t.Cleanup` or `t.Setenv` (Go 1.17+).
- **Mocking with `interface{}` instead of focused interfaces**: creating a mock that implements a 15-method interface when the function under test only calls 2. Define a local 2-method interface in the test file.
- **Not testing error paths**: only testing the happy path. Use table-driven tests that include expected errors and verify error wrapping with `errors.Is` / `errors.As`.
