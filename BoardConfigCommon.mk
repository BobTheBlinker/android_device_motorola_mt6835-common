COMMON_PATH := device/motorola/mt6835-common

# A/B
AB_OTA_UPDATER := true

AB_OTA_PARTITIONS += \
    boot \
    dtbo \
    init_boot \
    odm_dlkm \
    product \
    system \
    system_dlkm \
    system_ext \
    vbmeta \
    vbmeta_system \
    vbmeta_vendor \
    vendor \
    vendor_boot \
    vendor_dlkm

# Architecture
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_ABI2 :=
TARGET_CPU_VARIANT := cortex-a55

TARGET_2ND_ARCH := arm
TARGET_2ND_ARCH_VARIANT := armv8-2a
TARGET_2ND_CPU_ABI := armeabi-v7a
TARGET_2ND_CPU_ABI2 := armeabi
TARGET_2ND_CPU_VARIANT := cortex-a55

# Bootloader
TARGET_NO_BOOTLOADER := true

# Boot images
BOARD_BOOT_HEADER_VERSION := 4
BOARD_INIT_BOOT_HEADER_VERSION := 4

BOARD_KERNEL_PAGESIZE := 4096

BOARD_MKBOOTIMG_ARGS += \
    --header_version $(BOARD_BOOT_HEADER_VERSION)

BOARD_MKBOOTIMG_INIT_ARGS += \
    --header_version $(BOARD_INIT_BOOT_HEADER_VERSION)

BOARD_RAMDISK_USE_LZ4 := true

BOARD_BOOTIMAGE_PARTITION_SIZE := 67108864
BOARD_INIT_BOOT_IMAGE_PARTITION_SIZE := 8388608
BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE := 67108864

# DTBO
BOARD_DTBOIMG_PARTITION_SIZE := 8388608

# Dynamic partitions
BOARD_SUPER_PARTITION_SIZE := 11811160064



BOARD_BUILD_SUPER_IMAGE_BY_DEFAULT := true

# Filesystems
TARGET_USERIMAGES_USE_EXT4 := true
TARGET_USERIMAGES_USE_F2FS := true

BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_SYSTEM_EXTIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_PRODUCTIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_VENDORIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_VENDOR_DLKMIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_ODM_DLKMIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_SYSTEM_DLKMIMAGE_FILE_SYSTEM_TYPE := erofs

BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE := f2fs
BOARD_METADATAIMAGE_FILE_SYSTEM_TYPE := f2fs
BOARD_USES_METADATA_PARTITION := true

BOARD_FLASH_BLOCK_SIZE := 262144

# Verified Boot
BOARD_AVB_ENABLE := true

# Partition output paths
TARGET_COPY_OUT_VENDOR := vendor
TARGET_COPY_OUT_PRODUCT := product
TARGET_COPY_OUT_SYSTEM_EXT := system_ext
TARGET_COPY_OUT_VENDOR_DLKM := vendor_dlkm
TARGET_COPY_OUT_ODM_DLKM := odm_dlkm
TARGET_COPY_OUT_SYSTEM_DLKM := system_dlkm

# Platform
TARGET_BOARD_PLATFORM := mt6835

# Recovery lives in vendor_boot
TARGET_NO_RECOVERY := true
BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true

# VINTF (stock fragments whose module names are taken by AOSP)
DEVICE_MANIFEST_FILE += \
    $(COMMON_PATH)/configs/vintf/android.hardware.wifi.hostapd.xml \
    $(COMMON_PATH)/configs/vintf/android.hardware.wifi.supplicant.xml \
    $(COMMON_PATH)/configs/vintf/gnss-default.xml

DEVICE_FRAMEWORK_COMPATIBILITY_MATRIX_FILE += \
    hardware/mediatek/vintf/mediatek_framework_compatibility_matrix.xml \
    $(COMMON_PATH)/configs/vintf/framework_compatibility_matrix.xml

# The stock blobs link VNDK v33 libs that come from the VNDK APEX at
# runtime and are not declared as prebuilt dependencies
BUILD_BROKEN_PREBUILT_ELF_FILES := true

# SELinux
# Mirrors device/mediatek/sepolicy_vndr SEPolicy.mk at 2f2776f, with
# libperfmgr from device/bliss instead of device/lineage
MTK_SEPOLICY_PATH := device/mediatek/sepolicy_vndr
TRUSTY_DEVICE_PATH := device/generic/trusty

include device/bliss/sepolicy/libperfmgr/sepolicy.mk

BOARD_VENDOR_SEPOLICY_DIRS += $(MTK_SEPOLICY_PATH)/base/vendor
SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS += $(MTK_SEPOLICY_PATH)/base/private
SYSTEM_EXT_PUBLIC_SEPOLICY_DIRS += $(MTK_SEPOLICY_PATH)/base/public

BOARD_VENDOR_SEPOLICY_DIRS += $(TRUSTY_DEVICE_PATH)/custom_vm/sepolicy
SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS += $(TRUSTY_DEVICE_PATH)/sepolicy/system_ext/private

ifneq ($(TARGET_BUILD_VARIANT),user)
BOARD_VENDOR_SEPOLICY_DIRS += $(MTK_SEPOLICY_PATH)/debug/vendor
SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS += $(MTK_SEPOLICY_PATH)/debug/private
SYSTEM_EXT_PUBLIC_SEPOLICY_DIRS += $(MTK_SEPOLICY_PATH)/debug/public
endif

BOARD_VENDOR_SEPOLICY_DIRS += $(COMMON_PATH)/sepolicy/vendor

# Inherit the proprietary files
include vendor/motorola/mt6835-common/BoardConfigVendor.mk
