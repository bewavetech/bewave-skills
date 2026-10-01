# Startup and time to interactive

Guide basis: pp. 77–80, 102–110, 168–180.

Define the endpoint as meaningful content that accepts the intended user interaction. A splash disappearing, contentAppeared, initial useEffect, or first React mount can be an intermediate marker; none automatically proves interactivity.

Collect a monotonic/native-aligned start and markers for process/app setup, React Native/runtime initialization, bytecode load/evaluation, first content, data readiness and screenInteractive. Prefer existing instrumentation. Marker names/APIs differ by RN and react-native-performance versions; inspect actual support. JS and native clocks require a shared origin/explicit alignment; do not subtract unrelated wall clocks.

Classify cold/warm/hot/prewarmed and foreground/background launches. Filter or analyze them separately. iOS prewarming may shift pre-main timing; Android adb startup durations and first-frame reports are native launch metrics, not automatically TTI. Document missing marker coverage.

Follow the slow segment rather than only the largest bundle:

- Defer nonessential analytics/SDK initialization and imports only when timing/side effects allow it.
- Preserve auth, deep link, migrations, security checks, notifications and offline readiness ordering.
- Avoid unnecessary startup JS execution and native module touches that trigger lazy initialization early.
- Separate network time from parsing/normalization and rendering; use existing cache/data strategy where appropriate.
- Render useful initial content and defer secondary UI without prematurely declaring interactive status.

Hermes release builds typically ship precompiled bytecode and benefit from memory mapping, so web-style download/parse assumptions are insufficient. Reducing bytecode size or using lazy imports can help some paths, but actual executed initialization is the causal target. Measure TTI rather than infer it from bytes. inlineRequires/dynamic import do not guarantee remote production chunks.

For Expo, profile a representative standalone/release or development-client build as appropriate; Expo Go includes different runtime/native contents. Preserve generated native settings through app config/plugins. Compare the same start class/device/data state and test cold launch, logged-in/logged-out, deep link, offline and background resume after startup changes.
