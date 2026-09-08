# Core Defect Triage Matrix

Task: `TASK-20260904-002-core-defect-triage`  
Source task: `TASK-20260904-001-flutter-l1l2`  
Data label: `TEST-SYNTHETIC`

## Evidence basis and counting rules

- Analyzer source: `evidence/core-analyze-rerun.txt`; 328 diagnostics = 280 errors, 20 warnings, 28 infos.
- Test source: `evidence/core-test-rerun.txt`; final summary is `+2465 -43`.
- Eight of the 43 failing entries are explicit `Failed to load` entries. The remaining 35 are execution/assertion failures.
- Categories D and E are orthogonal overlays on the 43 test failures: their counts are matching evidence occurrences (not additional failures), so category totals intentionally do not sum to 43.

## Matrix

| Class | Count | Representative evidence (test/file line) | Root-cause direction | APK build blocked? |
|---|---:|---|---|---|
| A. Missing symbols / test-contract damage | 280 analyzer errors (dominant subset); includes unresolved test API and interface contract diagnostics | `packages/[company-]upnp_core/test/device_registry_test.dart:1:8` missing `package:test/test.dart`; `lib/core/platform_ports/app_system_port.dart:28:16` defines `canOpenExternalUrl`; `lib/core/platform_ports/local_playback_port.dart:306:16` defines `suspendForRouteHandoff`; `test/unified_music_port_test.dart:777` missing implementation | Restore test package visibility/import boundaries; reconcile fake ports and interface signatures before behavior triage | Yes for Core package validation; App APK may compile only if Core is consumed through a prebuilt artifact |
| B. Compile / load failures | 8 test files | `test/about_upgrade_dialog_test.dart:263:7` `_FakeAppSystemPort`; `test/app_update_coordinator_test.dart` load entry; `test/unified_music_port_test.dart:777` and `:767` override/signature errors | Fix the shared interface/test-double contract first, then rerun only affected files | Yes |
| C. Widget behavior assertions | 35 non-load test failures (includes platform/timing overlays) | `test/add_device_automation_semantics_test.dart:59:7` expected `add_device_ble_device_found`; `test/ai_secondary_page_header_test.dart:21:5` expected 55, actual 64 | Compare widget tree, semantics identifiers, layout constraints, and state transitions against the test contract; isolate one failure per task | Yes for release confidence; not necessarily a Dart compile blocker |
| D. Platform-channel stub / runtime adapter | 54 matching platform-stub/error log occurrences in test evidence | `test/ble_provisioning_port_test.dart:57:5` and `:121:5`; logs show OHOS `MissingPluginException` for `bleTransport`; `test/apple_music_port_test.dart:37:20` shows `PlatformException` | Make test doubles explicit per platform/channel, assert expected fallback outcomes, and keep native-only paths out of pure Flutter tests | Conditional: blocks platform APK validation and can fail tests; not a universal compile blocker |
| E. Timing / flaky suspicion | 3 timeout markers | `test/platform_auth_progress_test.dart:237:5` `pumpAndSettle timed out`; evidence also records multiroom refresh timeout and Vision provider expected-state timeout | Replace unbounded settling with condition-based waits, inspect timers/animations, and rerun repeated isolated tests before labeling flaky | Conditional; blocks reliable CI/release gate until deterministic |

## Key representative failures

### A/B contract and loading cluster

1. `packages/[company-]upnp_core/test/device_registry_test.dart:1:8` cannot resolve `package:test/test.dart`; subsequent `setUp`, `tearDown`, `group`, `test`, and matcher symbols cascade from the same dependency boundary.
2. `test/about_upgrade_dialog_test.dart:263:7` fake `AppSystemPort` does not implement `canOpenExternalUrl` declared at `lib/core/platform_ports/app_system_port.dart:28:16`.
3. `test/unified_music_port_test.dart:777` fake `LocalPlaybackPort` does not implement `suspendForRouteHandoff` declared at `lib/core/platform_ports/local_playback_port.dart:306:16`; its delayed UPnP fake also omits the `applyAsCurrentQueuePlayback` named parameter at the override site around line 767.

### C widget behavior cluster

1. `test/add_device_automation_semantics_test.dart:59:7` finds zero widgets for semantics identifier `add_device_ble_device_found` while exactly one is expected.
2. `test/ai_secondary_page_header_test.dart:21:5` receives height 64.0 where the contract expects 55.
3. Other assertion failures in the evidence include expected-value mismatches in device output selection, home music, playlist scrolling, and vision pages; each should retain its original test name and stack line when converted into a BUG ticket.

### D platform cluster

1. `test/ble_provisioning_port_test.dart:57:5` (and lines 121, 208, 243, 313) logs missing OHOS `bleTransport` plugin methods in the pure Flutter harness.
2. Apple Music channel tests at `test/apple_music_port_test.dart:37:20` and `:151:20` exercise `PlatformException` fallback behavior.
3. Video tests log `UnimplementedError: init() has not been implemented`, indicating a native video controller stub boundary rather than a Dart syntax failure.

### E timing cluster

1. `test/platform_auth_progress_test.dart:237:5` fails `pumpAndSettle` timeout while authorization progress UI is active.
2. The evidence records a multiroom candidate refresh timeout and a Vision-provider expected-state timeout; these need isolated repeat runs before assigning a flaky label.

## APK-build decision

- Core package is **not build-ready for an evidence-backed APK gate**: 328 analyzer diagnostics and 43 failing test entries remain.
- App-only Dart checks are green from task 001, but that does not clear native/plugin integration or a build that resolves Core from source.
- Do not treat platform-stub or timing overlays as harmless until the corresponding pure Flutter tests are deterministic and the target platform channel is covered by an approved adapter/stub.

## Remediation task split (dependency order)

1. **CORE-T1 — Dependency/test boundary:** restore `package:test` visibility for nested packages and document the intended package test ownership. Gate: analyzer error count from missing test symbols goes to zero.
2. **CORE-T2 — Port contract synchronization:** update test doubles and shared interface call signatures for `canOpenExternalUrl`, `suspendForRouteHandoff`, and `applyAsCurrentQueuePlayback`. Gate: all eight load/compile failures disappear without changing assertions.
3. **CORE-T3 — Platform harness adapters:** provide explicit OHOS/iOS/Android channel stubs and expected fallback fixtures for BLE, Apple Music, video, and authorization tests. Gate: no unexpected `MissingPluginException`/`UnimplementedError` remains.
4. **CORE-T4 — Widget contract fixes:** triage semantics identifier/state wiring and layout constraints (starting with the two cited failures), then process remaining assertion failures by feature area. Gate: isolated tests pass.
5. **CORE-T5 — Deterministic timing:** replace fragile settle assumptions with condition-based waits and verify timeout budgets for multiroom, authorization, and Vision flows. Gate: repeated runs produce the same result.
6. **CORE-T6 — Full Core regression:** run `flutter analyze` and `flutter test` with the task-001 Flutter/cache baseline; only then reassess APK build and device validation.

## Ticketing guidance

This matrix is the bottom layer for subsequent BUG reports. Each ticket should copy the exact test name, source line, evidence path, observed output, primary class, dependency task, and APK-blocking decision. No business-code change is implied by this read-only triage.
