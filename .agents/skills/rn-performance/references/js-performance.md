# JavaScript work and concurrent rendering

Guide basis: pp. 12–28, 56–62, 70–75.

## Locate long work

Profile JS CPU during the affected flow. Inspect top-down and bottom-up/self time with matching symbols. Identify synchronous filtering/sorting, serialization, large JSON parsing, repeated date formatting, effect loops, logging or synchronous native calls. Locate work relative to input and visual response. Classify network waiting separately from CPU execution.

Change the algorithm or volume first: pagination, indexed lookup, one-pass derivation, precomputation, bounded caches, eliminating duplicated transforms. Preserve data order and correctness.

For deferrable tasks, consider cooperative chunks with cancellation and a real yield to the event loop. Scheduling one large function later can still cause the same hang. A Promise, async declaration or await does not put synchronous JavaScript on another thread. A chain of microtasks can also starve the event loop.

## Use concurrency for update priority

- Keep TextInput value/urgent feedback urgent. useDeferredValue can feed an expensive results subtree; show stale/pending UI as appropriate.
- Use a supported transition for nonurgent React updates. startTransition invokes its callback immediately: a large synchronous filter inside that callback still blocks JS. A deferred value does not debounce requests or guarantee a fixed delay.
- Verify actual React/RN architecture and renderer support. Automatic batching reduces commits but does not remove expensive execution.
- Cancel obsolete work and avoid late state updates/races on navigation or rapidly changing queries.

## Choose scheduling by semantics

InteractionManager appears in the guide, but current RN docs deprecate it in favor of requestIdleCallback. Check the installed version. Idle time is not equivalent to navigation transition completion; when that ordering matters, use the navigator's supported completion event and cleanup. Respect deadline/timeRemaining and bound each chunk; add starvation handling only when required. Verify requestIdleCallback/cancelIdleCallback availability rather than assuming a browser environment.

For sustained expensive computation, consider an existing background runtime or an asynchronous native implementation only if traces justify the complexity. Do not move CPU-heavy processing to the UI runtime, where it competes with gestures and rendering. Verify functional behavior and compare input latency/long JS tasks before and after.
