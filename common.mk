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
    android.hardware.gatekeeper@1.0-impl \
    android.hardware.renderscript@1.0-impl \
    android.hardware.soundtrigger@2.3-impl \
    android.hardware.thermal@1.0-impl

# Frozen AIDL interface libs linked by the stock blobs (see extract-files.py)
PRODUCT_PACKAGES += \
    android.hardware.audio.common-V1-ndk.vendor \
    android.hardware.bluetooth.audio-V2-ndk.vendor \
    android.hardware.common-V2-ndk.vendor \
    android.hardware.common.fmq-V1-ndk.vendor \
    android.hardware.drm-V1-ndk.vendor \
    android.hardware.gnss-V2-ndk.vendor:64 \
    android.hardware.graphics.allocator-V1-ndk.vendor:64 \
    android.hardware.graphics.common-V3-ndk.vendor \
    android.hardware.graphics.composer3-V1-ndk.vendor:64 \
    android.hardware.health-V1-ndk.vendor:64 \
    android.hardware.light-V1-ndk.vendor:64 \
    android.hardware.light-V2-ndk.vendor:64 \
    android.hardware.memtrack-V1-ndk.vendor:64 \
    android.hardware.power-V3-ndk.vendor:64 \
    android.hardware.radio-V1-ndk.vendor:64 \
    android.hardware.radio.config-V1-ndk.vendor:64 \
    android.hardware.radio.data-V1-ndk.vendor:64 \
    android.hardware.radio.messaging-V1-ndk.vendor:64 \
    android.hardware.radio.modem-V1-ndk.vendor:64 \
    android.hardware.radio.network-V1-ndk.vendor:64 \
    android.hardware.radio.sim-V1-ndk.vendor:64 \
    android.hardware.radio.voice-V1-ndk.vendor:64 \
    android.hardware.security.keymint-V2-ndk.vendor:64 \
    android.hardware.security.secureclock-V1-ndk.vendor:64 \
    android.hardware.security.sharedsecret-V1-ndk.vendor:64 \
    android.hardware.usb-V1-ndk.vendor:64 \
    android.hardware.vibrator-V2-ndk.vendor:64 \
    android.hardware.wifi.hostapd-V1-ndk.vendor:64 \
    android.hardware.wifi.supplicant-V1-ndk.vendor:64 \
    android.media.audio.common.types-V1-cpp.vendor \
    android.system.keystore2-V1-ndk.vendor:64

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
