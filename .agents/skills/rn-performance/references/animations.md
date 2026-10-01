# Animations and gestures

Guide basis: pp. 70–75; native profiling pp. 92–101.

Determine whether jank comes from JS scheduling, UI-thread work, native layout, or GPU/compositing. Record the animation and frame/thread timeline under real workload. Reanimated can continue smooth UI animation while a JS handler is delayed; it cannot eliminate UI-thread overload.

Inspect the existing animation system first. For core Animated, use the native driver only for supported properties and behavior. For Reanimated, identify installed major version and compatible Worklets/RN/architecture/Babel setup before changing code.

Keep per-frame computation small in worklets; use shared values and supported animated props/styles. Prefer transforms/opacity when visually equivalent; layout, blur/shadows, clipping and large layers can still be expensive. Do not update React state or call back to the JS runtime on every frame without a measured need.

For Worklets versions exposing scheduleOnUI/scheduleOnRN, use their supported import paths and call signatures. Older runOnUI/runOnJS examples require version-specific treatment; do not rename blindly. Functions scheduled onto the RN runtime must belong to that runtime's scope. Capturing a large object graph into a worklet can increase transfer/memory cost.

Keep data processing off the UI thread. Clean up frame callbacks/listeners and cancel animations when their lifecycle ends. Respect reduced motion and gesture cancellation; preserve touch targets/accessibility. For navigation-triggered work, distinguish idle scheduling from actual transition completion.

Verify frames and responsiveness during gestures, interrupted transitions, rapid navigation and low-end-device stress. Test both platforms when changing shared behavior; never extrapolate Android FPS to iOS.
