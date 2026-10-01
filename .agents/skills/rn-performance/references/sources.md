# Provenance and chapter map

Base source: **The Ultimate Guide to React Native Optimization, 2026 edition**, Callstack, user-supplied PDF (223 pages). The source preface names Callstack's own agent-skills project. This is an independent, original workflow adaptation, not an official Callstack skill or a copy of that project. Do not imply endorsement. Do not bundle the full PDF, extracted chapters, screenshots or source code from the guide.

The reference modules paraphrase the book's mechanisms and add evidence labels, mode boundaries, repeatability rules, report structure and a measurement comparator. Those operational additions are this skill's design, not claims that the book prescribes them. A project-specific recommendation must be supported by code/traces and version-appropriate primary documentation. Book case studies are examples, never expected gains for the user's app.

## Complete performance chapter routing

Page starts below are **physical PDF pages**, starting at 1, matching the table of contents in this attachment. Some printed footer numbers in the native/bundling sections differ from physical pages. Use titles as well as page numbers to locate chapters. The cover and acknowledgements are not optimization procedures.

| Part | Chapter | Starts | Module/action |
| --- | --- | --- | --- |
| Context | Preface | 4 | Independent attribution; source-based agent workflow |
| Context | How to Read This Book | 6 | Load topic-specific modules progressively |
| Context | Why Performance Matters | 8 | Tie priorities and acceptance criteria to user/product impact |
| JavaScript | Introduction | 12 | js-performance: separate React, JS and UI work |
| JavaScript | How to Profile JS and React Code | 16 | measurement + rendering: causal CPU/commit evidence |
| JavaScript | How to Measure JS FPS | 25 | measurement: distinguish JS/UI FPS and frame times |
| JavaScript | How to Hunt JS Memory Leaks | 29 | memory: allocation/retainer/lifecycle checks |
| JavaScript | Uncontrolled Components | 37 | lists-inputs: preserve input semantics and legacy caveat |
| JavaScript | Higher-Order Specialized Components | 41 | lists-inputs: virtualization/recycling benchmark |
| JavaScript | Atomic State Management | 51 | rendering: narrow subscriptions without wholesale migration |
| JavaScript | Concurrent React | 56 | js-performance: prioritize updates, not arbitrary CPU |
| JavaScript | React Compiler | 63 | rendering: inspect coverage and adopt incrementally |
| JavaScript | High-Performance Animations Without Dropping Frames | 70 | animations: small worklets and correct runtime |
| Native | Introduction | 77 | startup-tti + native-performance: native pipeline |
| Native | Understand Platform Differences | 81 | native-performance + measurement: platform tooling/build context |
| Native | How to Profile Native Parts of React Native | 92 | native-performance: CPU/system trace/hangs |
| Native | How to Measure TTI | 102 | startup-tti: launch class and meaningful interactive endpoint |
| Native | Understanding Native Memory Management | 111 | memory: ARC/GC/RAII and cross-runtime ownership |
| Native | Understand the Threading Model of Turbo Modules and Fabric | 126 | native-performance: verify actual thread/queue implementation |
| Native | Use View Flattening | 136 | native-performance: real host hierarchy and child semantics |
| Native | Use Dedicated React Native SDKs Over Web | 140 | native-performance: native UI and locale-tested polyfills |
| Native | Make Your Native Modules Faster | 148 | native-performance: bounded async work, cancellation, crossings |
| Native | How to Hunt Memory Leaks | 159 | memory: native retainers, JVM/C++ distinctions |
| Bundling | Introduction | 168 | bundle-size + startup-tti: artifact/ABI/linking/Hermes context |
| Bundling | How to Analyze JS Bundle Size | 174 | bundle-size: production JS/HBC/source maps |
| Bundling | How to Analyze App Bundle Size | 181 | bundle-size: device download vs install size |
| Bundling | Determine True Size of Third-Party Libraries | 189 | bundle-size: JS estimates vs native shipped cost |
| Bundling | Avoid Barrel Exports | 192 | bundle-size: verify import graph and preserve side effects |
| Bundling | Experiment With Tree Shaking | 196 | bundle-size: enabled production optimizer and ESM checks |
| Bundling | Load Code Remotely When Needed | 201 | bundle-size: justify chunks, offline/compatibility behavior |
| Bundling | Shrink Code With R8 Android | 206 | bundle-size: actual release flags, keep rules and smoke checks |
| Bundling | Use Native Assets Folder | 210 | bundle-size: density variants/catalogs/app thinning |

## Version-sensitive corrections and primary references

Checked against official documentation on 2026-10-01. Recheck for the installed project versions when applying a change; do not treat this date as a future guarantee.

- **InteractionManager**: RN documentation marks it deprecated and recommends requestIdleCallback. Idle availability does not guarantee that a navigation transition finished; retain explicit ordering semantics where needed. https://reactnative.dev/docs/0.83/interactionmanager and https://reactnative.dev/docs/performance
- **Expo tree shaking**: the documented SDK 54 default is experimental import support, not automatic activation of the whole tree-shaking pipeline. The official guide separately describes production graph optimization and tree-shaking flags. Verify both configuration and final artifact. https://docs.expo.dev/guides/tree-shaking/
- **React Compiler**: prefer installed-version instructions; do not reproduce old lint plugin names, beta status, target defaults, or copy a misspelled import from the PDF. Current React docs describe incremental annotation/gating; Expo docs distinguish SDK-specific Babel/lint configuration. Inspect the actual project and compiler coverage before changing it. https://react.dev/learn/react-compiler/incremental-adoption and https://docs.expo.dev/guides/react-compiler/
- **Worklets**: scheduleOnUI/scheduleOnRN availability and runtime restrictions depend on version. Check exported APIs; do not blindly convert older Reanimated runOnUI/runOnJS patterns. https://docs.swmansion.com/react-native-worklets/docs/threading/scheduleOnUI/ and https://docs.swmansion.com/react-native-worklets/docs/threading/scheduleOnRN/
- **Architecture and engines**: the book's modern-architecture framing does not establish an arbitrary repository's RN architecture, Hermes configuration, native initialization behavior or thread identity. Resolve actual dependencies/configuration/source before applying examples.
- **Intl, shrinking, asset catalogs, list versions and remote loading**: treat book tables/commands as leads. Verify installed-version support, build templates, export paths, and primary documentation before implementing. Do not silently run @latest commands.

## Tool access limits

This skill supplies reasoning and workflows, not access to a mobile device, simulator, Xcode, Android Studio, profiler, tracing backend or app repository. Inspect available capabilities and finish the portion supported by actual access. Do not claim runtime measurements from static review. Keep source guides optional at execution: the original modules here are sufficient to route work without loading the whole book again.
