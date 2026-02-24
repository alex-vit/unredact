---
name: android
description: Android SDK command-line tooling gotchas — emulators, apksigner, sdkmanager, AVD management, APK signing with key rotation. Use when working with Android emulators, signing APKs, creating AVDs, or using sdkmanager.
---

# Android SDK Tooling

## sdkmanager

* Standalone `cmdline-tools` installs (not nested under `$ANDROID_SDK/cmdline-tools/latest/`) cannot auto-detect the SDK root. Always pass `--sdk_root=~/Library/Android/sdk` (or the actual path) to every `sdkmanager` invocation.
* Accept licenses before downloading: `yes | sdkmanager --sdk_root=... --licenses`

## AVD creation with standalone cmdline-tools

* `avdmanager` from a standalone cmdline-tools install writes incorrect `image.sysdir.1` paths in AVD configs. It prefixes the relative path with the cmdline-tools parent directory (e.g. `Android/sdk/system-images/...` instead of `system-images/...`).
* After creating an AVD, check `~/.android/avd/<name>.avd/config.ini` and verify `image.sysdir.1` is a correct path relative to the SDK root (should start with `system-images/`). Fix it if wrong.
* Symptom of a broken path: emulator exits immediately with `FATAL | Cannot find AVD system path` or `Broken AVD system path`.

## Emulators

* Old API-level system images (API 23, 24) are arm64 only (no Google APIs variant). They work on Apple Silicon but don't include Play Store.
* When launching emulators, set `ANDROID_SDK_ROOT` if the emulator can't find system images: `ANDROID_SDK_ROOT=~/Library/Android/sdk emulator -avd <name>`.
* Useful no-UI flags: `-no-window -no-audio -no-boot-anim -gpu swiftshader_indirect`.

## APK signing with key rotation (apksigner)

* `apksigner rotate` creates a proof-of-rotation lineage file linking an old key to a new key.
* `apksigner sign` with `--next-signer --lineage` produces an APK signed with both keys:
  - v1/v2 blocks use the **old** key (backward compat for pre-v3 devices)
  - v3 or v3.1 block uses the **new** key + lineage
* `--rotation-min-sdk-version 28`: rotation goes in the v3 block, visible to Android 9+.
* `--rotation-min-sdk-version 33` (default): rotation goes in the v3.1 block, visible only to Android 13+. The v3 block carries the old key for Android 9–12.
* Sideloaded APK upgrades with rotation lineage work on **all Android versions** (tested 6–14). Pre-v3 devices (Android 6–8) see the old key in v1/v2 and allow the upgrade. Android 9+ validates the v3 lineage.
* APKs signed with only the new key (no lineage) fail sideload upgrades with `INSTALL_FAILED_UPDATE_INCOMPATIBLE`.

## Bash scripting with adb

* `adb install -r` returns non-zero on failure. In `set -e` scripts, capture output with `|| true`: `result=$(adb install -r app.apk 2>&1) || true`, then check for "Success" in the output.
* `adb uninstall <pkg>` returns non-zero if the package isn't installed. Always append `|| true` in scripts.
