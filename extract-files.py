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


def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None


def lib_fixup_hardware_mediatek(lib: str, *args, **kwargs):
    return f'//hardware/mediatek:{lib}'


# Frozen AIDL interface libs linked by the stock blobs. They are installed
# from common.mk instead of as prebuilt deps: Soong rejects a dependency graph
# that mixes them with the newer versions the A16 vendor libs use.
aidl_stock_interfaces = (
    'android.hardware.audio.common-V1-ndk',
    'android.hardware.bluetooth.audio-V2-ndk',
    'android.hardware.common-V2-ndk',
    'android.hardware.common.fmq-V1-ndk',
    'android.hardware.drm-V1-ndk',
    'android.hardware.gnss-V2-ndk',
    'android.hardware.graphics.allocator-V1-ndk',
    'android.hardware.graphics.common-V3-ndk',
    'android.hardware.graphics.composer3-V1-ndk',
    'android.hardware.health-V1-ndk',
    'android.hardware.light-V1-ndk',
    'android.hardware.light-V2-ndk',
    'android.hardware.memtrack-V1-ndk',
    'android.hardware.power-V3-ndk',
    'android.hardware.radio-V1-ndk',
    'android.hardware.radio.config-V1-ndk',
    'android.hardware.radio.data-V1-ndk',
    'android.hardware.radio.messaging-V1-ndk',
    'android.hardware.radio.modem-V1-ndk',
    'android.hardware.radio.network-V1-ndk',
    'android.hardware.radio.sim-V1-ndk',
    'android.hardware.radio.voice-V1-ndk',
    'android.hardware.security.secureclock-V1-ndk',
    'android.hardware.security.sharedsecret-V1-ndk',
    'android.hardware.usb-V1-ndk',
    'android.hardware.vibrator-V2-ndk',
    'android.hardware.wifi.hostapd-V1-ndk',
    'android.hardware.wifi.supplicant-V1-ndk',
    'android.media.audio.common.types-V1-cpp',
    'android.system.keystore2-V1-ndk',
)


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    aidl_stock_interfaces: lib_fixup_remove,
    (
        'libarmnn',
        'libmtkperf_client_vendor',
        'libperfctl_vendor',
        'libpowerhalwrap_vendor',
        'libvibrator',
    ): lib_fixup_vendor_suffix,
    # Use the hardware/mediatek copies
    (
        'libaedv',
        'vendor.mediatek.hardware.mtkpower@1.0',
        'vendor.mediatek.hardware.mtkpower@1.1',
        'vendor.mediatek.hardware.mtkpower@1.2',
    ): lib_fixup_hardware_mediatek,
}

# Stock copies of libs that AOSP also builds for vendor, kept as -v33
v33_libs = (
    'android.hardware.audio.common-util',
    'audioclient-types-aidl-cpp',
    'framework-permission-aidl-cpp',
    'lib_android_keymaster_keymint_utils',
    'libalsautils',
    'libaudioclient_aidl_conversion',
    'libaudiofoundation',
    'libavservices_minijail',
    'libcodec2_hidl@1.0',
    'libcodec2_hidl@1.1',
    'libcodec2_hidl@1.2',
    'libcodec2_soft_common',
    'libcodec2_vndk',
    'libcppbor_external',
    'libcppcose_rkp',
    'libdrm',
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
    # These use symbols that are gone in A16
    (
        'vendor/bin/dynamicdata',
        'vendor/bin/hw/android.hardware.usb-aidl-service.mediatekv1.0',
        'vendor/lib/hw/android.hardware.boot@1.0-impl-1.2-mtkimpl.so',
        'vendor/lib/libavservices_minijail-v33.so',
        'vendor/lib/libcodec2_hidl@1.0-v33.so',
        'vendor/lib/libcodec2_hidl@1.1-v33.so',
        'vendor/lib/libcodec2_hidl@1.2-v33.so',
        'vendor/lib/libnvram.so',
        'vendor/lib64/android.hardware.power-service-mediatek.so',
        'vendor/lib64/hw/android.hardware.boot@1.0-impl-1.2-mtkimpl.so',
        'vendor/lib64/libavservices_minijail-v33.so',
        'vendor/lib64/libcodec2_hidl@1.0-v33.so',
        'vendor/lib64/libcodec2_hidl@1.1-v33.so',
        'vendor/lib64/libcodec2_hidl@1.2-v33.so',
        'vendor/lib64/libnvram.so',
    ): blob_fixup().replace_needed('libbase.so', 'libbase-v33.so'),
    (
        'vendor/lib/libcodec2_hidl@1.0-v33.so',
        'vendor/lib/libcodec2_hidl@1.1-v33.so',
        'vendor/lib/libcodec2_hidl@1.2-v33.so',
        'vendor/lib64/libcodec2_hidl@1.0-v33.so',
        'vendor/lib64/libcodec2_hidl@1.1-v33.so',
        'vendor/lib64/libcodec2_hidl@1.2-v33.so',
    ): blob_fixup().replace_needed(
        'libstagefright_bufferqueue_helper.so',
        'libstagefright_bufferqueue_helper-v33.so',
    ),
    (
        'vendor/lib/libcodec2_vndk-v33.so',
        'vendor/lib/libstagefright_softomx-v33.so',
        'vendor/lib64/libcodec2_vndk-v33.so',
    ): blob_fixup().replace_needed('libui.so', 'libui-v33.so'),
    (
        'vendor/bin/hw/android.hardware.security.keymint@2.0-service.beanpod',
        'vendor/lib64/lib_android_keymaster_keymint_utils-v33.so',
        'vendor/lib64/libkeymint-v33.so',
    ): blob_fixup().replace_needed(
        'android.hardware.security.keymint-V2-ndk.so',
        'android.hardware.security.keymint-V2-ndk-v33.so',
    ),
    (
        'vendor/bin/hs20-osu-client',
        'vendor/bin/hw/hostapd',
        'vendor/bin/hw/wpa_supplicant',
    ): blob_fixup()
    .add_needed('libcrypto_shim.so')
    .add_needed('libshim_crypto.so'),
    'vendor/lib64/hw/hwcomposer.mtk_common.so': (
        blob_fixup().add_needed('libprocessgroup_shim.so')
    ),
    (
        'vendor/bin/atcid',
        'vendor/bin/factory',
        'vendor/bin/hw/android.hardware.audio.service.mediatek-v33',
        'vendor/bin/hw/android.hardware.bluetooth@1.1-service-mediatek',
        'vendor/bin/hw/android.hardware.media.c2@1.2-mediatek',
        'vendor/bin/hw/android.hardware.media.c2@1.2-mediatek-64b',
        'vendor/bin/hw/android.hardware.media.omx@1.0-service',
        'vendor/bin/hw/android.hardware.memtrack-service.mediatek-v33',
        'vendor/bin/hw/android.hardware.security.keymint@2.0-service.beanpod',
        'vendor/bin/hw/android.hardware.vibrator-service.mediatek-v33',
        'vendor/bin/hw/mt6835/camerahalserver',
        'vendor/bin/hw/tetheroffloadservice',
        'vendor/bin/hw/vendor.dolby.media.c2-default-service-dax',
        'vendor/bin/hw/vendor.mediatek.hardware.mms@1.7-service',
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
        'vendor/bin/wlan_assistant-v33',
        'vendor/lib/android.hardware.audio.common-util-v33.so',
        'vendor/lib/android.hardware.audio.common@6.0-util.so',
        'vendor/lib/android.hardware.audio.common@7.0-util.so',
        'vendor/lib/android.hardware.audio.common@7.1-util.so',
        'vendor/lib/android.hardware.audio.effect@6.0-util.so',
        'vendor/lib/android.hardware.audio.effect@7.0-util.so',
        'vendor/lib/android.hardware.audio@7.0-util.so',
        'vendor/lib/android.hardware.audio@7.1-util.so',
        'vendor/lib/audioclient-types-aidl-cpp-v33.so',
        'vendor/lib/egl/mt6835/libGLES_mali.so',
        'vendor/lib/framework-permission-aidl-cpp-v33.so',
        'vendor/lib/hw/android.hardware.audio.effect@6.0-impl.so',
        'vendor/lib/hw/android.hardware.audio.effect@7.0-impl.so',
        'vendor/lib/hw/android.hardware.audio@6.0-impl-mediatek.so',
        'vendor/lib/hw/android.hardware.audio@7.0-impl-mediatek.so',
        'vendor/lib/hw/android.hardware.audio@7.1-impl-mediatek.so',
        'vendor/lib/hw/audio.primary.mediatek.so',
        'vendor/lib/hw/audio.usb.default.so',
        'vendor/lib/hw/mt6835/android.hardware.graphics.allocator@4.0-impl-mediatek.so',
        'vendor/lib/hw/mt6835/android.hardware.graphics.mapper@4.0-impl-mediatek.so',
        'vendor/lib/hw/mt6835/gralloc.common.so',
        'vendor/lib/hw/mt6835/vendor.mediatek.hardware.camera.atms@1.0-impl.so',
        'vendor/lib/hw/mt6835/vendor.mediatek.hardware.camera.bgservice@1.1-impl.so',
        'vendor/lib/hw/mt6835/vendor.mediatek.hardware.pq_aidl-impl.so',
        'vendor/lib/hw/vendor.mediatek.hardware.mms@1.7-impl.so',
        'vendor/lib/hw/vendor.mediatek.hardware.nvram@1.1-impl.so',
        'vendor/lib/libalsautils-v33.so',
        'vendor/lib/libaudioclient_aidl_conversion-v33.so',
        'vendor/lib/libaudiofoundation-v33.so',
        'vendor/lib/libaudioprimarydevicehalifclient.so',
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
        'vendor/lib/libdrm-v33.so',
        'vendor/lib/libflatbuffers-cpp-v33.so',
        'vendor/lib/libhidltransport-v33.so',
        'vendor/lib/libhwbinder-v33.so',
        'vendor/lib/libion_ulit.so',
        'vendor/lib/libmediautils_vendor-v33.so',
        'vendor/lib/libmemunreachable-v33.so',
        'vendor/lib/libminiui.so',
        'vendor/lib/libopus-v33.so',
        'vendor/lib/libpcap-v33.so',
        'vendor/lib/libpkm.so',
        'vendor/lib/libruy-v33.so',
        'vendor/lib/libsfplugin_ccodec_utils-v33.so',
        'vendor/lib/libshmemcompat-v33.so',
        'vendor/lib/libshmemutil-v33.so',
        'vendor/lib/libstagefright_amrnb_common-v33.so',
        'vendor/lib/libstagefright_bufferpool@2.0.1-v33.so',
        'vendor/lib/libstagefright_enc_common-v33.so',
        'vendor/lib/libstagefright_flacdec-v33.so',
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
        'vendor/lib/libstagefright_softomx-v33.so',
        'vendor/lib/libstagefright_softomx_plugin.so',
        'vendor/lib/libtextclassifier_hash-v33.so',
        'vendor/lib/libtflite_mtk.so',
        'vendor/lib/libvorbisidec-v33.so',
        'vendor/lib/libvpx-v33.so',
        'vendor/lib/mt6835/libaalservice.so',
        'vendor/lib/mt6835/libmtkcam_debugutils.so',
        'vendor/lib/mt6835/libmtkcam_metadata.so',
        'vendor/lib/mt6835/libmtkcam_stdutils.so',
        'vendor/lib/mt6835/libmtkcam_sysutils.so',
        'vendor/lib/mt6835/libmtkcam_ulog.so',
        'vendor/lib/shared-file-region-aidl-cpp-v33.so',
        'vendor/lib64/android.hardware.audio.common-util-v33.so',
        'vendor/lib64/android.hardware.audio.common@6.0-util.so',
        'vendor/lib64/android.hardware.audio.common@7.0-util.so',
        'vendor/lib64/android.hardware.audio.common@7.1-util.so',
        'vendor/lib64/android.hardware.audio.effect@6.0-util.so',
        'vendor/lib64/android.hardware.audio.effect@7.0-util.so',
        'vendor/lib64/android.hardware.audio@7.0-util.so',
        'vendor/lib64/android.hardware.audio@7.1-util.so',
        'vendor/lib64/audioclient-types-aidl-cpp-v33.so',
        'vendor/lib64/egl/mt6835/libGLES_mali.so',
        'vendor/lib64/framework-permission-aidl-cpp-v33.so',
        'vendor/lib64/hw/android.hardware.audio.effect@6.0-impl.so',
        'vendor/lib64/hw/android.hardware.audio.effect@7.0-impl.so',
        'vendor/lib64/hw/android.hardware.audio@6.0-impl-mediatek.so',
        'vendor/lib64/hw/android.hardware.audio@7.0-impl-mediatek.so',
        'vendor/lib64/hw/android.hardware.audio@7.1-impl-mediatek.so',
        'vendor/lib64/hw/android.hardware.gnss@2.1-impl-mediatek.so',
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
        'vendor/lib64/hw/vendor.mediatek.hardware.mms@1.7-impl.so',
        'vendor/lib64/hw/vendor.mediatek.hardware.nvram@1.1-impl.so',
        'vendor/lib64/lbs_hidl_service-impl.so',
        'vendor/lib64/lib_android_keymaster_keymint_utils-v33.so',
        'vendor/lib64/libalsautils-v33.so',
        'vendor/lib64/libaudioclient_aidl_conversion-v33.so',
        'vendor/lib64/libaudiofoundation-v33.so',
        'vendor/lib64/libaudioprimarydevicehalifclient.so',
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
        'vendor/lib64/libcppbor_external-v33.so',
        'vendor/lib64/libcppcose_rkp-v33.so',
        'vendor/lib64/libdrm-v33.so',
        'vendor/lib64/libext2_blkid-v33.so',
        'vendor/lib64/libext2_com_err-v33.so',
        'vendor/lib64/libext2_e2p-v33.so',
        'vendor/lib64/libext2_misc-v33.so',
        'vendor/lib64/libext2_quota-v33.so',
        'vendor/lib64/libext2_uuid-v33.so',
        'vendor/lib64/libext2fs-v33.so',
        'vendor/lib64/libflatbuffers-cpp-v33.so',
        'vendor/lib64/libhidltransport-v33.so',
        'vendor/lib64/libhwbinder-v33.so',
        'vendor/lib64/libion_ulit.so',
        'vendor/lib64/libkeymaster_messages-v33.so',
        'vendor/lib64/libkeymaster_portable-v33.so',
        'vendor/lib64/libkeymint-v33.so',
        'vendor/lib64/libmediautils_vendor-v33.so',
        'vendor/lib64/libmemunreachable-v33.so',
        'vendor/lib64/libminiui.so',
        'vendor/lib64/libmtkutils.so',
        'vendor/lib64/libpcap-v33.so',
        'vendor/lib64/libpkm.so',
        'vendor/lib64/libpuresoftkeymasterdevice-v33.so',
        'vendor/lib64/librilfusion.so',
        'vendor/lib64/libruy-v33.so',
        'vendor/lib64/libsfplugin_ccodec_utils-v33.so',
        'vendor/lib64/libshmemcompat-v33.so',
        'vendor/lib64/libshmemutil-v33.so',
        'vendor/lib64/libsoft_attestation_cert-v33.so',
        'vendor/lib64/libsparse-v33.so',
        'vendor/lib64/libstagefright_bufferpool@2.0.1-v33.so',
        'vendor/lib64/libtextclassifier_hash-v33.so',
        'vendor/lib64/libtflite_mtk.so',
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
        'vendor/lib64/mt6835/libmtkcam_pipelinemodel_utils.so',
        'vendor/lib64/mt6835/libmtkcam_scenariorecorder.so',
        'vendor/lib64/mt6835/libmtkcam_stdutils.so',
        'vendor/lib64/mt6835/libmtkcam_sysutils.so',
        'vendor/lib64/mt6835/libmtkcam_ulog.so',
        'vendor/lib64/shared-file-region-aidl-cpp-v33.so',
    ): blob_fixup_v33(),
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
    'android.hardware.bluetooth.audio-impl',
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
    restrict_lib64_only_packages()
