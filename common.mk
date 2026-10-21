COMMON_PATH := device/motorola/mt6835-common

# Dynamic partitions.
PRODUCT_USE_DYNAMIC_PARTITIONS := true

# Virtual A/B.
PRODUCT_VIRTUAL_AB_OTA := true

# Soong namespaces.
PRODUCT_SOONG_NAMESPACES += \
    $(COMMON_PATH) \
    $(COMMON_PATH)/bt16

# Bluetooth audio (AOSP provider + audio.bluetooth module, bt16 island)
PRODUCT_PACKAGES += \
    android.hardware.bluetooth.audio-impl:64 \
    bt16_island

PRODUCT_VENDOR_PROPERTIES += \
    ro.hardware.audio.bluetooth=bt16

# fastbootd
PRODUCT_PACKAGES += \
    fastbootd \
    android.hardware.fastboot-service.example_recovery \
    android.hardware.health-service.example_recovery

# HIDL (stock vendor is API 33 and still ships HIDL HALs)
PRODUCT_PACKAGES += \
    hwservicemanager \
    android.hidl.allocator@1.0-service \
    android.hidl.memory@1.0-impl

# Permissions (AOSP module, byte-identical to the stock file)
PRODUCT_PACKAGES += \
    android.hardware.touchscreen.multitouch.distinct.prebuilt.xml

# init_boot
PRODUCT_BUILD_INIT_BOOT_IMAGE := true

# Kernel source is kept in-tree but excluded from Soong discovery
# until source-kernel integration.
PRODUCT_SOURCE_ROOT_DIRS += \
    -kernel/motorola/mt6835

# Symlinks
PRODUCT_PACKAGES += \
    mt6835_mdota_symlink

# Inherit the proprietary files
$(call inherit-product, vendor/motorola/mt6835-common/mt6835-common-vendor.mk)
