COMMON_PATH := device/motorola/mt6835-common

# Dynamic partitions.
PRODUCT_USE_DYNAMIC_PARTITIONS := true

# Virtual A/B.
PRODUCT_VIRTUAL_AB_OTA := true

# Soong namespaces.
PRODUCT_SOONG_NAMESPACES += \
    $(COMMON_PATH) \
    hardware/mediatek

# fastbootd
PRODUCT_PACKAGES += \
    fastbootd \
    android.hardware.fastboot-service.example_recovery \
    android.hardware.health-service.example_recovery

# Boot control (recovery and fastbootd only; normal boot keeps the stock HAL)
PRODUCT_PACKAGES += \
    android.hardware.boot-service.mediatek_recovery

# HIDL (stock vendor is API 33 and still ships HIDL HALs)
PRODUCT_PACKAGES += \
    hwservicemanager \
    android.hidl.allocator@1.0-service \
    android.hidl.memory@1.0-impl

# init_boot
PRODUCT_BUILD_INIT_BOOT_IMAGE := true

# Kernel source is kept in-tree but excluded from Soong discovery
# until source-kernel integration.
PRODUCT_SOURCE_ROOT_DIRS += \
    -kernel/motorola/mt6835

# AOSP HALs built from source (replacing the stock copies)
PRODUCT_PACKAGES += \
    android.hardware.drm-service.clearkey \
    android.hardware.gatekeeper@1.0-service \
    android.hardware.health-service.example \
    android.hardware.sensors-service.multihal

# AOSP passthrough HAL implementations (loaded by the stock HAL services)
PRODUCT_PACKAGES += \
    android.hardware.audio.effect@6.0-impl \
    android.hardware.audio.effect@7.0-impl \
    android.hardware.bluetooth.audio@2.0-impl \
    android.hardware.bluetooth.audio@2.1-impl \
    android.hardware.gatekeeper@1.0-impl \
    android.hardware.renderscript@1.0-impl \
    android.hardware.soundtrigger@2.3-impl \
    android.hardware.thermal@1.0-impl

# vndbinder (stock vendor still uses /dev/vndbinder)
PRODUCT_PACKAGES += \
    vndservicemanager

# Vendor tools
PRODUCT_PACKAGES += \
    awk_vendor \
    chipinfo \
    dumpsys_vendor \
    vndservice

# Symlinks
PRODUCT_PACKAGES += \
    mdota_symlink

# Inherit the proprietary files
$(call inherit-product, vendor/motorola/mt6835-common/mt6835-common-vendor.mk)
