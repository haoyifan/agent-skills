# C / C++ Performance Patterns

## Memory & Allocation

- **Heap allocation in hot loops**: `malloc`/`new` inside tight loops. Pre-allocate buffers, use stack allocation, or use memory pools/arenas for short-lived allocations.
- **Memory fragmentation**: many small allocations of varying sizes fragment the heap. Use pool allocators (`tcmalloc`, `jemalloc`) or arena allocation for same-lifetime objects.
- **Unnecessary `std::string` copies**: passing `std::string` by value instead of `const std::string&` or `std::string_view`. In C++17+, use `std::string_view` for non-owning read access.
- **`std::vector` reallocation**: `push_back` without `reserve()` causes repeated reallocation and copy/move of all elements. Pre-allocate with `reserve(n)` when size is known.
- **Smart pointer overhead**: `std::shared_ptr` has atomic reference counting overhead. Use `std::unique_ptr` when ownership is exclusive. Avoid `make_shared` in hot paths if the control block + object allocation pattern doesn't suit.
- **Cache-unfriendly data layouts**: array of structs (AoS) vs struct of arrays (SoA) — for SIMD or sequential access of single fields, SoA is faster. Related: padding and alignment of struct fields.
- **Memory leaks**: missing `free`/`delete`, or exceptions bypassing cleanup in C++ code without RAII. Use RAII wrappers, smart pointers, and containers.

## Computation & Algorithms

- **Virtual function calls in tight loops**: vtable dispatch prevents inlining. For hot inner loops, use CRTP (static polymorphism), templates, or `if constexpr` dispatch.
- **Branch misprediction**: data-dependent branches in tight loops (e.g., `if (data[i] > threshold)`) cause pipeline stalls. Use branchless techniques (`cmov`, bitwise tricks) or sort data to improve prediction.
- **SIMD-unfriendly code**: scalar processing of arrays that could use SSE/AVX/NEON. Auto-vectorization requires: no loop-carried dependencies, simple data types, aligned access, and no function calls in the loop body.
- **Unnecessary copies in range-based for**: `for (auto x : container)` copies each element. Use `for (const auto& x : container)` for read access.
- **`std::map` where `std::unordered_map` suffices**: `std::map` is a red-black tree (O(log n) lookup) while `std::unordered_map` is O(1). For small collections, `std::vector` with linear search may beat both due to cache locality.
- **Exception handling overhead**: exceptions that are thrown frequently (not just on error paths) have significant overhead. Use error codes or `std::expected` (C++23) for expected failure cases.
- **Floating-point precision flags**: `-ffast-math` enables optimizations (FMA, reordering) that break strict IEEE 754 compliance but can significantly speed up numerical code. Use per-function with `#pragma` when only some code can tolerate it.

## Concurrency

- **False sharing**: threads writing to variables that share a cache line. Align with `alignas(64)` or pad between per-thread data.
- **Lock contention**: `std::mutex` on hot paths accessed by many threads. Use `std::shared_mutex` for read-heavy workloads, lock-free atomics, or thread-local accumulation with periodic merge.
- **Atomic memory order**: `std::atomic` defaults to `memory_order_seq_cst` (strongest, slowest). Use `memory_order_relaxed`, `acquire`, `release` when sequential consistency isn't needed.
- **Thread creation cost**: `std::thread` per task is expensive. Use thread pools (`std::async` with a custom executor, TBB, or a simple worker pool).
- **Excessive synchronization**: barriers, mutexes, or condition variables that force threads to wait when data partitioning could eliminate sharing entirely.

## I/O & Resources

- **Unbuffered I/O**: `read()`/`write()` syscalls on small chunks. Use `stdio` buffering, `mmap`, or user-space buffering.
- **`std::endl` vs `'\n'`**: `std::endl` flushes the stream buffer on every use. Use `'\n'` for newlines and flush explicitly when needed.
- **File I/O in hot paths**: `fopen`/`fclose` per record instead of batch processing. Use memory-mapped I/O (`mmap`) for random access patterns on large files.
- **System call overhead**: frequent small syscalls (`read`, `write`, `gettimeofday`). Batch operations, use `io_uring` (Linux) for async I/O, or `vDSO` for time queries.
- **Dynamic library loading overhead**: `dlopen`/`dlsym` in hot paths. Load once at startup and cache function pointers.

## Build & Compilation

- **Missing optimization flags**: building without `-O2`/`-O3` for release. `-O2` is the baseline; `-O3` enables auto-vectorization and aggressive inlining.
- **LTO (Link-Time Optimization)**: `-flto` enables cross-translation-unit inlining and dead-code elimination. Significant for large projects with many small functions across files.
- **PGO (Profile-Guided Optimization)**: compile with `-fprofile-generate`, run representative workload, recompile with `-fprofile-use`. Typically 10-20% improvement.
- **Debug symbols in release**: `-g` doesn't affect code generation but increases binary size. Use separate debug info (`-gsplit-dwarf`) or strip for deployment.
- **Include bloat**: heavy headers (Boost, STL containers) in frequently compiled files. Use forward declarations and the pimpl idiom to reduce compile-time and potentially reduce code bloat from template instantiation.
