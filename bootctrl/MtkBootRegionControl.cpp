//
// SPDX-FileCopyrightText: 2022 The Android Open Source Project
// SPDX-FileCopyrightText: The LineageOS Project
// SPDX-License-Identifier: Apache-2.0
//

// From hardware/mediatek aidl/boot @ 8c15a9a. UFS only: /dev/block/mmcblk0 is the
// microSD slot on this platform, so there is no eMMC fallback.

#include <android-base/logging.h>
#include <errno.h>
#include <unistd.h>

#include "MtkBootRegionControl.h"
#include "ufs-bsg.h"

namespace aidl::android::hardware::boot {

MtkBootRegionControl::MtkBootRegionControl() {}

bool MtkBootRegionControl::SetActiveBootSlot(int32_t in_slot) {
    if (access(UFS_BSG0_DEV, F_OK) != 0) {
        LOG(ERROR) << UFS_BSG0_DEV << " not found (" << errno << "), not switching boot LU";
        return false;
    }
    return ufs_set_boot_part(in_slot) == 0;
}

}  // namespace aidl::android::hardware::boot
