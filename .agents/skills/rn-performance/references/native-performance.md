# Native profiling, threading and layout

Guide basis: pp. 81–101, 126–158.

## Profile the native path

Use Instruments Time Profiler/Hangs on iOS; Android Studio CPU/system trace and Perfetto on Android. Correlate the affected interval with JS, main/UI, module/background threads and GPU/layout activity. Use symbolicated stacks and self/total weight, not only aggregate CPU percentage. Native CPU can exceed 100% relative to one core. Inspect native layout hierarchy only if layout/mounting is implicated.

## TurboModules and Fabric

Treat the book's init/method/invalidation thread observations as examples of a particular implementation, not a stable cross-version contract. Verify installed RN/module source, Codegen signatures and actual thread/queue. Native views require platform UI affinity. Synchronous JSI/native calls can block the calling thread; Promise-shaped APIs do not prove expensive work was offloaded. Initialization can differ by platform and eager/lazy settings.

For heavy native work, use existing dispatch queues/executors/coroutine dispatchers. Separate CPU-bound from I/O work. Preserve completion ordering, error propagation, cancellation, module invalidation and thread-safe access. Re-enter the JS runtime only through its supported invoker and only while it is alive; do not call JSI from arbitrary worker threads. Do not hold locks across callbacks without assessing deadlock/reentrancy.

Reduce repeated boundary crossings or excessive data copies when traces show them expensive. Consider batching at a semantic boundary. C++/Nitro/Swift/Kotlin migrations add complexity and are not automatic performance wins; benchmark the real hot path before proposing one.

## View flattening

Fabric can collapse layout-only views. JSX depth/count is not native view depth/count. Inspect the native hierarchy before removing wrappers. Check collapsable=false only at unnecessary forced host boundaries; some are required for refs/measurement, animations or native child semantics. Preserve a native component's expected children/identity and layout/accessibility. Never flip collapsable globally.

## Native SDKs and UI primitives

Compare native navigation/components with an expensive JS implementation when the interaction permits it. Preserve design, navigation state, deep links and accessibility; do not swap libraries merely because native sounds faster. Investigate Intl/polyfills against actual engine and locale requirements. Removing a polyfill based on an old Hermes support table can break formatting; use feature/locale tests on both platforms.

Validate native changes with the affected release variant and lifecycle/error scenarios; report any platform/build unavailable. An emulator can help functional diagnosis but does not stand in for physical-device user performance.
