# Measurement protocol

Guide basis: JS/React profiling pp. 16–24; FPS pp. 25–28; native profiling pp. 92–101; TTI pp. 102–110. Use PDF page numbering from sources.md.

## Build a repeatable experiment

1. Define one real flow: cold launch to searchable home, typing a fixed query with a fixed dataset, scrolling the same long list, opening/closing a detail screen, or dragging the same gesture.
2. Record device model, OS, refresh rate, engine, architecture, build variant, artifact/commit, dataset fixture, auth state, network/cache policy, tool/version, and instrumentation. Maintain thermal/battery conditions as closely as practical and document variability.
3. Choose primary and guardrail metrics. JS FPS and UI FPS diagnose different lanes; frame-time distributions/dropped frames and input latency usually explain jank better than average FPS alone. Render counts are explanatory metrics, not the user outcome.
4. Separate cold, warm, hot and iOS prewarmed launches. Compare matching launch types; use cold starts as the canonical startup baseline and report other classes separately when useful.
5. Use a declared repetition count and reset procedure. As a starting operational rule, obtain at least 10 repeated runtime runs; 20 or more improves tail descriptions. These counts are this skill's protocol, not a book guarantee or proof of significance. For expensive runs, keep fewer samples and label low confidence.
6. Keep raw samples. Report n, median, p95 method, spread, context, and failures. Nearest-rank p95 with a small sample is often its maximum. Single size measurements can suffice for a deterministic artifact; do not treat one timing as reliable.
7. Re-run the candidate and, if noise is substantial, interleave baseline/candidate runs or repeat the baseline. Set acceptance based on product needs and variability, not a universal percentage.

## Select tools by question

| Question | Tool/evidence | Limitation |
| --- | --- | --- |
| Which components cost time? | RN DevTools React Profiler, ranked/flame graph, why-render data | Development/Strict Mode overhead; renders do not equal native repaint |
| What blocks JS? | RN DevTools CPU profiling, version-supported Hermes profiling | Verify symbol/source-map compatibility; tool availability varies |
| Is it JS or UI jank? | Perf Monitor for triage; native frame/system trace for confirmation | Overlay is a quick signal, not release benchmark evidence |
| Android scenario comparison | Existing Flashlight flow, native trace or project benchmark | Do not infer iOS results from Android; inspect tool availability |
| Native CPU/hang | Instruments Time Profiler/Hangs; Android Studio CPU/System Trace/Perfetto | Associate stacks with the actual interaction |
| Retained memory | Hermes snapshots/allocation timeline; Instruments Allocations/Leaks/Memory Graph; Android heap/native allocations | Different heaps and domains require different tools |
| Startup | Native start markers plus app-specific interaction-ready marker | First mount/contentAppeared does not establish interactivity |
| Artifact sizes | JS source map analyzer/Expo Atlas; APK Analyzer/bundletool; exported iOS thinning report | JS bytes, HBC, download and installed size are distinct |

Never silently install profiling agents or upload proprietary binaries/traces to external services; use existing local tools and user-authorized destinations. Choose actual project scripts rather than assuming any CLI name exists.

## Budget interpretation

At 60 Hz a frame interval is about 16.67 ms; at 120 Hz about 8.33 ms. This is a total frame budget, not a promise that each individual function may consume that much. CPU, layout, GPU, and scheduling work share deadlines; JS and UI operate separately. Diagnose the actual refresh rate and frame distribution. Transitions or idle scheduling can improve responsiveness without reducing total work.

## JSON comparison schema

Use assets/metrics-example.json as a schema example; its empty sample arrays are deliberately invalid until populated with real measurements. Put run metadata in run; put every controlled variable affecting comparability in context. Required context: platform, device, os, build_mode, scenario, engine, architecture, refresh_hz, dataset, network, cache, start_type, instrumentation. Use explicit "not-applicable" when appropriate, never omit a required key.

Use the same metric names, unit and direction in each file. Each metric requires nonempty, finite, nonnegative numeric samples; direction is lower or higher. Use separate files for different platforms/scenarios/start types. Store source artifact paths/tool versions in run and context as appropriate. Do not use the comparator output as a universal pass/fail gate.
