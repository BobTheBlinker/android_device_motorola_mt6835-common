COMMON_PATH := device/motorola/mt6835-common

# Dynamic partitions.
PRODUCT_USE_DYNAMIC_PARTITIONS := true

# Virtual A/B.
PRODUCT_VIRTUAL_AB_OTA := true

# Soong namespaces.
PRODUCT_SOONG_NAMESPACES += \
    $(COMMON_PATH)

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
