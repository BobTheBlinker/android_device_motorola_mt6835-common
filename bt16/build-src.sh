#!/bin/bash
#
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#
# Regenerate the -bt16 Bluetooth audio island in this directory.
#
# The AOSP sources are built on a generic product (OUT_DIR=out-bt16): in our
# product the module names resolve to the stock prebuilts in the vendor
# namespace. The local patches are applied for the build and reverted after.

MY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANDROID_ROOT="$(cd "${MY_DIR}/../../../.." && pwd)"
cd "${ANDROID_ROOT}" || exit 1

BT=packages/modules/Bluetooth
PATCH="${MY_DIR}/patches/packages_modules_Bluetooth-create_audio_patch.patch"

git -C "${BT}" apply "${PATCH}" || exit 1
trap 'git -C "${BT}" apply -R "${PATCH}"' EXIT

(
    export OUT_DIR=out-bt16
    source build/envsetup.sh >/dev/null
    lunch lineage_gsi_arm64-bp4a-userdebug >/dev/null || exit 1
    m audio.bluetooth.default android.hardware.bluetooth.audio-impl \
        libbluetooth_audio_session_aidl
) || exit 1

python3 -I "${MY_DIR}/repack-bt16.py" \
    out-bt16/target/product/generic_arm64/vendor "${ANDROID_ROOT}" "${MY_DIR}" || exit 1

echo "${BT} $(git -C "${BT}" rev-parse HEAD)"
echo "hardware/interfaces $(git -C hardware/interfaces rev-parse HEAD)"
