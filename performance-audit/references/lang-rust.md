# Rust Performance Patterns

## Memory & Allocation

- **Unnecessary `clone()`**: calling `.clone()` to satisfy the borrow checker when restructuring code to use references or lifetimes would be more efficient. Especially costly on `String`, `Vec`, `HashMap`, and types containing them.
- **Heap allocations where stack suffices**: using `Box<T>` or `Vec<T>` for small, fixed-size data that could be stack-allocated arrays or inline structs.
- **`String` where `&str` suffices**: functions accepting `String` parameters force callers to allocate. Accept `&str` or `impl AsRef<str>` when ownership isn't needed.
- **`Vec` growth without pre-allocation**: `Vec::new()` followed by repeated `push` causes reallocations. Use `Vec::with_capacity(n)` when the size is known or estimable.
- **`to_string()` / `format!()` in hot paths**: string formatting allocates. In tight loops, consider reusing a `String` buffer with `write!()` or using `itoa`/`ryu` for number-to-string conversion.
- **`Arc` where `Rc` suffices**: `Arc` has atomic reference counting overhead. Use `Rc` for single-threaded contexts.
- **Excessive `Arc<Mutex<T>>`**: fine-grained locking with many `Arc<Mutex<T>>` adds overhead. Consider `RwLock`, lock-free data structures, or message passing.

## Computation & Algorithms

- **Missing iterator combinators**: manual loops with `push` where `.collect()`, `.map()`, `.filter()`, `.fold()` would fuse operations and enable LLVM auto-vectorization.
- **`HashMap` for small collections**: for < ~20 elements, a sorted `Vec` with binary search or a `BTreeMap` often outperforms `HashMap` due to cache locality. For tiny maps (< 8 elements), linear scan of a `Vec<(K, V)>` wins.
- **Default hasher**: `HashMap` uses `SipHash` (DoS-resistant but slower). For non-adversarial inputs, `FxHashMap` (`rustc-hash`) or `AHashMap` (`ahash`) are 2-5x faster.
- **Bounds checking in hot loops**: indexing with `v[i]` includes bounds checks. Use iterators (`.iter()`, `.chunks()`) to eliminate them, or `unsafe { v.get_unchecked(i) }` when correctness is proven.
- **Dynamic dispatch in tight loops**: `dyn Trait` calls go through vtables. For inner loops, use generics (monomorphization) or `enum` dispatch for a known set of types.
- **Unnecessary `collect()` between iterator chains**: `.iter().map(f).collect::<Vec<_>>().iter().filter(g)` materializes an intermediate `Vec`. Chain the operations: `.iter().map(f).filter(g)`.
- **`Cow<str>` / `Cow<[T]>` for conditional cloning**: when a function sometimes needs to modify data and sometimes doesn't, `Cow` avoids allocating in the no-modification case.

## Concurrency

- **Lock contention on `Mutex`**: a single `Mutex` protecting shared state accessed by many threads. Use `RwLock` for read-heavy workloads, sharding, or `crossbeam` concurrent data structures.
- **Channel overhead**: `std::sync::mpsc` is not the fastest channel. For high-throughput, consider `crossbeam-channel` or `flume`.
- **`tokio::spawn` per item**: spawning a task per item in a large collection. Use `futures::stream::iter(...).buffer_unordered(concurrency_limit)` for bounded concurrency.
- **Blocking in async context**: calling blocking I/O, CPU-heavy computation, or `std::sync::Mutex::lock()` inside an async task blocks the executor thread. Use `tokio::task::spawn_blocking` or `tokio::sync::Mutex`.
- **False sharing**: multiple threads writing to adjacent cache lines (e.g., adjacent elements in a shared array, adjacent fields in a struct). Pad with `#[repr(align(64))]` or use per-thread accumulators.

## I/O & Resources

- **Unbuffered I/O**: `File::read` / `File::write` without `BufReader`/`BufWriter` makes a syscall per operation. Always wrap in buffered I/O for non-trivial read/write patterns.
- **Synchronous I/O in async code**: using `std::fs` in a `tokio` async context. Use `tokio::fs` or `spawn_blocking`.
- **Serialization overhead**: `serde_json` with default settings is good but not optimal. For maximum throughput: `simd-json` for parsing, `serde_json::to_writer` (streaming) over `to_string` (allocating).
- **Regex compilation**: `Regex::new()` compiles the pattern — call once and reuse. Use `lazy_static!` or `once_cell::sync::Lazy` for regex at module scope.
- **Missing `#[inline]` on small hot functions across crate boundaries**: LLVM can only inline across crate boundaries if the function is marked `#[inline]`. Small functions in library crates called from hot paths benefit from this.

## Build & Compilation

- **Release mode**: debug builds are 10-100x slower. Always benchmark in `--release` mode.
- **LTO (Link-Time Optimization)**: `lto = true` in `Cargo.toml` `[profile.release]` enables cross-crate inlining and dead-code elimination. `lto = "thin"` is a faster alternative with most of the benefit.
- **`codegen-units = 1`**: reducing codegen units (default 16) allows more optimization at the cost of longer compile times. Best for release builds.
- **`target-cpu = native`**: `RUSTFLAGS="-C target-cpu=native"` enables CPU-specific optimizations (AVX2, etc.) for the build machine.
- **Profile-Guided Optimization (PGO)**: collect runtime profiles and feed them to rustc for 10-20% improvements on hot paths.
