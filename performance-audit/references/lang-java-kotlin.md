# Java / Kotlin Performance Patterns

## Memory & GC

- **Autoboxing in hot paths**: using `Integer`, `Long`, `Double` instead of `int`, `long`, `double` in loops, collections, or arithmetic creates garbage. In Kotlin, nullable numeric types (`Int?`) force boxing.
- **String concatenation in loops**: `str += value` in Java creates a new `StringBuilder` and `String` per iteration. Use `StringBuilder` explicitly. Kotlin's `buildString {}` or `joinToString()` handle this.
- **Unnecessary object creation**: creating `SimpleDateFormat`, `Pattern`, `DecimalFormat` per method call instead of reusing (thread-local or `DateTimeFormatter` which is thread-safe).
- **Collection sizing**: `new ArrayList<>()` / `new HashMap<>()` without initial capacity causes repeated internal array resizing. Use `ArrayList(expectedSize)` / `HashMap(expectedSize, 0.75f)`.
- **Large object graphs in memory**: holding entire query results, file contents, or deep object trees when only a summary/subset is needed. Process in streaming fashion.
- **Kotlin data class `copy()`**: creates full shallow copies — expensive for data classes with many fields or large collections. Only use when you actually need a modified copy.
- **Kotlin coroutine context accumulation**: creating many `CoroutineContext` elements per coroutine adds allocation overhead. Reuse dispatchers and contexts.

## Computation & Algorithms

- **Stream API overhead for simple operations**: `list.stream().filter(...).map(...).collect(...)` has setup overhead (lambda capture, spliterator creation). For small collections (< 50 elements) or trivial operations, a for-loop is faster.
- **Reflection in request paths**: `Class.forName`, `method.invoke`, `field.get` are slow. Use direct calls, generated code, or `MethodHandle` for performance-critical paths. Spring and Jackson use bytecode generation to avoid this at steady state.
- **Kotlin `Sequence` vs `List` operations**: chained `map`/`filter` on `List` creates intermediate lists. Use `.asSequence()` to fuse operations (like Java `Stream` but lazier).
- **HashMap with poor `hashCode()`**: objects with colliding hash codes degrade `HashMap` to O(n) lookup. Ensure `hashCode()` distributes well.
- **Regex compilation**: `Pattern.compile()` in a method called repeatedly. Compile once as a `static final` / top-level `val` and reuse.
- **Synchronized blocks on hot paths**: `synchronized` has overhead even without contention. Use `java.util.concurrent` atomics, `ConcurrentHashMap`, or `ReadWriteLock` as appropriate.
- **Unnecessary exception creation**: exceptions capture stack traces on creation — expensive. Don't use exceptions for control flow in hot paths (e.g., catching `NumberFormatException` on every parse attempt).

## Concurrency

- **Thread creation per request**: `new Thread()` per task. Use `ExecutorService` / thread pools. In Kotlin, use coroutines with dispatchers.
- **Kotlin coroutine dispatcher misuse**: CPU-bound work on `Dispatchers.IO` (over-provisions threads) or I/O on `Dispatchers.Default` (blocks limited threads). Match dispatcher to workload.
- **Sequential coroutine launches**: `val a = async { ... }.await(); val b = async { ... }.await()` defeats concurrency. Launch both, then await: `val a = async { ... }; val b = async { ... }; a.await() to b.await()`.
- **Lock contention on shared state**: multiple threads competing for a single `ReentrantLock` or `synchronized` block. Shard the data or use lock-free structures.
- **`volatile` vs atomics**: `volatile` only guarantees visibility, not atomicity of read-modify-write. Use `AtomicInteger`, `AtomicReference`, etc. for compound operations.

## I/O & Resources

- **N+1 queries (JPA/Hibernate)**: accessing lazy-loaded collections inside a loop. Use `@EntityGraph`, `JOIN FETCH`, or batch fetch size.
- **Unbuffered I/O**: `FileInputStream`/`FileOutputStream` without `BufferedInputStream`/`BufferedOutputStream`. Or better: use `Files.newBufferedReader()` / `Files.newBufferedWriter()`.
- **Connection pool exhaustion**: holding DB connections longer than needed (e.g., doing non-DB work inside a `@Transactional` method). Keep transactions short.
- **Missing HTTP client connection pooling**: creating `HttpClient` / `OkHttpClient` per request. Share a single instance with configured pool.
- **Serialization framework overhead**: Jackson/Gson reflection on every serialize/deserialize. Use Jackson's `@JsonCreator` or code-gen (Moshi, kotlinx.serialization) for high-throughput paths.
- **Logging overhead**: `log.debug("Data: " + expensiveToString())` evaluates the string even when debug is disabled. Use parameterized logging: `log.debug("Data: {}", data)` or Kotlin's `logger.debug { "Data: $data" }`.

## JVM & Build

- **JIT warmup**: code is interpreted before the JIT compiles hot methods. For latency-sensitive services, consider warmup strategies or GraalVM native-image for AOT compilation.
- **GC tuning**: default GC (G1 since Java 9) may not suit all workloads. High-throughput batch jobs may benefit from `ZGC` or `Shenandoah` for low latency. Monitor GC pause times.
- **Missing JVM flags**: `-XX:+UseStringDeduplication` (G1 GC) reduces memory for apps with many duplicate strings. `-XX:+UseCompressedOops` (default < 32GB heap) saves memory.
- **Large jar/classpath scanning**: frameworks scanning the entire classpath at startup (Spring component scan). Narrow the scan base packages.
