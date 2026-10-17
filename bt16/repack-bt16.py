#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#
# Repackage the AOSP Bluetooth audio HAL (provider + session +
# audio.bluetooth module) as an island isolated from the v33 VNDK.
#
# The inputs are the vendor variants built on a generic target
# (lineage_gsi_arm64), so they are plain A16 source builds. The NEEDED
# closure of the two roots is walked; everything that is not v33 LLNDK
# is copied and renamed to <name>-bt16.so (soname and every DT_NEEDED),
# so no stock blob can bind to it and the island never binds to the
# stock v33 copies.
#
# usage: repack-bt16.py <generic vendor dir> <android root> <out dir>
# (normally run from build-src.sh)

import os
import shutil
import struct
import subprocess
import sys

from elftools.elf.dynamic import DynamicSection
from elftools.elf.elffile import ELFFile

SUFFIX = '-bt16'

# Same name as the hardware/interfaces source module, which would otherwise
# also install to vendor/lib64/android.hardware.bluetooth.audio-impl.so.
# Left out of the phony: requiring it would also pull the 32-bit source
# variant; the product lists it as <name>:64.
PREFER = ('android.hardware.bluetooth.audio-impl',)

# root file -> (installed name, soname); everything else gets SUFFIX
ROOTS = {
    # loaded by ro.hardware.audio.bluetooth=bt16
    'lib64/hw/audio.bluetooth.default.so': (
        'lib64/hw/audio.bluetooth.bt16.so', 'audio.bluetooth.bt16.so'),
    # dlopen()ed by name from the stock audio service
    'lib64/android.hardware.bluetooth.audio-impl.so': (
        'lib64/android.hardware.bluetooth.audio-impl.so',
        'android.hardware.bluetooth.audio-impl.so'),
}


# Dynamic tags holding an address of an ALLOC section. patchelf moves
# sections when .dynstr grows but does not know the Android packed/RELR
# tags, which then point at the 'Z'-filled old location.
ANDROID_TAGS = {
    0x6000000f,  # DT_ANDROID_REL
    0x60000011,  # DT_ANDROID_RELA
    0x6fffe000,  # DT_ANDROID_RELR
}
PTR_TAGS = ANDROID_TAGS | {
    3,  # DT_PLTGOT
    4,  # DT_HASH
    5,  # DT_STRTAB
    6,  # DT_SYMTAB
    7,  # DT_RELA
    12,  # DT_INIT
    13,  # DT_FINI
    17,  # DT_REL
    23,  # DT_JMPREL
    25,  # DT_INIT_ARRAY
    26,  # DT_FINI_ARRAY
    32,  # DT_PREINIT_ARRAY
    36,  # DT_RELR
    0x6ffffef5,  # DT_GNU_HASH
    0x6ffffff0,  # DT_VERSYM
    0x6ffffffc,  # DT_VERDEF
    0x6ffffffe,  # DT_VERNEED
}


def layout(path):
    """(sections {name: (addr, offset, size, type)}, dynamic [(file off, tag, val)])"""
    with open(path, 'rb') as f:
        e = ELFFile(f)
        secs = {}
        for sec in e.iter_sections():
            if sec['sh_flags'] & 2 and sec['sh_type'] != 'SHT_NOBITS':  # SHF_ALLOC
                secs[sec.name] = (sec['sh_addr'], sec['sh_offset'], sec['sh_size'])
        d = e.get_section_by_name('.dynamic')
        dyn = []
        for i in range(d['sh_size'] // 16):
            off = d['sh_offset'] + 16 * i
            f.seek(off)
            tag, val = struct.unpack('<qQ', f.read(16))
            if tag == 0:
                break
            dyn.append((off, tag, val))
    return secs, dyn


def fix_tags(orig, path):
    """Point every address tag at its section's new address, verify bytes."""
    osecs, odyn = layout(orig)
    nsecs, ndyn = layout(path)
    by_addr = {a: n for n, (a, o, sz) in osecs.items()}
    otags = {t: v for o, t, v in odyn}
    with open(orig, 'rb') as f:
        odata = f.read()
    with open(path, 'r+b') as f:
        for off, tag, val in ndyn:
            if tag not in PTR_TAGS:
                continue
            name = by_addr.get(otags.get(tag))
            if name is None or name not in nsecs:
                sys.exit(f'{path}: tag {tag:#x} has no matching section')
            addr, noff, size = nsecs[name]
            if val != addr:
                if tag not in ANDROID_TAGS:
                    sys.exit(f'{path}: tag {tag:#x} -> {val:#x}, {name} at {addr:#x}')
                f.seek(off + 8)
                f.write(struct.pack('<Q', addr))
            if tag not in ANDROID_TAGS | {7, 17, 23, 36}:
                continue  # string/symbol tables are rewritten on purpose
            oa, ooff, osize = osecs[name]
            f.seek(noff)
            if osize != size or f.read(size) != odata[ooff:ooff + osize]:
                sys.exit(f'{path}: {name} content changed')


def renamed(name):
    base, ext = os.path.splitext(name)
    return base + SUFFIX + ext


def dyn(path):
    with open(path, 'rb') as f:
        e = ELFFile(f)
        sec = next(s for s in e.iter_sections() if isinstance(s, DynamicSection))
        needed = [t.needed for t in sec.iter_tags() if t.entry.d_tag == 'DT_NEEDED']
        soname = next((t.soname for t in sec.iter_tags()
                       if t.entry.d_tag == 'DT_SONAME'), None)
    return needed, soname


def main():
    src, root, out = sys.argv[1:4]
    patchelf = os.path.join(root, 'prebuilts/extract-tools/linux-x86/bin/patchelf-0_18')
    with open(os.path.join(root, 'prebuilts/vndk/v33/arm64/configs/llndk.libraries.txt')) as f:
        llndk = {l.strip() for l in f if l.strip()}

    # NEEDED closure, lib64 only (the audio HAL service is 64-bit)
    island = {}  # src rel path -> soname
    queue = list(ROOTS)
    while queue:
        rel = queue.pop()
        if rel in island:
            continue
        needed, soname = dyn(os.path.join(src, rel))
        island[rel] = soname or os.path.basename(rel)
        for n in needed:
            if n in llndk:
                continue
            dep = 'lib64/' + n
            if not os.path.exists(os.path.join(src, dep)):
                sys.exit(f'{rel}: {n} is neither v33 LLNDK nor built')
            queue.append(dep)

    names = {}  # old soname -> new soname
    for rel, so in island.items():
        names[so] = ROOTS[rel][1] if rel in ROOTS else renamed(so)

    # only the generated files; the scripts live next to them
    shutil.rmtree(os.path.join(out, 'lib64'), ignore_errors=True)
    if os.path.exists(os.path.join(out, 'Android.bp')):
        os.remove(os.path.join(out, 'Android.bp'))
    files = []
    for rel, so in sorted(island.items()):
        dst = ROOTS[rel][0] if rel in ROOTS else 'lib64/' + names[so]
        p = os.path.join(out, dst)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        shutil.copyfile(os.path.join(src, rel), p)
        args = [patchelf, '--set-soname', names[so]]
        for n in dyn(p)[0]:
            if n in names:
                args += ['--replace-needed', n, names[n]]
        subprocess.run(args + [p], check=True)
        fix_tags(os.path.join(src, rel), p)
        files.append(dst)

    write_bp(out, files)
    for f in files:
        print(f)


def write_bp(out, files):
    lines = ['//', '// SPDX-FileCopyrightText: The LineageOS Project',
             '// SPDX-License-Identifier: Apache-2.0', '//', '',
             '// Generated by repack-bt16.py. DO NOT EDIT.', '']
    mods = []
    for f in files:
        base = os.path.splitext(os.path.basename(f))[0]
        if base in PREFER:
            name = base
        elif base.endswith(('-bt16', '.bt16')):
            name = base
        else:
            name = base + SUFFIX
        mods.append(name)
        lines += [
            'cc_prebuilt_library_shared {',
            f'    name: "{name}",',
            f'    stem: "{base}",',
        ]
        if base in PREFER:
            lines.append('    prefer: true,')
        lines += [
            '    vendor: true,',
            '    compile_multilib: "64",',
            f'    srcs: ["{f}"],',
        ]
        if '/hw/' in f:
            lines.append('    relative_install_path: "hw",')
        lines += [
            '    stl: "none",',
            '    check_elf_files: false,',
            '    strip: {',
            '        none: true,',
            '    },',
            '}',
            '',
        ]
    lines += ['phony {', '    name: "bt16_island",', '    required: [']
    lines += [f'        "{m}",' for m in sorted(mods) if m not in PREFER]
    lines += ['    ],', '}', '']
    with open(os.path.join(out, 'Android.bp'), 'w') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    main()
