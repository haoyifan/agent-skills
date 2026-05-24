# Swift / SwiftUI Performance Patterns

## Memory & ARC

- **Retain cycles in closures**: closures capturing `self` strongly inside classes create cycles. Look for missing `[weak self]` or `[unowned self]` in escaping closures, especially in completion handlers, NotificationCenter observers, Combine sinks, and Timer callbacks.
- **Retain cycles in delegates**: delegate properties declared as `var delegate: SomeProtocol` instead of `weak var delegate: SomeProtocol?` cause cycles when the delegate holds a reference to the delegator.
- **Large value types**: structs containing arrays, dictionaries, or strings trigger copy-on-write only when mutated through a non-unique reference — but passing large structs through multiple function calls creates unnecessary copies on the stack. Watch for structs > 64 bytes being passed by value in hot paths.
- **String bridging**: repeated `String`↔`NSString` bridging in loops (common with Foundation APIs) allocates on every conversion.
- **Autorelease pool exhaustion**: tight loops creating many temporary Objective-C objects without `autoreleasepool {}` blocks cause memory spikes before the outer pool drains.
- **Unnecessary boxing**: storing value types in `[Any]` or using `AnyHashable` keys forces heap allocation for each value.

## Computation & Algorithms

- **Quadratic string operations**: `String` in Swift is not random-access — `string.count`, indexing via `string.index(string.startIndex, offsetBy: n)`, and slicing are O(n). Nested use in loops produces O(n²).
- **Repeated `filter`/`map`/`compactMap` chains**: chaining multiple lazy-capable operations on arrays creates intermediate arrays. Use `.lazy` to fuse iterations, or combine into a single pass.
- **Dictionary lookups in loops**: calling `dictionary[key]` inside a loop over the same dictionary's keys — restructure to iterate `.values` or `.enumerated()` directly.
- **Redundant sorting**: sorting an already-sorted collection, or sorting then filtering (filter first, sort the smaller set).
- **`contains(where:)` on arrays**: when checking membership repeatedly, convert to a `Set` first — `Set.contains` is O(1) vs Array's O(n).

## SwiftUI-Specific

- **View body recomputation**: the `body` property is called every time any `@State`, `@Binding`, `@ObservedObject`, or `@EnvironmentObject` changes. Expensive computation in `body` (date formatting, JSON parsing, filtering large arrays) should be cached or moved to a view model.
- **`@ObservedObject` / `@StateObject` misuse**: using `@ObservedObject` for an object the view creates (instead of `@StateObject`) causes re-creation on every parent redraw. Using `@StateObject` for an externally-owned object that should be `@ObservedObject` keeps stale references.
- **Missing `EquatableView` / custom `Equatable` on data**: SwiftUI diffing relies on `Equatable` conformance. Without it, views re-render even when data hasn't changed.
- **Unbounded `List`/`ForEach` without lazy loading**: rendering thousands of items without pagination or `LazyVStack`/`LazyHStack` loads all views into memory.
- **Frequent `objectWillChange` firing**: an `ObservableObject` with many `@Published` properties fires `objectWillChange` on every property set, even if only one property changed — causing all subscribers to re-render. Split into focused objects or use manual `objectWillChange.send()`.
- **Heavy work on main thread**: image decoding, JSON parsing, network calls on `MainActor`-isolated contexts block the UI. Should be dispatched to background with `Task.detached` or a custom actor.
- **Image loading without caching**: loading images from disk/network in `body` without `AsyncImage` caching or a shared image cache causes repeated I/O.

## Concurrency

- **Actor contention**: overusing a single global actor (or `@MainActor`) as a synchronization point creates a bottleneck. Spread work across dedicated actors when tasks are independent.
- **Unnecessary `await` serialization**: sequential `await` calls that don't depend on each other should use `async let` or `TaskGroup` to run concurrently.
- **Task over-creation**: spawning a `Task {}` per item in a large loop floods the cooperative thread pool. Use `TaskGroup` with bounded concurrency or process in batches.
- **GCD → Swift Concurrency bridging overhead**: wrapping `DispatchQueue.async` inside async functions (or vice versa) introduces unnecessary context switches.

## I/O & Resources

- **Synchronous file I/O on main thread**: `FileManager` operations, `Data(contentsOf:)`, and `JSONDecoder().decode()` on large files block the calling thread.
- **Unbounded Core Data fetch**: `NSFetchRequest` without `fetchBatchSize` or `fetchLimit` loads entire result sets into memory.
- **UserDefaults abuse**: storing large blobs (images, arrays of thousands of items) in `UserDefaults` — it's plist-backed and loaded entirely into memory on first access.
- **Notification observer leaks**: adding `NotificationCenter` observers without removing them (or relying on deprecated auto-removal) causes observers to accumulate and fire redundantly.
- **Timer without invalidation**: `Timer.scheduledTimer` that's never invalidated keeps firing, retains its target, and wastes CPU.
- **URLSession configuration**: creating a new `URLSession` per request instead of reusing a shared session wastes connection pool resources and disables HTTP/2 multiplexing.

## Compilation & Build

- **Type inference in complex expressions**: long chains of operators or closures with inferred types force the type checker into exponential behavior. Adding explicit type annotations to intermediate variables reduces compile time.
- **Large switch/if-else chains in `body`**: deeply nested conditionals in SwiftUI `body` increase type-checker workload. Extract into helper `@ViewBuilder` methods.
