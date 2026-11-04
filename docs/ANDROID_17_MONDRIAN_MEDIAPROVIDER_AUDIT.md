# P1 — MediaProvider Android 17 / mondrian APEX & storage audit

Date: 2026-11-04. **AUDIT ONLY — old source not ported, not selected, no device testing.**

## Exact historical and official sources

- PixelExperience-Reborn `packages_providers_MediaProvider` branch `seventeen`: `835ccdd03cdf07dd8d671110f7ec49f854678e90`, Android14 r21 merge (2024-01-30). The repository's branch name is not the target Android version.
- Official AOSP17 r1 `platform/packages/providers/MediaProvider`: commit `773ea53100eeb1e97c223826ca59054a58cd74ff`, tree `ff9cbc25addab66597be2bbf394a3b107b465260`. Source: https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/tags/android-17.0.0_r1
- AOSP17 source graph already includes `platform/packages/providers/MediaProvider`, `platform/packages/modules/Media` and `platform/prebuilts/module_sdk/MediaProvider`. Do not replace the provider with an Android14 fork while compiling official framework, Media Mainline SDK or Photo Picker.

## Verified module architecture

The historical `Android.bp` already declares a privileged `MediaProvider` under `com.android.mediaprovider`, `sdk_version: "module_current"`, `min_sdk_version: "30"`, media certificate and `libfuse_jni/libfuse`. It includes an older `mediaprovider-database` file list and `apex/Android.bp` packaging `MediaProvider`. A previously Mainline-capable component is **not** automatically AOSP17 compatible just because its module name remains the same.

Official AOSP17 `Android.bp` also uses `module_current`, but additionally includes (among other things):
- `mediaprovider_flags_java_lib` and `mediaprovider_flags.aconfig` declarations for AConfig;
- `photopicker/res` in resource directories and new Photo Picker / cloud integrations;
- `libleveldb_jni`, updated FUSE / embedded native library configuration;
- `framework-mediaprovider.impl`, framework module stubs and `androidx.media3.media3-transformer` APIs;
- new `legacy/src/...LegacyDatabaseUtils.java` and related database compatibility modules (historical file list refers to Android14 `src/...DatabaseUtils.java` and several non-equivalent older Java classes);
- `privapp_allowlist`, `apex_available: ["com.android.mediaprovider"]`, `updatable: true`, plus AppSearch and additional errorprone processing.

Official Soong blob: `70e4a9f3b7b3e440974ea0deadf1c77aa0079dbd`. See https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/tags/android-17.0.0_r1/Android.bp .

## Legacy PixelExperience patch

Commit `dd2cc92852a6b`, **"MediaProvider: Less spam"** (2020), replaces unconditional `Log.w(TAG, e)` with `if (LOGV) Log.w(TAG, e)` for thumbnail IOException. It only suppresses logging and is not a needed functional or security port. **Reject** copying this old code into the current thumbnail pipeline, where different error reporting may be needed. This is a confirmed historical patch, *not* a complete classification of every commit.

## Security, storage and device gates

1. Do not alter FUSE, `/storage` mount, SELinux or scoped storage permissions without full Android17/VINTF/CTS validation.
2. Preserve MediaStore and DocumentsProvider authorities, URI access and foreground/background checks; test user/work profile isolation, Photo Picker permissions, EXIF/location privacy and grants.
3. Verify old database upgrades and `legacy/src` migration for devices with existing media catalogs (including after OTA and reboot). Check that there is one installed MediaProvider APEX and matching bootclasspath fragment/signature.
4. Check products with and without GMS, OEM gallery/camera integrations and file manager access on mondrian; AOSP17 MediaStore and DownloadProvider must agree about Downloads collection handling.
5. Validate `m MediaProvider` and `com.android.mediaprovider` (target-files/APEX signing/ABI), JNI symbols and module SDK. Test `MediaProviderTests`, CTS scoped-storage, MediaProviderTranscode and PhotoPicker.
6. Confirm no regressions in image thumbnail, RAW/DNG, camera capture, HDR/video transcoding and cloud picker when relevant.

## Acceptance record

- [x] Identify old / official commits and Soong package/SDK differences.
- [x] Isolate historical noise-suppression patch and reject unneeded port.
- [x] Add source-only old-tree regression gate; no live storage changes.
- [x] Preserve the official MediaProvider source selection in staged manifest.
- [ ] Verify exact official AOSP17 source sync, source tree, APEX and Photo Picker module declarations.
- [ ] Complete all historic non-upstream patch history review.
- [ ] Build and test actual AOSP17 MediaProvider/APEX and work-profile scoped-storage CTS.
- [ ] Test OTA media-database migration, mounted volumes, file grants and playback on mondrian.

**Decision:** leave the official AOSP17 MediaProvider and Media module selected, and do not import any old Android14 fork or alter runtime storage/permissions. Host-only audit CI cannot prove APEX build, CTS, OTA or physical device behavior.
