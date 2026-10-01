# JS bundle, binary and asset size

Guide basis: pp. 168–216.

## Establish the metric

Inventory bundler/config, entrypoints, production flags, engine/bytecode, ABIs, assets, SDKs and native linking. Separate raw/minified JS, compressed JS, Hermes bytecode, APK/AAB/IPA archive, device-specific download, installed binary and runtime storage/cache. Compare the same platform/device ABI/density/locale and build settings. Universal APK/AAB archive size does not represent a device-specific Play download.

Use source-map-explorer/react-native-bundle-visualizer or Expo Atlas when supported by the project; Re.Pack stats/Rsdoctor apply to that bundler. Produce matching source maps with the actual entrypoint/config. Use Android APK Analyzer/bundletool or an existing Ruler configuration and iOS export/thinning reports for native size. Do not remove Hermes because an automated analyzer labels it large.

## Reduce included or initialized code

1. Identify largest real artifact contributors, duplicates, dead modules and unnecessary locale/polyfill/asset payloads. npm installation size, Import Cost and Bundlephobia estimates are not the shipped native cost.
2. Follow dependency edges from entrypoint to costly initialization. Narrow an import or replace a barrel only when it actually includes/initializes unused code under this bundler. Keep documented export paths; arbitrary deep imports may violate package exports or load an incompatible platform implementation.
3. Preserve import side effects, registration and initialization order. Distinguish type-only exports. Measure JS/HBC change and startup independently; byte reduction alone is not a demonstrated TTI gain.
4. Confirm actual ESM transforms and enabled production optimization. Expo ESM import support, platform shaking, general tree shaking and Metro's default behavior are separate capabilities. Do not claim tree shaking is automatically on solely from SDK version. See sources.md for the verified configuration distinction.
5. Test side effects and all impacted routes when changing module format/tree shaking. Do not set sideEffects=false broadly for code with registration, polyfills or global setup. Do not migrate Metro to Re.Pack as a default fix.

## Remote loading and code splitting

Consider only when a measured problem and product/organizational requirements justify it. Hermes memory mapping limits the value of web-style startup reasoning. Verify the production bundler actually emits/loads separate chunks; dynamic import alone is insufficient evidence. Assess offline fallback, version compatibility, caching, failure handling and current platform distribution policies using official sources if proposing remote execution. Do not add microfrontends to reduce a few bytes.

## Android R8 and resources

Inspect release minifyEnabled and shrinkResources wiring plus consumer rules. Old template variable names are not guaranteed. For generated Expo projects, use the version-supported expo-build-properties/config plugin rather than edits prebuild will overwrite.

Enable resource shrinking with compatible code shrinking when justified. Preserve reflection/JNI/serialization/SDK entry points with narrow documented rules; blanket keep rules can erase benefits. Build and smoke-test the actual minified release (login, navigation, critical SDK/native functions), preserve mapping files for crash symbolication and compare device-specific size. A debug test does not validate R8 behavior.

## Assets and native linking

Inspect density variants and oversized images/fonts/audio/video. Compress/resize to actual display needs, preserve visual quality, and use platform delivery mechanisms when applicable. Android AAB density/ABI splits and iOS asset catalogs/app thinning affect delivery; verify packaged contents. Older --asset-catalog-dest recipes require checking the installed CLI and Xcode build setup. Do not blindly edit build phases.

For multiple iOS targets/extensions, inspect duplicated static frameworks; dynamic linking can reduce duplication but change startup/link behavior. Consider only with artifact evidence and supported SDK configuration. Keep supported ABIs/locales unless the product explicitly drops them. Compare download/install sizes and runtime rendering/memory guardrails after asset changes.
