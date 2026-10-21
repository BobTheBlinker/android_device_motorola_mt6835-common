#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixup_remove,
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)
from os import path
import re

namespace_imports = []


def vndk_v33_libs():
    # Provided at runtime by the com.android.vndk.v33 APEX
    configs = path.join(
        path.dirname(path.realpath(__file__)),
        '../../../prebuilts/vndk/v33/arm64/configs',
    )
    libs = set()
    for name in ('vndkcore.libraries.33.txt', 'vndksp.libraries.txt'):
        with open(path.join(configs, name)) as f:
            libs.update(line.strip().removesuffix('.so') for line in f)
    libs.discard('')
    return libs


def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'libarmnn',
        'libformatter',
        'libmtkperf_client_vendor',
        'libperfctl_vendor',
        'libpowerhalwrap_vendor',
        'libvibrator',
    ): lib_fixup_vendor_suffix,
}

lib_fixups_covered = {
    lib
    for key in lib_fixups
    for lib in (key if isinstance(key, tuple) else (key,))
}

lib_fixups.update(
    {
        lib: lib_fixup_remove
        for lib in vndk_v33_libs()
        if lib not in lib_fixups_covered
    }
)

# Stock copies of libs that AOSP also builds for vendor, kept as -v33
v33_libs = (
    'android.frameworks.cameraservice.common@2.0',
    'android.frameworks.cameraservice.device@2.0',
    'android.frameworks.cameraservice.device@2.1',
    'android.frameworks.cameraservice.service@2.0',
    'android.frameworks.cameraservice.service@2.1',
    'android.frameworks.cameraservice.service@2.2',
    'android.frameworks.sensorservice@1.0',
    'android.hardware.audio.common-util',
    'android.hardware.audio.common@5.0',
    'android.hardware.audio.common@6.0',
    'android.hardware.audio.common@6.0-util',
    'android.hardware.audio.common@7.0',
    'android.hardware.audio.common@7.0-enums',
    'android.hardware.audio.common@7.0-util',
    'android.hardware.audio.common@7.1-enums',
    'android.hardware.audio.common@7.1-util',
    'android.hardware.audio.effect@6.0',
    'android.hardware.audio.effect@6.0-util',
    'android.hardware.audio.effect@7.0',
    'android.hardware.audio.effect@7.0-util',
    'android.hardware.audio@6.0',
    'android.hardware.audio@7.0',
    'android.hardware.audio@7.0-util',
    'android.hardware.audio@7.1',
    'android.hardware.audio@7.1-util',
    'android.hardware.bluetooth.audio@2.0',
    'android.hardware.bluetooth.audio@2.1',
    'android.hardware.bluetooth@1.0',
    'android.hardware.bluetooth@1.1',
    'android.hardware.boot@1.0',
    'android.hardware.boot@1.1',
    'android.hardware.boot@1.2',
    'android.hardware.camera.common@1.0',
    'android.hardware.camera.device@1.0',
    'android.hardware.camera.device@3.2',
    'android.hardware.camera.device@3.3',
    'android.hardware.camera.device@3.4',
    'android.hardware.camera.device@3.5',
    'android.hardware.camera.device@3.6',
    'android.hardware.camera.provider@2.4',
    'android.hardware.camera.provider@2.5',
    'android.hardware.camera.provider@2.6',
    'android.hardware.gatekeeper@1.0',
    'android.hardware.gnss.measurement_corrections@1.0',
    'android.hardware.gnss.measurement_corrections@1.1',
    'android.hardware.gnss.visibility_control@1.0',
    'android.hardware.gnss@1.0',
    'android.hardware.gnss@1.1',
    'android.hardware.gnss@2.0',
    'android.hardware.gnss@2.1',
    'android.hardware.graphics.composer@2.1',
    'android.hardware.graphics.composer@2.1-resources',
    'android.hardware.graphics.composer@2.2',
    'android.hardware.graphics.composer@2.2-resources',
    'android.hardware.graphics.composer@2.3',
    'android.hardware.graphics.composer@2.4',
    'android.hardware.light-V1-ndk',
    'android.hardware.light@2.0',
    'android.hardware.media.c2@1.0',
    'android.hardware.media.c2@1.1',
    'android.hardware.media.c2@1.2',
    'android.hardware.power@1.0',
    'android.hardware.power@1.1',
    'android.hardware.power@1.2',
    'android.hardware.radio@1.0',
    'android.hardware.radio@1.1',
    'android.hardware.radio@1.2',
    'android.hardware.secure_element@1.0',
    'android.hardware.secure_element@1.1',
    'android.hardware.secure_element@1.2',
    'android.hardware.security.keymint-V1-ndk',
    'android.hardware.sensors@1.0',
    'android.hardware.sensors@2.0',
    'android.hardware.sensors@2.0-ScopedWakelock',
    'android.hardware.sensors@2.1',
    'android.hardware.soundtrigger@2.1',
    'android.hardware.soundtrigger@2.2',
    'android.hardware.soundtrigger@2.3',
    'android.hardware.tetheroffload.config@1.0',
    'android.hardware.tetheroffload.control@1.0',
    'android.hardware.tetheroffload.control@1.1',
    'android.hardware.thermal@1.0',
    'android.hardware.thermal@2.0',
    'android.hardware.usb.gadget@1.0',
    'android.hardware.usb.gadget@1.1',
    'android.hardware.wifi@1.0',
    'android.hardware.wifi@1.1',
    'android.hardware.wifi@1.2',
    'android.hardware.wifi@1.3',
    'android.hardware.wifi@1.4',
    'android.hardware.wifi@1.5',
    'android.hardware.wifi@1.6',
    'android.hidl.allocator@1.0',
    'android.media.audio.common.types-V1-cpp',
    'android.system.keystore2-V1-ndk',
    'android.system.wifi.keystore@1.0',
    'audioclient-types-aidl-cpp',
    'framework-permission-aidl-cpp',
    'lib_android_keymaster_keymint_utils',
    'libalsautils',
    'libaudioclient_aidl_conversion',
    'libaudiofoundation',
    'libavservices_minijail',
    'libbinderdebug',
    'libcodec2_hidl@1.0',
    'libcodec2_hidl@1.1',
    'libcodec2_hidl@1.2',
    'libcodec2_soft_common',
    'libcodec2_vndk',
    'libcppbor_external',
    'libcppcose_rkp',
    'libdrm',
    'libeffectsconfig',
    'libext2_blkid',
    'libext2_com_err',
    'libext2_e2p',
    'libext2_misc',
    'libext2_quota',
    'libext2_uuid',
    'libext2fs',
    'libflatbuffers-cpp',
    'libhidltransport',
    'libhwbinder',
    'libkeymaster_messages',
    'libkeymaster_portable',
    'libkeymint',
    'libladder',
    'libmediautils_vendor',
    'libmemunreachable',
    'libopus',
    'libpcap',
    'libprotobuf-cpp-full-3.9.1',
    'libprotobuf-cpp-lite-3.9.1',
    'libpuresoftkeymasterdevice',
    'libruy',
    'libsfplugin_ccodec_utils',
    'libshmemcompat',
    'libshmemutil',
    'libsoft_attestation_cert',
    'libsparse',
    'libstagefright_amrnb_common',
    'libstagefright_bufferpool@2.0.1',
    'libstagefright_enc_common',
    'libstagefright_flacdec',
    'libstagefright_softomx',
    'libtextclassifier_hash',
    'libvorbisidec',
    'libvpx',
    'shared-file-region-aidl-cpp',
    'vendor.mediatek.hardware.mtkpower@1.0',
    'vendor.mediatek.hardware.mtkpower@1.1',
    'vendor.mediatek.hardware.mtkpower@1.2',
)


def blob_fixup_v33():
    fixup = blob_fixup()
    for lib in v33_libs:
        fixup = fixup.replace_needed(f'{lib}.so', f'{lib}-v33.so')
    return fixup


# Stock binaries whose names are taken by hardware/mediatek, kept as -v33
v33_bins = (
    'bin/hw/android.hardware.audio.service.mediatek',
    'bin/hw/android.hardware.memtrack-service.mediatek',
    'bin/hw/android.hardware.vibrator-service.mediatek',
    'bin/wlan_assistant',
)


def blob_fixup_v33_rc():
    fixup = blob_fixup()
    for b in v33_bins:
        fixup = fixup.regex_replace(
            rf'(?m)(/vendor/{re.escape(b)})(?=\s|$)',
            r'\1-v33',
        )
    return fixup


blob_fixups: blob_fixups_user_type = {
    (
        'vendor/bin/atcid',
        'vendor/bin/dumpsys',
        'vendor/bin/factory',
        'vendor/bin/hw/android.hardware.bluetooth@1.1-service-mediatek',
        'vendor/bin/hw/android.hardware.boot@1.2-service',
        'vendor/bin/hw/android.hardware.drm-service.clearkey',
        'vendor/bin/hw/android.hardware.gatekeeper@1.0-service',
        'vendor/bin/hw/android.hardware.gnss-service.mediatek',
        'vendor/bin/hw/android.hardware.graphics.composer@2.1-service',
        'vendor/bin/hw/android.hardware.graphics.composer@2.3-service',
        'vendor/bin/hw/android.hardware.graphics.composer@2.4-service',
        'vendor/bin/hw/android.hardware.graphics.composer@3.1-service',
        'vendor/bin/hw/android.hardware.media.c2@1.2-mediatek',
        'vendor/bin/hw/android.hardware.media.c2@1.2-mediatek-64b',
        'vendor/bin/hw/android.hardware.media.omx@1.0-service',
        'vendor/bin/hw/android.hardware.secure_element@1.2-service-mediatek',
        'vendor/bin/hw/android.hardware.security.keymint@2.0-service.beanpod',
        'vendor/bin/hw/android.hardware.sensors-service.multihal',
        'vendor/bin/hw/android.hardware.thermal@2.0-service.mtk',
        'vendor/bin/hw/android.hardware.usb.gadget-service.mediatekv1.1',
        'vendor/bin/hw/android.hardware.wifi@1.0-service-lazy',
        'vendor/bin/hw/mt6835/camerahalserver',
        'vendor/bin/hw/tetheroffloadservice',
        'vendor/bin/hw/vendor.dolby.media.c2-default-service-dax',
        'vendor/bin/hw/vendor.mediatek.hardware.mms@1.7-service',
        'vendor/bin/hw/vendor.mediatek.hardware.mtkpower@1.0-service',
        'vendor/bin/hw/vendor.mediatek.hardware.nvram@1.1-service',
        'vendor/bin/hw/vtservice_hidl',
        'vendor/bin/lbs_hidl_service',
        'vendor/bin/make_f2fs_vendor',
        'vendor/bin/meta_tst',
        'vendor/bin/mnld',
        'vendor/bin/vendor_mke2fs',
        'vendor/bin/volte_clientapi_ua',
        'vendor/bin/volte_rcs_ua',
        'vendor/bin/volte_rcs_ua64',
        'vendor/lib/android.frameworks.cameraservice.device@2.0-v33.so',
        'vendor/lib/android.frameworks.cameraservice.device@2.1-v33.so',
        'vendor/lib/android.frameworks.cameraservice.service@2.0-v33.so',
        'vendor/lib/android.frameworks.cameraservice.service@2.1-v33.so',
        'vendor/lib/android.frameworks.cameraservice.service@2.2-v33.so',
        'vendor/lib/android.frameworks.sensorservice@1.0-v33.so',
        'vendor/lib/android.hardware.audio.common@6.0-util-v33.so',
        'vendor/lib/android.hardware.audio.common@7.0-util-v33.so',
        'vendor/lib/android.hardware.audio.common@7.1-util-v33.so',
        'vendor/lib/android.hardware.audio.effect@6.0-util-v33.so',
        'vendor/lib/android.hardware.audio.effect@6.0-v33.so',
        'vendor/lib/android.hardware.audio.effect@7.0-util-v33.so',
        'vendor/lib/android.hardware.audio.effect@7.0-v33.so',
        'vendor/lib/android.hardware.audio@6.0-v33.so',
        'vendor/lib/android.hardware.audio@7.0-util-v33.so',
        'vendor/lib/android.hardware.audio@7.0-v33.so',
        'vendor/lib/android.hardware.audio@7.1-util-v33.so',
        'vendor/lib/android.hardware.audio@7.1-v33.so',
        'vendor/lib/android.hardware.bluetooth.audio@2.0-v33.so',
        'vendor/lib/android.hardware.bluetooth.audio@2.1-v33.so',
        'vendor/lib/android.hardware.bluetooth@1.1-v33.so',
        'vendor/lib/android.hardware.boot@1.1-v33.so',
        'vendor/lib/android.hardware.boot@1.2-v33.so',
        'vendor/lib/android.hardware.media.c2@1.1-v33.so',
        'vendor/lib/android.hardware.media.c2@1.2-v33.so',
        'vendor/lib/android.hardware.radio@1.1-v33.so',
        'vendor/lib/android.hardware.sensors@2.0-ScopedWakelock-v33.so',
        'vendor/lib/android.hardware.sensors@2.0-v33.so',
        'vendor/lib/android.hardware.sensors@2.1-v33.so',
        'vendor/lib/android.hardware.soundtrigger@2.2-v33.so',
        'vendor/lib/android.hardware.soundtrigger@2.3-v33.so',
        'vendor/lib/android.hardware.thermal@2.0-v33.so',
        'vendor/lib/audioclient-types-aidl-cpp-v33.so',
        'vendor/lib/egl/mt6835/libGLES_mali.so',
        'vendor/lib/hw/android.hardware.audio.effect@6.0-impl.so',
        'vendor/lib/hw/android.hardware.audio.effect@7.0-impl.so',
        'vendor/lib/hw/android.hardware.audio@6.0-impl-mediatek.so',
        'vendor/lib/hw/android.hardware.audio@7.0-impl-mediatek.so',
        'vendor/lib/hw/android.hardware.audio@7.1-impl-mediatek.so',
        'vendor/lib/hw/android.hardware.bluetooth.audio@2.0-impl.so',
        'vendor/lib/hw/android.hardware.bluetooth.audio@2.1-impl.so',
        'vendor/lib/hw/android.hardware.bluetooth@1.1-impl-mediatek.so',
        'vendor/lib/hw/android.hardware.boot@1.0-impl-1.2-mtkimpl.so',
        'vendor/lib/hw/android.hardware.gatekeeper@1.0-impl.so',
        'vendor/lib/hw/android.hardware.soundtrigger@2.3-impl.so',
        'vendor/lib/hw/android.hardware.thermal@1.0-impl.so',
        'vendor/lib/hw/android.hardware.thermal@2.0-impl.so',
        'vendor/lib/hw/audio.bluetooth.default.so',
        'vendor/lib/hw/audio.primary.mediatek.so',
        'vendor/lib/hw/audio.usb.default.so',
        'vendor/lib/hw/mt6835/android.hardware.graphics.allocator@4.0-impl-mediatek.so',
        'vendor/lib/hw/mt6835/android.hardware.graphics.mapper@4.0-impl-mediatek.so',
        'vendor/lib/hw/mt6835/gralloc.common.so',
        'vendor/lib/hw/mt6835/vendor.mediatek.hardware.camera.atms@1.0-impl.so',
        'vendor/lib/hw/mt6835/vendor.mediatek.hardware.camera.bgservice@1.1-impl.so',
        'vendor/lib/hw/mt6835/vendor.mediatek.hardware.pq_aidl-impl.so',
        'vendor/lib/hw/sensors.dynamic_sensor_hal.so',
        'vendor/lib/hw/sound_trigger.primary.default.so',
        'vendor/lib/hw/vendor.mediatek.hardware.bluetooth.audio@2.1-impl.so',
        'vendor/lib/hw/vendor.mediatek.hardware.bluetooth.audio@2.2-impl.so',
        'vendor/lib/hw/vendor.mediatek.hardware.mms@1.7-impl.so',
        'vendor/lib/hw/vendor.mediatek.hardware.mtkpower@1.2-impl.so',
        'vendor/lib/hw/vendor.mediatek.hardware.nvram@1.1-impl.so',
        'vendor/lib/lib_power_applist.so',
        'vendor/lib/libaudioclient_aidl_conversion-v33.so',
        'vendor/lib/libaudiofoundation-v33.so',
        'vendor/lib/libaudioprimarydevicehalifclient.so',
        'vendor/lib/libbluetooth_audio_session.so',
        'vendor/lib/libbluetooth_audio_session_aidl.so',
        'vendor/lib/libcamera2ndk_vendor.so',
        'vendor/lib/libcodec2_hidl@1.0-v33.so',
        'vendor/lib/libcodec2_hidl@1.1-v33.so',
        'vendor/lib/libcodec2_hidl@1.2-v33.so',
        'vendor/lib/libcodec2_hidl_plugin.so',
        'vendor/lib/libcodec2_mtk_c2store.so',
        'vendor/lib/libcodec2_mtk_vdec.so',
        'vendor/lib/libcodec2_mtk_venc.so',
        'vendor/lib/libcodec2_soft_common-v33.so',
        'vendor/lib/libcodec2_soft_mtk_alacdec.so',
        'vendor/lib/libcodec2_soft_mtk_imaadpcmdec.so',
        'vendor/lib/libcodec2_soft_mtk_mp3dec.so',
        'vendor/lib/libcodec2_soft_mtk_msadpcmdec.so',
        'vendor/lib/libcodec2_soft_mtk_wmadec.so',
        'vendor/lib/libcodec2_vndk-v33.so',
        'vendor/lib/libcodec2_vpp_mi_plugin.so',
        'vendor/lib/libcodec2_vpp_qt_plugin.so',
        'vendor/lib/libcodec2_vpp_rs_plugin.so',
        'vendor/lib/libeffects.so',
        'vendor/lib/libion_ulit.so',
        'vendor/lib/libminiui.so',
        'vendor/lib/libmtkperf_client_vendor.so',
        'vendor/lib/libpkm.so',
        'vendor/lib/libpowerhal.so',
        'vendor/lib/libpowerhalwrap_vendor.so',
        'vendor/lib/librgbwlightsensor.so',
        'vendor/lib/libril.so',
        'vendor/lib/libsensorndkbridge.so',
        'vendor/lib/libsfplugin_ccodec_utils-v33.so',
        'vendor/lib/libshmemcompat-v33.so',
        'vendor/lib/libshmemutil-v33.so',
        'vendor/lib/libstagefright_soft_aacdec.so',
        'vendor/lib/libstagefright_soft_aacenc.so',
        'vendor/lib/libstagefright_soft_amrdec.so',
        'vendor/lib/libstagefright_soft_amrnbenc.so',
        'vendor/lib/libstagefright_soft_amrwbenc.so',
        'vendor/lib/libstagefright_soft_avcdec.so',
        'vendor/lib/libstagefright_soft_avcenc.so',
        'vendor/lib/libstagefright_soft_flacdec.so',
        'vendor/lib/libstagefright_soft_flacenc.so',
        'vendor/lib/libstagefright_soft_g711dec.so',
        'vendor/lib/libstagefright_soft_gsmdec.so',
        'vendor/lib/libstagefright_soft_hevcdec.so',
        'vendor/lib/libstagefright_soft_mp3dec.so',
        'vendor/lib/libstagefright_soft_mpeg2dec.so',
        'vendor/lib/libstagefright_soft_mpeg4dec.so',
        'vendor/lib/libstagefright_soft_mpeg4enc.so',
        'vendor/lib/libstagefright_soft_opusdec.so',
        'vendor/lib/libstagefright_soft_rawdec.so',
        'vendor/lib/libstagefright_soft_vorbisdec.so',
        'vendor/lib/libstagefright_soft_vpxdec.so',
        'vendor/lib/libstagefright_soft_vpxenc.so',
        'vendor/lib/libtflite_mtk.so',
        'vendor/lib/libwvaidl.so',
        'vendor/lib/mediacas/libclearkeycasplugin.so',
        'vendor/lib/mt6835/libaalservice.so',
        'vendor/lib/mt6835/libmtkcam_debugutils.so',
        'vendor/lib/mt6835/libmtkcam_metadata.so',
        'vendor/lib/mt6835/libmtkcam_stdutils.so',
        'vendor/lib/mt6835/libmtkcam_sysutils.so',
        'vendor/lib/mt6835/libmtkcam_ulog.so',
        'vendor/lib/vendor.mediatek.hardware.audio@6.1.so',
        'vendor/lib/vendor.mediatek.hardware.audio@7.1.so',
        'vendor/lib/vendor.mediatek.hardware.audio@8.1.so',
        'vendor/lib/vendor.mediatek.hardware.bluetooth.audio@2.1.so',
        'vendor/lib/vendor.mediatek.hardware.bluetooth.audio@2.2.so',
        'vendor/lib/vendor.mediatek.hardware.mtkpower@1.1-v33.so',
        'vendor/lib/vendor.mediatek.hardware.mtkpower@1.2-v33.so',
        'vendor/lib64/APUWareUtilsServer.so',
        'vendor/lib64/android.frameworks.cameraservice.device@2.0-v33.so',
        'vendor/lib64/android.frameworks.cameraservice.device@2.1-v33.so',
        'vendor/lib64/android.frameworks.cameraservice.service@2.0-v33.so',
        'vendor/lib64/android.frameworks.cameraservice.service@2.1-v33.so',
        'vendor/lib64/android.frameworks.cameraservice.service@2.2-v33.so',
        'vendor/lib64/android.frameworks.sensorservice@1.0-v33.so',
        'vendor/lib64/android.hardware.audio.common@6.0-util-v33.so',
        'vendor/lib64/android.hardware.audio.common@7.0-util-v33.so',
        'vendor/lib64/android.hardware.audio.common@7.1-util-v33.so',
        'vendor/lib64/android.hardware.audio.effect@6.0-util-v33.so',
        'vendor/lib64/android.hardware.audio.effect@6.0-v33.so',
        'vendor/lib64/android.hardware.audio.effect@7.0-util-v33.so',
        'vendor/lib64/android.hardware.audio.effect@7.0-v33.so',
        'vendor/lib64/android.hardware.audio@6.0-v33.so',
        'vendor/lib64/android.hardware.audio@7.0-util-v33.so',
        'vendor/lib64/android.hardware.audio@7.0-v33.so',
        'vendor/lib64/android.hardware.audio@7.1-util-v33.so',
        'vendor/lib64/android.hardware.audio@7.1-v33.so',
        'vendor/lib64/android.hardware.bluetooth.audio@2.0-v33.so',
        'vendor/lib64/android.hardware.bluetooth.audio@2.1-v33.so',
        'vendor/lib64/android.hardware.bluetooth@1.1-v33.so',
        'vendor/lib64/android.hardware.boot@1.1-v33.so',
        'vendor/lib64/android.hardware.boot@1.2-v33.so',
        'vendor/lib64/android.hardware.camera.device@1.0-v33.so',
        'vendor/lib64/android.hardware.camera.device@3.2-v33.so',
        'vendor/lib64/android.hardware.camera.device@3.3-v33.so',
        'vendor/lib64/android.hardware.camera.device@3.4-v33.so',
        'vendor/lib64/android.hardware.camera.device@3.5-v33.so',
        'vendor/lib64/android.hardware.camera.device@3.6-v33.so',
        'vendor/lib64/android.hardware.camera.provider@2.4-v33.so',
        'vendor/lib64/android.hardware.camera.provider@2.5-v33.so',
        'vendor/lib64/android.hardware.camera.provider@2.6-v33.so',
        'vendor/lib64/android.hardware.gnss.measurement_corrections@1.0-v33.so',
        'vendor/lib64/android.hardware.gnss.measurement_corrections@1.1-v33.so',
        'vendor/lib64/android.hardware.gnss@1.1-v33.so',
        'vendor/lib64/android.hardware.gnss@2.0-v33.so',
        'vendor/lib64/android.hardware.gnss@2.1-v33.so',
        'vendor/lib64/android.hardware.graphics.composer@2.1-resources-v33.so',
        'vendor/lib64/android.hardware.graphics.composer@2.2-resources-v33.so',
        'vendor/lib64/android.hardware.graphics.composer@2.2-v33.so',
        'vendor/lib64/android.hardware.graphics.composer@2.3-v33.so',
        'vendor/lib64/android.hardware.graphics.composer@2.4-v33.so',
        'vendor/lib64/android.hardware.media.c2@1.1-v33.so',
        'vendor/lib64/android.hardware.media.c2@1.2-v33.so',
        'vendor/lib64/android.hardware.power-service-mediatek.so',
        'vendor/lib64/android.hardware.power@1.1-v33.so',
        'vendor/lib64/android.hardware.power@1.2-v33.so',
        'vendor/lib64/android.hardware.radio@1.1-v33.so',
        'vendor/lib64/android.hardware.radio@1.2-v33.so',
        'vendor/lib64/android.hardware.secure_element@1.1-v33.so',
        'vendor/lib64/android.hardware.secure_element@1.2-v33.so',
        'vendor/lib64/android.hardware.sensors@2.0-ScopedWakelock-v33.so',
        'vendor/lib64/android.hardware.sensors@2.0-v33.so',
        'vendor/lib64/android.hardware.sensors@2.1-v33.so',
        'vendor/lib64/android.hardware.soundtrigger@2.2-v33.so',
        'vendor/lib64/android.hardware.soundtrigger@2.3-v33.so',
        'vendor/lib64/android.hardware.tetheroffload.control@1.1-v33.so',
        'vendor/lib64/android.hardware.thermal@2.0-v33.so',
        'vendor/lib64/android.hardware.usb.gadget@1.1-v33.so',
        'vendor/lib64/android.hardware.wifi@1.1-v33.so',
        'vendor/lib64/android.hardware.wifi@1.2-v33.so',
        'vendor/lib64/android.hardware.wifi@1.3-v33.so',
        'vendor/lib64/android.hardware.wifi@1.4-v33.so',
        'vendor/lib64/android.hardware.wifi@1.5-v33.so',
        'vendor/lib64/android.hardware.wifi@1.6-v33.so',
        'vendor/lib64/android.system.keystore2-V1-ndk-v33.so',
        'vendor/lib64/audioclient-types-aidl-cpp-v33.so',
        'vendor/lib64/egl/mt6835/libGLES_mali.so',
        'vendor/lib64/hw/android.hardware.audio.effect@6.0-impl.so',
        'vendor/lib64/hw/android.hardware.audio.effect@7.0-impl.so',
        'vendor/lib64/hw/android.hardware.audio@6.0-impl-mediatek.so',
        'vendor/lib64/hw/android.hardware.audio@7.0-impl-mediatek.so',
        'vendor/lib64/hw/android.hardware.audio@7.1-impl-mediatek.so',
        'vendor/lib64/hw/android.hardware.bluetooth.audio@2.0-impl.so',
        'vendor/lib64/hw/android.hardware.bluetooth.audio@2.1-impl.so',
        'vendor/lib64/hw/android.hardware.bluetooth@1.1-impl-mediatek.so',
        'vendor/lib64/hw/android.hardware.boot@1.0-impl-1.2-mtkimpl.so',
        'vendor/lib64/hw/android.hardware.gatekeeper@1.0-impl.so',
        'vendor/lib64/hw/android.hardware.gnss@2.1-impl-mediatek.so',
        'vendor/lib64/hw/android.hardware.sensors@2.X-subhal-mediatek.so',
        'vendor/lib64/hw/android.hardware.soundtrigger@2.3-impl.so',
        'vendor/lib64/hw/android.hardware.thermal@1.0-impl.so',
        'vendor/lib64/hw/android.hardware.thermal@2.0-impl.so',
        'vendor/lib64/hw/audio.bluetooth.default.so',
        'vendor/lib64/hw/audio.primary.mediatek.so',
        'vendor/lib64/hw/audio.usb.default.so',
        'vendor/lib64/hw/hwcomposer.mtk_common.so',
        'vendor/lib64/hw/mt6835/android.hardware.camera.provider@2.6-impl-mediatek.so',
        'vendor/lib64/hw/mt6835/android.hardware.graphics.allocator@4.0-impl-mediatek.so',
        'vendor/lib64/hw/mt6835/android.hardware.graphics.mapper@4.0-impl-mediatek.so',
        'vendor/lib64/hw/mt6835/gralloc.common.so',
        'vendor/lib64/hw/mt6835/vendor.mediatek.hardware.camera.atms@1.0-impl.so',
        'vendor/lib64/hw/mt6835/vendor.mediatek.hardware.camera.bgservice@1.1-impl.so',
        'vendor/lib64/hw/mt6835/vendor.mediatek.hardware.camera.ccap@1.0-impl.so',
        'vendor/lib64/hw/mt6835/vendor.mediatek.hardware.camera.isphal@1.0-impl.so',
        'vendor/lib64/hw/mt6835/vendor.mediatek.hardware.camera.isphal@1.1-impl.so',
        'vendor/lib64/hw/mt6835/vendor.mediatek.hardware.camera.lomoeffect@1.0-impl.so',
        'vendor/lib64/hw/mt6835/vendor.mediatek.hardware.pq_aidl-impl.so',
        'vendor/lib64/hw/sensors.dynamic_sensor_hal.so',
        'vendor/lib64/hw/sound_trigger.primary.default.so',
        'vendor/lib64/hw/vendor.mediatek.hardware.bluetooth.audio@2.1-impl.so',
        'vendor/lib64/hw/vendor.mediatek.hardware.bluetooth.audio@2.2-impl.so',
        'vendor/lib64/hw/vendor.mediatek.hardware.mms@1.7-impl.so',
        'vendor/lib64/hw/vendor.mediatek.hardware.mtkpower@1.2-impl.so',
        'vendor/lib64/hw/vendor.mediatek.hardware.nvram@1.1-impl.so',
        'vendor/lib64/lbs_hidl_service-impl.so',
        'vendor/lib64/lib_power_applist.so',
        'vendor/lib64/libaudioclient_aidl_conversion-v33.so',
        'vendor/lib64/libaudiofoundation-v33.so',
        'vendor/lib64/libaudioprimarydevicehalifclient.so',
        'vendor/lib64/libbluetooth_audio_session.so',
        'vendor/lib64/libbluetooth_audio_session_aidl.so',
        'vendor/lib64/libcamera2ndk_vendor.so',
        'vendor/lib64/libcodec2_hidl@1.0-v33.so',
        'vendor/lib64/libcodec2_hidl@1.1-v33.so',
        'vendor/lib64/libcodec2_hidl@1.2-v33.so',
        'vendor/lib64/libcodec2_hidl_plugin.so',
        'vendor/lib64/libcodec2_mtk_c2store.so',
        'vendor/lib64/libcodec2_mtk_vdec.so',
        'vendor/lib64/libcodec2_mtk_venc.so',
        'vendor/lib64/libcodec2_soft_ac4dec.so',
        'vendor/lib64/libcodec2_soft_common-v33.so',
        'vendor/lib64/libcodec2_soft_ddpdec.so',
        'vendor/lib64/libcodec2_soft_mtk_alacdec.so',
        'vendor/lib64/libcodec2_soft_mtk_imaadpcmdec.so',
        'vendor/lib64/libcodec2_soft_mtk_mp3dec.so',
        'vendor/lib64/libcodec2_soft_mtk_msadpcmdec.so',
        'vendor/lib64/libcodec2_soft_mtk_wmadec.so',
        'vendor/lib64/libcodec2_store_dolby.so',
        'vendor/lib64/libcodec2_vndk-v33.so',
        'vendor/lib64/libcodec2_vpp_AIMEMC_plugin.so',
        'vendor/lib64/libcodec2_vpp_AISR_plugin.so',
        'vendor/lib64/libcodec2_vpp_mi_plugin.so',
        'vendor/lib64/libcodec2_vpp_qt_plugin.so',
        'vendor/lib64/libcodec2_vpp_rs_plugin.so',
        'vendor/lib64/libcppcose_rkp-v33.so',
        'vendor/lib64/libeffects.so',
        'vendor/lib64/libext2_blkid-v33.so',
        'vendor/lib64/libext2_misc-v33.so',
        'vendor/lib64/libext2_quota-v33.so',
        'vendor/lib64/libext2fs-v33.so',
        'vendor/lib64/libion_ulit.so',
        'vendor/lib64/libkeymaster_portable-v33.so',
        'vendor/lib64/libkeymint-v33.so',
        'vendor/lib64/libkeystore-engine-wifi-hidl.so',
        'vendor/lib64/libkeystore-wifi-hidl.so',
        'vendor/lib64/libminiui.so',
        'vendor/lib64/libmtkperf_client_vendor.so',
        'vendor/lib64/libmtkutils.so',
        'vendor/lib64/libpkm.so',
        'vendor/lib64/libpowerhal.so',
        'vendor/lib64/libpowerhalwrap_vendor.so',
        'vendor/lib64/libpuresoftkeymasterdevice-v33.so',
        'vendor/lib64/librgbwlightsensor.so',
        'vendor/lib64/libril.so',
        'vendor/lib64/librilfusion.so',
        'vendor/lib64/libsensorndkbridge.so',
        'vendor/lib64/libsfplugin_ccodec_utils-v33.so',
        'vendor/lib64/libshmemcompat-v33.so',
        'vendor/lib64/libshmemutil-v33.so',
        'vendor/lib64/libsoft_attestation_cert-v33.so',
        'vendor/lib64/libtflite_mtk.so',
        'vendor/lib64/libwvaidl.so',
        'vendor/lib64/mediacas/libclearkeycasplugin.so',
        'vendor/lib64/mt6835/libaalservice.so',
        'vendor/lib64/mt6835/libacdk.so',
        'vendor/lib64/mt6835/libcam.afhal.so',
        'vendor/lib64/mt6835/libcam.hal3a.v3.ae.so',
        'vendor/lib64/mt6835/libcam.hal3a.v3.ai3a.so',
        'vendor/lib64/mt6835/libcam.hal3a.v3.awb.so',
        'vendor/lib64/mt6835/libcam.hal3a.v3.platform.so',
        'vendor/lib64/mt6835/libcam.hal3a.v3.resultpool.so',
        'vendor/lib64/mt6835/libcam.hal3a.v3.so',
        'vendor/lib64/mt6835/libcam.halisp.common.so',
        'vendor/lib64/mt6835/libcam.halisp.so',
        'vendor/lib64/mt6835/libcam.isptuning.so',
        'vendor/lib64/mt6835/libcam.utils.sensorprovider.so',
        'vendor/lib64/mt6835/libcameracustom.eis.so',
        'vendor/lib64/mt6835/libmtkcam.debugwrapper.so',
        'vendor/lib64/mt6835/libmtkcam.featurepipe.capture.so',
        'vendor/lib64/mt6835/libmtkcam.featurepipe.depthmap.so',
        'vendor/lib64/mt6835/libmtkcam.featurepipe.streaming.so',
        'vendor/lib64/mt6835/libmtkcam_debugutils.so',
        'vendor/lib64/mt6835/libmtkcam_device3_hal.so',
        'vendor/lib64/mt6835/libmtkcam_device3_hidl.so',
        'vendor/lib64/mt6835/libmtkcam_device3_hidlutils.so',
        'vendor/lib64/mt6835/libmtkcam_hwnode.so',
        'vendor/lib64/mt6835/libmtkcam_hwutils.so',
        'vendor/lib64/mt6835/libmtkcam_metadata.so',
        'vendor/lib64/mt6835/libmtkcam_pipelinemodel_session.so',
        'vendor/lib64/mt6835/libmtkcam_pipelinemodel_utils.so',
        'vendor/lib64/mt6835/libmtkcam_scenariorecorder.so',
        'vendor/lib64/mt6835/libmtkcam_stdutils.so',
        'vendor/lib64/mt6835/libmtkcam_sysutils.so',
        'vendor/lib64/mt6835/libmtkcam_ulog.so',
        'vendor/lib64/vendor.mediatek.hardware.audio@6.1.so',
        'vendor/lib64/vendor.mediatek.hardware.audio@7.1.so',
        'vendor/lib64/vendor.mediatek.hardware.audio@8.1.so',
        'vendor/lib64/vendor.mediatek.hardware.bluetooth.audio@2.1.so',
        'vendor/lib64/vendor.mediatek.hardware.bluetooth.audio@2.2.so',
        'vendor/lib64/vendor.mediatek.hardware.camera.frhandler@1.0.so',
        'vendor/lib64/vendor.mediatek.hardware.camera.lomoeffect@1.0.so',
        'vendor/lib64/vendor.mediatek.hardware.camera.security@1.0.so',
        'vendor/lib64/vendor.mediatek.hardware.mtkpower@1.1-v33.so',
        'vendor/lib64/vendor.mediatek.hardware.mtkpower@1.2-v33.so',
        'vendor/lib64/vendor.mediatek.hardware.power@1.1.so',
        'vendor/lib64/vendor.mediatek.hardware.power@2.0.so',
    ): blob_fixup_v33(),
    # Loads the provider with dlopen() by name (no symbols bound); the NEEDED
    # would put the bt16 provider into the v33 link group
    'vendor/bin/hw/android.hardware.audio.service.mediatek-v33': blob_fixup_v33()
        .remove_needed('android.hardware.bluetooth.audio-impl.so'),
    (
        'vendor/etc/init/android.hardware.audio.service.mediatek-v33.rc',
        'vendor/etc/init/init.wlan_drv.rc',
        'vendor/etc/init/memtrack-mediatek-v33.rc',
        'vendor/etc/init/vibrator-mtk-default.rc',
        'vendor/etc/init/wlan_assistant-v33.rc',
    ): blob_fixup_v33_rc(),
}  # fmt: skip

# Stock libs that are 64-bit only while their AOSP source also builds a
# 32-bit variant; request only the 64-bit (stock) one
lib64_only_packages = (
    'libhwc2on1adapter',
    'libhwc2onfbadapter',
    'libkeystore-engine-wifi-hidl',
    'libkeystore-wifi-hidl',
)


def restrict_lib64_only_packages():
    mk = path.join(
        path.dirname(path.realpath(__file__)),
        '../../../vendor/motorola/mt6835-common/mt6835-common-vendor.mk',
    )
    with open(mk) as f:
        s = f.read()
    for name in lib64_only_packages:
        s = re.sub(rf'(?m)^(    {re.escape(name)})( \\)?$', r'\1:64\2', s)
    with open(mk, 'w') as f:
        f.write(s)


# Stock binaries that replace a base_vendor module installed under other
# names; extract-utils only emits overrides for apps
bp_overrides = {}


def add_bp_overrides():
    bp = path.join(
        path.dirname(path.realpath(__file__)),
        '../../../vendor/motorola/mt6835-common/Android.bp',
    )
    with open(bp) as f:
        s = f.read()
    for name, overrides in bp_overrides.items():
        line = f'    name: "{name}",\n'
        assert s.count(line) == 1, name
        values = ''.join(f'        "{o}",\n' for o in overrides)
        s = s.replace(line, f'{line}    overrides: [\n{values}    ],\n')
    with open(bp, 'w') as f:
        f.write(s)


def add_stl_none():
    # Without this every prebuilt gets an implicit libc++ dependency, which
    # installs an A16 libc++ into /vendor ahead of the VNDK v33 APEX copy
    for repo in ('mt6835-common', 'sycamore_row_5G'):
        bp = path.join(
            path.dirname(path.realpath(__file__)),
            f'../../../vendor/motorola/{repo}/Android.bp',
        )
        with open(bp) as f:
            s = f.read()
        s = re.sub(
            r'(?m)^(cc_prebuilt_(?:library_shared|binary) \{\n)',
            r'\1    stl: "none",\n',
            s,
        )
        with open(bp, 'w') as f:
            f.write(s)


def postprocess_makefiles():
    restrict_lib64_only_packages()
    add_bp_overrides()
    add_stl_none()


module = ExtractUtilsModule(
    'mt6835-common',
    'motorola',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
    postprocess_makefiles()
