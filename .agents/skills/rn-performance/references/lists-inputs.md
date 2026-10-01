# Specialized lists and responsive inputs

Guide basis: pp. 37–50.

## Large lists

Confirm data volume and item cost. A short static ScrollView is valid; thousands of eagerly mounted items justify a virtualization investigation. Profile mount/scroll, JS and UI frame times, blank cells and memory with realistic production data.

Prefer the project's virtualized list first (FlatList/SectionList or existing FlashList/LegendList). Check stable data IDs, keyExtractor, item state identity, expensive renderItem work, image dimensions/decoding, nested same-axis scrolling, unnecessary subscriptions and data array churn.

Tune window/batch/initial-render sizes with measurements: too little produces gaps, too much raises CPU/memory. Use getItemLayout only when offsets/heights are actually known, including separators/headers. Do not invent a fixed height for dynamic text/accessibility layouts. removeClippedSubviews is platform-dependent and can cause missing content; test before enabling.

For recycling lists, read the installed major version's APIs rather than assuming older props such as estimatedItemSize apply. Recycled views may receive another item: reset or correctly associate local state, images, effects, refs and callbacks. Enabling recycling is a semantic change for item-owned state.

Migrate libraries only after a benchmark justifies it and required interactions/layouts are supported. Smoke-check scroll-to-index, pagination, pull-to-refresh, keyboard, selection, accessibility and changed item identities; capture native memory and frame tails as guardrails.

## TextInput

Reproduce rapid typing/paste/IME/autocomplete while realistic JS work runs. Trace whether expensive parents/list filtering, formatting or controlled synchronization causes latency. Fix unrelated work and isolate input state before converting it to uncontrolled.

The book's synchronization example explicitly concerns legacy asynchronous architecture; do not assume that exact defect exists in a modern app. Uncontrolled inputs can help some flows but alter source-of-truth behavior. Preserve initial value, programmatic reset, validation, masks, selection/cursor, autofill, submission and external updates. Read latest text correctly when submitting. Avoid debounce on the controlled value; debounce expensive downstream work if appropriate. Use an existing form library's field subscriptions before replacing the form architecture.
