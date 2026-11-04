#!/usr/bin/env python3
"""Source-only check for the archived PE MediaProvider tree. NOT an A17 port."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
A = "{http://schemas.android.com/apk/res/android}"


def verify(ok, label):
    if not ok:
        raise AssertionError(label)
    print("PASS INVENTORY:", label)


def read(path):
    p = ROOT / path
    verify(p.is_file(), "historical file: " + path)
    return p.read_text(encoding="utf-8")


def main():
    bp = read("Android.bp")
    apex = read("apex/Android.bp")
    source = read("src/com/android/providers/media/MediaProvider.java")
    manifest = ET.parse(ROOT / "AndroidManifest.xml").getroot()
    verify('name: "MediaProvider"' in bp and 'certificate: "media"' in bp
           and 'privileged: true' in bp, "old media-signed privileged app")
    verify('sdk_version: "module_current"' in bp, "old Mainline module SDK marker")
    verify('name: "com.android.mediaprovider"' in apex
           and 'apps: ["MediaProvider"]' in apex, "old MediaProvider APEX exists")
    verify('"libfuse_jni"' in bp and '"libfuse"' in bp, "old FUSE JNI stack")
    verify('"libleveldb_jni"' not in bp, "old Soong lacks newer LevelDB JNI entry")
    verify('"mediaprovider_flags_java_lib"' not in bp, "old Soong lacks AOSP17 AConfig library")
    verify('if (LOGV) Log.w(TAG, e);' in source,
           "old thumbnail-IOException log suppression present (NOT TO PORT)")
    verify(manifest.get("package") == "com.android.providers.media.module",
           "old MediaProvider module package")
    auths = {p.get(A + "authorities") for p in manifest.findall("./application/provider")}
    verify({"media", "com.android.providers.media.documents"}.issubset(auths),
           "old MediaStore/DocumentsProvider authority identities")
    verify((ROOT / "TEST_MAPPING").is_file(), "legacy media CTS test mapping exists")
    print("PASS: old source inspection only; AOSP17 APEX/CTS/database/device NOT TESTED.")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ET.ParseError) as exc:
        print("FAIL:", exc, file=sys.stderr)
        sys.exit(1)
