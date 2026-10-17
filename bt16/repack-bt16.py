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
# is copied and renamed b16<name[3:]> (libbase.so -> b16base.so), so no
# stock blob can bind to it and the island never binds to the stock v33
# copies.
#
# The renames are done in place in .dynstr (DT_SONAME and DT_NEEDED
# strings, never longer than the original), so every byte outside .dynstr
# stays as the linker wrote it.
#
# usage: repack-bt16.py <generic vendor dir> <android root> <out dir>
# (normally run from build-src.sh)

import os
import shutil
import struct
import sys

from elftools.elf.dynamic import DynamicSection
from elftools.elf.elffile import ELFFile

PREFIX = 'b16'

# Same name as the hardware/interfaces source module, which would otherwise
# also install to vendor/lib64/android.hardware.bluetooth.audio-impl.so.
# Left out of the phony: requiring it would also pull the 32-bit source
# variant; the product lists it as <name>:64.
PREFER = ('android.hardware.bluetooth.audio-impl',)

# root file -> (installed name, soname); everything else gets PREFIX
ROOTS = {
    # loaded by ro.hardware.audio.bluetooth=bt16
    'lib64/hw/audio.bluetooth.default.so': (
        'lib64/hw/audio.bluetooth.bt16.so', 'audio.bluetooth.bt16.so'),
    # dlopen()ed by name from the stock audio service
    'lib64/android.hardware.bluetooth.audio-impl.so': (
        'lib64/android.hardware.bluetooth.audio-impl.so',
        'android.hardware.bluetooth.audio-impl.so'),
}

DT_NEEDED, DT_SONAME, DT_RPATH, DT_RUNPATH = 1, 14, 15, 29
SHT_GNU_VERDEF, SHT_GNU_VERNEED = 0x6ffffffd, 0x6ffffffe


def renamed(name):
    return PREFIX + name[len(PREFIX):]


def dyn(path):
    with open(path, 'rb') as f:
        e = ELFFile(f)
        sec = next(s for s in e.iter_sections() if isinstance(s, DynamicSection))
        needed = [t.needed for t in sec.iter_tags() if t.entry.d_tag == 'DT_NEEDED']
        soname = next((t.soname for t in sec.iter_tags()
                       if t.entry.d_tag == 'DT_SONAME'), None)
    return needed, soname


def dynstr_refs(data):
    """(.dynstr (offset, size), {strtab offset: kinds}) for one ELF64 LE."""
    with open_bytes(data) as e:
        shdr = {}
        for i, sec in enumerate(e.iter_sections()):
            raw_type = struct.unpack_from(
                '<I', data, e['e_shoff'] + i * e['e_shentsize'] + 4)[0]
            shdr[sec.name] = (sec, raw_type)
        dynstr = shdr['.dynstr'][0]
        refs = {}

        def add(off, kind):
            refs.setdefault(off, set()).add(kind)

        for sym in shdr['.dynsym'][0].iter_symbols():
            add(sym['st_name'], 'sym')
        d = shdr['.dynamic'][0]
        for i in range(d['sh_size'] // 16):
            tag, val = struct.unpack_from('<qQ', data, d['sh_offset'] + 16 * i)
            if tag == 0:
                break
            if tag in (DT_NEEDED, DT_SONAME):
                add(val, 'lib')
            elif tag in (DT_RPATH, DT_RUNPATH):
                add(val, 'path')
        for sec, raw_type in shdr.values():
            o = sec['sh_offset']
            if raw_type == SHT_GNU_VERNEED:
                for _ in range(sec['sh_info']):
                    _, cnt, vfile, aux, nxt = struct.unpack_from('<HHIII', data, o)
                    add(vfile, 'lib')
                    a = o + aux
                    for _ in range(cnt):
                        _, _, _, name, anext = struct.unpack_from('<IHHII', data, a)
                        add(name, 'ver')
                        a += anext
                    o += nxt
            elif raw_type == SHT_GNU_VERDEF:
                for _ in range(sec['sh_info']):
                    _, flags, _, cnt, _, aux, nxt = struct.unpack_from('<HHHHIII', data, o)
                    a = o + aux
                    for k in range(cnt):
                        name, anext = struct.unpack_from('<II', data, a)
                        # the VER_FLG_BASE entry names the file itself
                        # (= DT_SONAME); nothing requires it by name
                        add(name, 'lib' if flags & 1 and k == 0 else 'ver')
                        a += anext
                    o += nxt
        return (dynstr['sh_offset'], dynstr['sh_size']), refs


class open_bytes:
    def __init__(self, data):
        import io
        self.f = io.BytesIO(data)

    def __enter__(self):
        return ELFFile(self.f)

    def __exit__(self, *a):
        self.f.close()


def rename_in_place(src, dst, names):
    """Rewrite the DT_SONAME/DT_NEEDED strings listed in names inside
    .dynstr; fail if any other reference points into a rewritten string."""
    with open(src, 'rb') as f:
        data = bytearray(f.read())
    (str_off, str_size), refs = dynstr_refs(bytes(data))
    starts = sorted(refs)
    done = set()
    for o in starts:
        if 'lib' not in refs[o]:
            continue
        end = data.index(b'\0', str_off + o) - str_off
        old = data[str_off + o:str_off + end].decode()
        if old not in names or names[old] == old:
            continue
        new = names[old].encode()
        if len(new) > len(old):
            sys.exit(f'{src}: {names[old]} is longer than {old}')
        if refs[o] != {'lib'}:
            sys.exit(f'{src}: {old} is also used as {refs[o] - {"lib"}}')
        inside = [r for r in starts if o < r <= end]
        if inside:
            sys.exit(f'{src}: {old} shares bytes with strings at {inside}')
        data[str_off + o:str_off + end] = new + b'\0' * (len(old) - len(new))
        done.add(old)
    with open(dst, 'wb') as f:
        f.write(data)

    # every byte outside .dynstr is unchanged
    with open(src, 'rb') as f:
        orig = f.read()
    diff = [i for i in range(len(orig)) if orig[i] != data[i]]
    if len(orig) != len(data) or (diff and (diff[0] < str_off or
                                            diff[-1] >= str_off + str_size)):
        sys.exit(f'{dst}: changed outside .dynstr')
    return done


def main():
    src, root, out = sys.argv[1:4]
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
        # an already repackaged lib means the generic build picked up our
        # prebuilts instead of the sources
        if any(n.startswith(PREFIX) or '-bt16' in n for n in needed):
            sys.exit(f'{rel}: input is already repackaged: {needed}')
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
    if len(set(names.values())) != len(names):
        sys.exit('rename collision')
    taken = {n for n in os.listdir(os.path.join(src, 'lib64')) if n.startswith(PREFIX)}
    if taken:
        sys.exit(f'{PREFIX} prefix already in use: {sorted(taken)}')

    # only the generated files; the scripts live next to them
    shutil.rmtree(os.path.join(out, 'lib64'), ignore_errors=True)
    if os.path.exists(os.path.join(out, 'Android.bp')):
        os.remove(os.path.join(out, 'Android.bp'))
    files = []
    for rel, so in sorted(island.items()):
        dst = ROOTS[rel][0] if rel in ROOTS else 'lib64/' + names[so]
        p = os.path.join(out, dst)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        rename_in_place(os.path.join(src, rel), p, names)
        needed, soname = dyn(p)
        want = [names.get(n, n) for n in dyn(os.path.join(src, rel))[0]]
        if needed != want or soname != names[so]:
            sys.exit(f'{p}: rename incomplete: {soname} {needed}')
        os.chmod(p, 0o644)
        files.append(dst)

    write_bp(out, files)
    for f in files:
        print(f)


def write_bp(out, files):
    lines = ['//', '// SPDX-FileCopyrightText: The LineageOS Project',
             '// SPDX-License-Identifier: Apache-2.0', '//', '',
             '// Generated by repack-bt16.py. DO NOT EDIT.', '',
             '// Own namespace: only our product imports it, so the generic',
             '// build-src.sh product never swaps the source provider for it.',
             'soong_namespace {', '}', '']
    mods = []
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        mods.append(name)
        lines += [
            'cc_prebuilt_library_shared {',
            f'    name: "{name}",',
        ]
        if name in PREFER:
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
