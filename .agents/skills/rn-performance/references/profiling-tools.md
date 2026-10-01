# Profiling tool selection

Use this reference when choosing profilers, capture steps, or trace artifacts. Prefer tools already installed in the project or available on the user's machine. Do not install agents, upload traces, or send binaries to external services without explicit user authorization.

## Selection principles

- Start from the symptom and suspected lane, then pick the narrowest profiler that can confirm or falsify it.
- Use development tooling to localize a cause, but use release or representative profiling builds for user-facing timing, frame, startup, memory, and size claims.
- Keep the trace tied to a named scenario, device, OS, refresh rate, build mode, dataset, network/cache state, tool version, and artifact/commit.
- Prefer raw trace exports plus summarized findings. Screenshots alone are weak evidence unless they include enough labels, timestamps, and context.
- If a tool's availability or output format changed by version, inspect local docs/help or installed package exports before prescribing commands.

## Recommended tool by question

| Question | Primary tools | Capture notes | Output to keep |
| --- | --- | --- | --- |
| Which React components are expensive? | React Native DevTools React Profiler, Flipper/legacy tooling only if the project still uses it | Capture the exact interaction; inspect ranked/flame views, commit durations, and why-render details | Profiler export or screenshot with component names, commit times, and interaction |
| What blocks JS execution? | React Native DevTools CPU profiler, Hermes sampling profile where supported | Record during the affected interaction; verify source maps/symbolication before naming functions | CPU profile export, symbolicated stack, interval for the slow work |
| Is jank on JS or UI/native? | Perf Monitor for triage, Android Studio System Trace/Perfetto, Xcode Instruments Core Animation/Time Profiler | Capture frame timelines around the interaction; compare JS and UI/native threads | Trace file plus dropped-frame/frame-time summary |
| Why is Android slow? | Android Studio Profiler, Perfetto/System Trace, APK Analyzer, bundletool | Use a release/profileable build when possible; tag the scenario with markers/logs | `.perfetto-trace`/Studio trace, APK/AAB size report |
| Why is iOS slow? | Xcode Instruments Time Profiler, Hangs, Allocations, Leaks, Memory Graph, Core Animation | Use a release/profile build on device; keep dSYM/symbols available | `.trace` package or exported call tree, allocation snapshots |
| Is startup slow? | Native startup markers, app-specific interactive marker, Android logcat/am start only as native launch context, Xcode Instruments | Measure cold/warm/hot separately; align JS/native clocks before subtracting times | Marker table with timestamps, raw logs/trace |
| Is memory leaking? | Hermes heap snapshots/allocation timeline, Android heap/native allocation tools, Instruments Allocations/Leaks/Memory Graph | Repeat the lifecycle several times; compare retained objects after cleanup points | Heap snapshots, retainer paths, lifecycle count |
| Is the bundle or app too large? | Expo Atlas, source-map-explorer or equivalent source-map analyzer, Metro output, APK Analyzer, bundletool, Xcode archive/app thinning reports | Distinguish JS source, Hermes bytecode, native libraries, assets, download size, installed size | Analyzer output and artifact sizes for the exact build |

## Scenario playbooks

### React render or input lag

1. Capture React commits for the interaction.
2. Pair the expensive commit with source ownership: provider/store selector, parent component, derived data, and child boundary.
3. If the commit is cheap but input still lags, capture JS CPU and frame timing before changing React code.

### List scrolling or recycled state

1. Capture a fixed scroll path with the same dataset and device refresh rate.
2. Record frame times/dropped frames and item render cost.
3. Inspect list implementation, key stability, item measurement, image loading, state ownership, and recycling behavior.

### Animation or gesture jank

1. Capture JS and UI/native timelines during the gesture.
2. Verify whether worklet/UI-thread code is actually running off JS for the installed animation library.
3. Keep cancellation, gesture state, and accessibility/reduced-motion behavior intact when optimizing.

### Startup/TTI

1. Define the interactive endpoint first, then add or reuse native and JS markers.
2. Capture cold starts as the canonical baseline; keep warm/hot/prewarmed separate.
3. Attribute time to native startup, RN/runtime init, bytecode load/evaluation, data readiness, and first interactive screen rather than treating total launch as one bucket.

### Memory growth

1. Reproduce with repeated lifecycle cycles: navigate/open/close, background/foreground, attach/detach listeners, or run the same media flow.
2. Capture snapshots after cleanup points and compare retained paths.
3. Separate JS heap, native heap, image/cache memory, and OS-level memory pressure.

## Reporting requirements

When a profiler is used, report the tool name/version, build variant, device, scenario, trace path, capture interval, and the exact stack/commit/thread/retainer that supports the finding. If profiling is unavailable, provide the exact capture plan and label impact as unverified.
