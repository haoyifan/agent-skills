# Rust Refactoring Patterns

## Sync Operations in Async Context (Critical)

- **Blocking I/O in async tasks**: calling `std::fs`, `std::net`, `std::io::Read/Write`, or any blocking syscall inside an `async fn` or `tokio::spawn` block starves the executor thread pool. Use `tokio::fs`, `tokio::net`, or wrap with `tokio::task::spawn_blocking`.
- **`std::sync::Mutex` in async code**: `std::sync::Mutex::lock()` blocks the thread while holding the lock across an `.await` point. Use `tokio::sync::Mutex` when the lock must be held across await points. If the critical section is short and never crosses an await, `std::sync::Mutex` is fine — but flag cases where it does cross.
- **`std::thread::sleep` in async code**: blocks the executor thread. Use `tokio::time::sleep` instead.
- **Synchronous HTTP clients in async**: using `reqwest::blocking` or `ureq` inside async context. Use the async `reqwest` client.
- **`std::sync::mpsc` in async code**: the receiver's `recv()` blocks. Use `tokio::sync::mpsc`, `broadcast`, or `watch` channels.
- **CPU-heavy computation in async tasks**: long-running CPU work (parsing, compression, hashing large data) blocks the executor. Move to `spawn_blocking` or a dedicated thread pool.

## Type Safety & Stringly-Typed Code

- **`String`/`&str` for domain values**: function parameters like `fn create_user(name: String, email: String, role: String)` provide no compile-time protection against argument swapping. Wrap in newtypes: `struct Email(String)`, `struct Role(String)`.
- **`Vec<String>` for structured collections**: a `Vec<String>` carrying tags, permissions, or identifiers loses semantic meaning. Use `Vec<Tag>`, `Vec<Permission>` with newtypes or enums.
- **String enums**: values like `"admin"`, `"user"`, `"guest"` passed as `&str` should be `enum Role { Admin, User, Guest }`. The compiler catches typos and exhaustiveness.
- **Stringly-typed IDs**: `user_id: String`, `order_id: String` can be accidentally swapped. Use `struct UserId(String)`, `struct OrderId(String)` or a generic `Id<T>(String, PhantomData<T>)`.
- **`HashMap<String, Value>` as pseudo-structs**: if the keys are known at compile time, use a proper struct. Reserve `HashMap` for truly dynamic keys.
- **Primitive obsession with numeric types**: `port: u16`, `timeout_ms: u64`, `retry_count: u32` — when multiple numeric parameters exist, newtypes prevent mixing them up. At minimum, use type aliases for documentation.
- **Parse, don't validate**: accept raw `String` at the boundary, parse into a validated type immediately (`EmailAddress::parse(input)?`), and pass the validated type through the rest of the system. Never re-validate downstream.

## Error Handling

- **Silently discarded `Result`**: any `let _ = fallible_call()` or bare `fallible_call();` without handling the `Result` is a bug. The compiler warns on unused `#[must_use]` — ensure warnings are not suppressed.
- **Blanket `.unwrap()` / `.expect()` outside tests**: panics in production code crash the process. Use `?` propagation, `.unwrap_or_default()`, or explicit match. `.expect("reason")` is acceptable only for invariants that are truly impossible to violate.
- **`Box<dyn Error>` or `anyhow::Error` in library crates**: libraries should define typed error enums so callers can match. Reserve `anyhow` for applications and `thiserror` for libraries.
- **Swallowed errors in `map` / `for_each`**: `.for_each(|item| { let _ = process(item); })` silently drops errors. Collect results or use `try_for_each`.
- **Ignoring errors in `Drop` implementations**: `Drop::drop` can't return errors, but logging or recording the failure is better than silently ignoring it.
- **Overly broad error types**: a single `AppError` enum with 30 variants used everywhere. Scope error types to the module or layer — a parsing module shouldn't carry network error variants.
- **Missing context on error propagation**: bare `?` without `.map_err()` or `context()` (anyhow) loses the call site. Add context at module boundaries: `file.read().context("reading config file")?`.

## Crate Structure & Compilation Speed

- **Monolithic crates with high internal coupling**: a single crate where changing any file recompiles everything. Split along natural boundaries — a `types` crate for shared data structures, a `core` crate for business logic, and leaf crates for I/O and CLI. The type crate changes rarely and downstream crates compile in parallel.
- **Unnecessary dependencies**: each dependency adds compile time. Audit `Cargo.toml` for deps used in one place that could be replaced with a few lines of code. Use `cargo tree` and `cargo udeps` to find unused deps.
- **Fat feature flags**: a crate with `default = ["everything"]` pulls in dependencies that most consumers don't need. Use additive, granular feature flags.
- **Proc-macro crates not isolated**: proc macros must be in their own crate. If mixed with regular code, the entire crate becomes a proc-macro crate and its compilation becomes sequential.
- **High fan-out from core crates**: if a foundational crate depends on many other crates, it becomes a bottleneck — everything downstream waits for it. Core/types crates should have minimal or zero internal dependencies.
- **Recompilation cascading from public-API churn**: changing a public type in a low-level crate forces recompilation of everything above it. Stabilize public interfaces early, use `#[non_exhaustive]` on enums, and hide implementation details behind opaque types.
- **Build script (`build.rs`) overhead**: build scripts run on every compile if their inputs aren't declared with `rerun-if-changed`. Missing directives cause unnecessary rebuilds.
- **`include!` and `env!` preventing incremental compilation**: these macros depend on external state that the incremental compiler can't track, causing full rebuilds.

## Ownership & Borrowing

- **Cloning to satisfy the borrow checker**: excessive `.clone()` on `String`, `Vec`, `HashMap` — often a sign the data model needs restructuring. Consider `Rc`/`Arc` for shared ownership, or restructure to avoid simultaneous borrows.
- **Accepting owned types when borrowing suffices**: `fn process(data: Vec<u8>)` forces callers to give up ownership. Use `fn process(data: &[u8])` or `fn process(data: impl AsRef<[u8]>)` when the function doesn't need to own the data.
- **Returning references tied to short-lived borrows**: functions that return `&str` or `&[T]` tied to a local variable — the borrow can't outlive the function. Return owned types or use `Cow<'_, T>`.
- **`Arc<Mutex<T>>` where message passing fits**: shared mutable state through locking is error-prone. If the data has a single logical owner, use channels to send updates to it.

## API Design

- **Boolean parameters**: `fn connect(host: &str, use_tls: bool, verify_certs: bool)` — multiple booleans are unreadable at the call site. Use an options struct or builder pattern.
- **Leaking implementation details in public types**: public structs containing `HashMap`, `Vec`, or other concrete collections lock in the implementation. Expose domain-specific methods instead.
- **`impl Trait` in return position hiding important information**: `fn get_items() -> impl Iterator<Item = Foo>` hides whether the iterator is `Clone`, `Send`, `ExactSizeIterator`, etc. Be explicit when callers need those bounds.
- **Missing `#[must_use]` on types/functions with important return values**: functions that return `Result`, builder methods, or computed values should be `#[must_use]` so the compiler warns if ignored.
- **Large enums without boxing**: an enum where one variant is much larger than the others wastes memory for every instance. Box the large variant: `Large(Box<LargeStruct>)`.

## Patterns & Idioms

- **Manual trait implementations where derives suffice**: hand-written `Clone`, `Debug`, `PartialEq` that do the same thing as `#[derive(...)]` are maintenance burdens and can diverge.
- **`match` with identical arms**: multiple match arms doing the same thing should be combined with `|`.
- **Nested `Option<Option<T>>` or `Result<Result<T, E1>, E2>`**: a sign of missing flattening. Use `.flatten()`, `.and_then()`, or restructure the API.
- **Index-based iteration over collections**: `for i in 0..vec.len() { vec[i] }` instead of `for item in &vec` — loses iterator optimizations and adds bounds-check overhead.
- **`unsafe` blocks without safety comments**: every `unsafe` block should document the invariant it relies on. Missing safety docs suggest the invariant hasn't been thought through.
- **Reimplementing standard library functionality**: custom `min`/`max`, string splitting, or collection operations that `std` already provides. Prefer `std` — it's tested, optimized, and familiar.

## Testing

- **Tests that depend on global mutable state**: `static mut` or `lazy_static` state shared across tests causes flaky failures because `cargo test` runs tests in parallel. Use per-test instances or `serial_test`.
- **Integration tests in `src/`**: files in `src/tests/` are compiled with the library. True integration tests belong in `tests/` at the crate root — they compile as separate crates and test the public API.
- **Missing `#[should_panic]` or `#[ignore]` annotations**: tests expected to panic without `#[should_panic]` will fail. Long-running tests without `#[ignore]` slow down the default test suite.
