# JavaScript and native memory

Guide basis: pp. 29–36, 111–125, 159–166.

## Establish domain and lifecycle

Separate Hermes heap from JVM, ARC-managed objects, C++ allocations and image/native caches. RSS/PSS growth identifies pressure, not its owning heap. Repeatedly execute the same lifecycle (open/close a screen, mount/unmount, navigate or invalidate a module). Allow normal GC/cache behavior and compare post-cycle retained objects. Navigation may keep screens mounted by design; inspect actual ownership before assuming an unmount.

A live object/allocation, a state update after unmount, or one memory spike does not alone prove a leak. Confirm an unexpected retainer path or allocations that remain after their intended lifetime. Bounded caches/warm-up often plateau; unbounded retention grows across repeated cycles.

## JavaScript

Use snapshots and allocation timelines/sampling; compare retained vs shallow size and inspect retainers. Check unremoved subscriptions, timers, closures held by global registries, pending callbacks, abandoned async tasks and unbounded caches. Match every resource to its owner/cleanup event. Cancel obsolete work where supported; ensure callbacks cannot commit stale results. Do not clear shared resources owned by another screen or service.

Fix the proven lifecycle or retaining reference and repeat the same number of cycles. Forced GC, when available, is a diagnostic control; do not use it as the production fix or compare forced-GC baseline to normal candidate runs.

## Native

- iOS: use Memory Graph for ownership, Instruments Allocations/Leaks for allocation paths, and verify deinit. Examine strong cycles/delegates/closures; choose weak captures only when their changed lifetime behavior is correct. unowned can crash if an object dies first. ARC cannot automatically break strong cycles.
- Android: examine heap dumps and retained Activities/Contexts, singleton listeners, coroutine scopes, views and lifecycle registrations. Cancel module-scoped work on invalidation. LeakCanary is a debug-only JVM diagnostic and does not inspect Hermes or C++ heaps; review possible framework false positives.
- C++/JSI: verify RAII/unique/shared ownership, reference cycles, host objects, JNI local/global references and runtime lifetime. Use native allocators/sanitizers available in the project. Never access a destroyed JS runtime from a late worker callback. Do not pair allocation/free across incompatible owners or APIs.

Prefer scoped ownership over manual freeing; audit Swift Unmanaged retained/unretained conventions if they appear. After fixing, repeat lifecycle and cancellation/error scenarios, inspect retained counts and memory plateau, and run crash/correctness checks. Lower memory alone does not demonstrate that a particular leak was fixed.
