# Rendering, state and React Compiler

Guide basis: pp. 16–24, 51–69.

## Establish the expensive boundary

- Record the same interaction in React Profiler. Inspect costly commits, self/total time, the ranked view, and why components rendered. Tie changes to state/context/props and subscription scope.
- Read the owning component, provider/store selector, and descendant path. Check whether the parent propagates unused changes, selectors return fresh objects, context combines unrelated updates, or expensive derivation repeats.
- Distinguish legitimate UI updates from wasted work. Many fast renders can be harmless; a single slow computation may dominate. Count actual cost, not callbacks in source.

## Prefer precise corrections

1. Keep rapidly changing state close to its consumers; split unrelated provider concerns only when needed.
2. Narrow existing Redux/Zustand/Jotai/etc. subscriptions to the fields used. Preserve selector equality and immutable updates; use the installed library's selector API.
3. Avoid duplicated filtering/sorting/normalization. Memoize expensive pure derived data with complete dependencies when input identity supports reuse.
4. Memoize a costly component boundary when unrelated parent updates cause meaningful repeated work. Stabilize callbacks/objects only when identity matters to that boundary, subscription, or effect; inline functions are not inherently defects.
5. Avoid custom deep equality until comparison cost, behavior and stale closure risk are understood. Keep updated callback semantics.

Do not migrate an app's entire state library for a render count. Compiler memoization does not replace state subscription design, network caching, virtualization, or efficient algorithms.

## Evaluate the compiler incrementally

Inspect Babel/Expo configuration, compiler version, React target and rules linting; installed does not mean enabled, and enabled does not mean this component compiles. Check diagnostics/generated output or DevTools Memo badge when available.

Resolve Rules of React violations before adoption. Use version-supported incremental scope (annotation mode/use memo, gating or documented equivalent). Preserve project presets/plugin ordering. Do not copy book snippets with stale plugin names or force a beta/latest package.

Keep existing memoization until behavior and profiles show that removing it is useful. Memoization is a performance optimization, not a correctness contract. Test identity-sensitive effects and external subscriptions during compiler rollout. Compare commits and the user-facing metric on the target device; do not promise a guide case study's gain.
