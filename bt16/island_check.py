#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#
# Island isolation check for the bt16 BT audio HAL (b16* libs).
#
# Model: the built vendor image (out/.../vendor, stock parity) with the
# island overlaid (the stock provider impl replaced by the island one),
# vendor linkerconfig with ro.vndk.version=33: vendor dirs first, then v33
# LLNDK from system, then VNDK v33 through the vndk namespace.
#
# (a) each island root: every DT_NEEDED resolves to an island file or a v33
#     LLNDK system lib (never a stock vendor/VNDK lib), and every non-weak
#     undefined symbol is defined in that closure. Symbols the host
#     executable exports (bionic global group) are reported as interposition.
# (b) every other vendor ELF: its NEEDED closure never reaches an island
#     file, and no stock ELF names an island soname anywhere.
# (c) each island lib: every address-valued dynamic tag (incl. the Android
#     packed/RELR relocation tags) points at the start of an ALLOC section,
#     of the matching type for table tags.
# (d) with --src <generic vendor dir>: each island lib has the same program
#     and section headers (llvm-readelf -lW / -SW) as its unpatched build
#     output, and differs from it only inside .dynstr.
# (e) each island lib: every .gnu.version_r vn_file is one of its DT_NEEDED
#     (bionic looks the file up among the lib's children) and is an island
#     soname or v33 LLNDK.
#
# The host executable is modelled with the blob_fixup applied
# (remove_needed android.hardware.bluetooth.audio-impl.so); it dlopen()s the
# provider by name, so the provider becomes its own dlopen root.
# Only LLNDK libs linked directly from the vendor namespace count for
# symbol lookup (bionic is_accessible); their system-side deps do not.
#
# --installed: check the files installed in out/ as they are (no overlay,
# no simulated fixup) and require them to match the island dir byte for byte.
#
# usage: island_check.py <island dir> <android root> <host exe rel path>
#                        [--installed] [--src <generic vendor dir>]
import filecmp
import os
import struct
import subprocess
import sys

from elftools.common.exceptions import ELFError
from elftools.elf.dynamic import DynamicSection
from elftools.elf.elffile import ELFFile

ISL, ROOT, HOST = sys.argv[1:4]
OPTS = sys.argv[4:]
INSTALLED = '--installed' in OPTS
SRC = OPTS[OPTS.index('--src') + 1] if '--src' in OPTS else None
P = os.path.join(ROOT, 'out/target/product/sycamore_row_5G')
V33 = os.path.join(ROOT, 'prebuilts/vndk/v33/arm64')
V33_ARCH = {'lib64': 'arch-arm64-armv8-a', 'lib': 'arch-arm-armv8-a'}


def read_list(p):
    with open(p) as f:
        return {l.strip() for l in f if l.strip()}


LLNDK = read_list(os.path.join(V33, 'configs/llndk.libraries.txt'))
VNDK = (read_list(os.path.join(V33, 'configs/vndkcore.libraries.33.txt')) |
        read_list(os.path.join(V33, 'configs/vndksp.libraries.txt')))

_elf = {}
REMOVE_NEEDED = {} if INSTALLED else {
    os.path.basename(HOST): ('android.hardware.bluetooth.audio-impl.so',),
}


def elf_info(path):
    rp = os.path.realpath(path)
    if rp in _elf:
        return _elf[rp]
    info = None
    try:
        with open(rp, 'rb') as f:
            if f.read(4) == b'\x7fELF':
                f.seek(0)
                e = ELFFile(f)
                needed, defined, undef = [], set(), set()
                for sec in e.iter_sections():
                    if isinstance(sec, DynamicSection):
                        needed = [t.needed for t in sec.iter_tags()
                                  if t.entry.d_tag == 'DT_NEEDED']
                dynsym = e.get_section_by_name('.dynsym')
                if dynsym is not None:
                    for sym in dynsym.iter_symbols():
                        n = sym.name
                        if not n:
                            continue
                        bind = sym['st_info']['bind']
                        if sym['st_shndx'] == 'SHN_UNDEF':
                            if bind == 'STB_GLOBAL':
                                undef.add(n)
                        elif (bind in ('STB_GLOBAL', 'STB_WEAK',
                                       'STB_GNU_UNIQUE', 'STB_LOOS') and
                              sym['st_other']['visibility'] in
                              ('STV_DEFAULT', 'STV_PROTECTED')):
                            defined.add(n)
                needed = [n for n in needed
                          if n not in REMOVE_NEEDED.get(os.path.basename(rp), ())]
                info = (needed, defined, undef, e.elfclass)
    except (OSError, ELFError):
        info = None
    _elf[rp] = info
    return info


# vendor image: install path -> file, island overlaid on top
fs = {}
for root, dirs, files in os.walk(os.path.join(P, 'vendor')):
    for n in files:
        full = os.path.join(root, n)
        fs[os.path.relpath(full, P)] = full
island = {}
fail = 0
for root, dirs, files in os.walk(ISL):
    for n in files:
        if n.endswith('.so'):
            full = os.path.join(root, n)
            rel = 'vendor/' + os.path.relpath(full, ISL)
            if INSTALLED:
                if rel not in fs:
                    print('FAIL not installed:', rel)
                    fail += 1
                    continue
                if not filecmp.cmp(full, fs[rel], shallow=False):
                    print('FAIL installed file differs:', rel)
                    fail += 1
                full = fs[rel]
            fs[rel] = full
            island[rel] = full
print(f'== mode: {"installed out/ files" if INSTALLED else "island overlay"}, '
      f'island files: {len(island)}')
ISLAND_FILES = {os.path.realpath(f) for f in island.values()}

sysdirs = {}


def sys_find(name, L):
    if L not in sysdirs:
        d = [os.path.join(P, 'apex/com.android.runtime', L, 'bionic'),
             os.path.join(P, 'system', L)]
        for a in sorted(os.listdir(os.path.join(P, 'apex'))):
            if a != 'com.android.vndk.v33':
                d.append(os.path.join(P, 'apex', a, L))
        sysdirs[L] = [x for x in d if os.path.isdir(x)]
    for d in sysdirs[L]:
        f = os.path.join(d, name)
        if os.path.isfile(f) and elf_info(f):
            return f
    return None


def resolve(ns, name, L):
    if ns == 'system':
        f = sys_find(name, L)
        return ('system', f) if f else None
    if ns == 'vendor':
        for d in (f'vendor/odm/{L}', f'vendor/{L}', f'vendor/{L}/hw',
                  f'vendor/{L}/egl'):
            f = fs.get(f'{d}/{name}')
            if f:
                return ('vendor', f)
        if name in LLNDK:
            return resolve('system', name, L)
        if name in VNDK:
            return resolve('vndk', name, L)
        return None
    for d in (f'vendor/{L}/vndk-sp', f'vendor/{L}/vndk'):
        f = fs.get(f'{d}/{name}')
        if f:
            return ('vndk', f)
    for sub in ('vndk-sp', 'vndk-core'):
        f = os.path.join(V33, V33_ARCH[L], 'shared', sub, name)
        if os.path.isfile(f):
            return ('vndk', f)
    if name in LLNDK:
        return resolve('system', name, L)
    return None


def closure(path, L):
    """BFS load order [(ns, file, visible)], missing [(parent, name)].
    visible: in the root's local group for symbol lookup."""
    order, seen, missing = [], {}, []
    queue = [('vendor', path, True)]
    while queue:
        ns, f, vis = queue.pop(0)
        rp = os.path.realpath(f)
        if rp in seen:
            # one load per lib; it is visible if any edge from the
            # vendor side reaches it (shared LLNDK lib)
            i = seen[rp]
            if vis and not order[i][2]:
                order[i] = order[i][:2] + (True,)
            continue
        seen[rp] = len(order)
        order.append((ns, f, vis))
        info = elf_info(f)
        if not info:
            continue
        for n in info[0]:
            r = resolve(ns, n, L)
            if r is None:
                missing.append((f, n))
            else:
                queue.append(r + (vis and (ns != 'system'),))
    return order, missing


def short(f):
    rp = os.path.realpath(f)
    for base in (ISL, P, V33, ROOT):
        if rp.startswith(os.path.realpath(base) + '/'):
            return os.path.relpath(rp, os.path.realpath(base))
    return rp


host = elf_info(os.path.join(P, HOST))
host_exports = host[1] if host else set()
print(f'== host executable {HOST}: {len(host_exports)} exported symbols, '
      f'NEEDED provider: {"android.hardware.bluetooth.audio-impl.so" in host[0]}')

print('== (a) island closure')
roots = [r for r in island if r.endswith(('/hw/audio.bluetooth.bt16.so',
                                          '/android.hardware.bluetooth.audio-impl.so'))]
for r in sorted(roots):
    order, missing = closure(island[r], 'lib64')
    isl = [f for ns, f, v in order if os.path.realpath(f) in ISLAND_FILES]
    sysl = [f for ns, f, v in order if ns == 'system' and v]
    hidden = [f for ns, f, v in order if ns == 'system' and not v]
    other = [(ns, f) for ns, f, v in order
             if os.path.realpath(f) not in ISLAND_FILES and ns != 'system']
    print(f'-- {r}: {len(isl)} island + {len(sysl)} LLNDK (+{len(hidden)} system-internal deps, not visible)')
    print('   LLNDK:', ' '.join(os.path.basename(f) for f in sysl))
    for ns, f in other:
        print('   FAIL non-island vendor/vndk lib in closure:', ns, short(f))
        fail += 1
    for p, n in missing:
        print('   FAIL unresolved NEEDED', n, 'from', short(p))
        fail += 1
    defined = {}
    for ns, f, v in order:
        if v:
            for s in elf_info(f)[1]:
                defined.setdefault(s, f)
    unres, interp = [], []
    for ns, f, v in order:
        if os.path.realpath(f) not in ISLAND_FILES:
            continue
        for s in sorted(elf_info(f)[2]):
            if s in host_exports:
                interp.append((short(f), s))
            elif s not in defined:
                unres.append((short(f), s))
    for f, s in unres:
        print('   FAIL unresolved symbol', s, 'in', f)
        fail += 1
    for f, s in interp:
        print('   WARN host exe would interpose', s, 'for', f)
    print(f'   undefined symbols unresolved: {len(unres)}, host-interposed: {len(interp)}')

print('== (b) stock ELFs never reach the island')
checked = reached = 0
for rel, f in sorted(fs.items()):
    if rel in island:
        continue
    info = elf_info(f)
    if not info:
        continue
    L = 'lib64' if info[3] == 64 else 'lib'
    checked += 1
    order, _ = closure(f, L)
    hits = [short(x) for ns, x, v in order if os.path.realpath(x) in ISLAND_FILES]
    if hits:
        reached += 1
        fail += 1
        print('   FAIL', rel, '->', ', '.join(hits))
# the provider keeps its name: the stock service dlopen()s it on purpose
names = [os.path.basename(f).encode() for f in island.values()
         if not f.endswith('/android.hardware.bluetooth.audio-impl.so')]
strhits = 0
for rel, f in sorted(fs.items()):
    if rel in island or not elf_info(f):
        continue
    with open(f, 'rb') as fh:
        data = fh.read()
    for n in names:
        if n in data:
            strhits += 1
            fail += 1
            print('   FAIL', rel, 'contains string', n.decode())
print(f'   stock ELFs checked: {checked}, NEEDED closures reaching island: {reached}, '
      f'island name strings: {strhits}')
dl = [rel for rel, f in fs.items() if rel not in island and elf_info(f)
      and b'android.hardware.bluetooth.audio-impl' in open(f, 'rb').read()]
print('   dlopen users of the swapped provider name:', ', '.join(sorted(dl)))
print('== (c) island dynamic address tags')
PTR_TAGS = {3, 4, 5, 6, 7, 12, 13, 17, 23, 25, 26, 32, 36, 0x6000000f,
            0x60000011, 0x6fffe000, 0x6ffffef5, 0x6ffffff0, 0x6ffffffc,
            0x6ffffffe}
# tag -> required raw sh_type
TAG_TYPES = {
    5: (3,),  # DT_STRTAB -> SHT_STRTAB
    6: (11,),  # DT_SYMTAB -> SHT_DYNSYM
    7: (4,), 17: (9,), 23: (4, 9),  # RELA, REL, JMPREL
    36: (19,),  # DT_RELR -> SHT_RELR
    0x6000000f: (0x60000001,),  # DT_ANDROID_REL -> SHT_ANDROID_REL
    0x60000011: (0x60000002,),  # DT_ANDROID_RELA -> SHT_ANDROID_RELA
    0x6fffe000: (0x6fffff00,),  # DT_ANDROID_RELR -> SHT_ANDROID_RELR
    0x6ffffef5: (0x6ffffff6,),  # DT_GNU_HASH -> SHT_GNU_HASH
    0x6ffffff0: (0x6fffffff,),  # DT_VERSYM -> SHT_GNU_versym
    0x6ffffffe: (0x6ffffffe,),  # DT_VERNEED -> SHT_GNU_verneed
}
ntags = 0
for rel, f in sorted(island.items()):
    with open(f, 'rb') as fh:
        e = ELFFile(fh)
        starts = {}
        for i, sec in enumerate(e.iter_sections()):
            if sec['sh_flags'] & 2 and sec['sh_size']:
                fh.seek(e['e_shoff'] + i * e['e_shentsize'] + 4)
                starts.setdefault(sec['sh_addr'], set()).add(
                    struct.unpack('<I', fh.read(4))[0])
        d = e.get_section_by_name('.dynamic')
        for i in range(d['sh_size'] // 16):
            fh.seek(d['sh_offset'] + 16 * i)
            tag, val = struct.unpack('<qQ', fh.read(16))
            if tag == 0:
                break
            if tag in PTR_TAGS:
                ntags += 1
                if val not in starts:
                    print(f'   FAIL {rel}: tag {tag:#x} -> {val:#x} is not a section start')
                    fail += 1
                elif tag in TAG_TYPES and not starts[val] & set(TAG_TYPES[tag]):
                    print(f'   FAIL {rel}: tag {tag:#x} -> {val:#x} is a section of type '
                          f'{sorted(starts[val])}')
                    fail += 1
print(f'   address tags checked: {ntags}')

print('== (d) layout vs unpatched build')
if SRC is None:
    print('   skipped (no --src)')
else:
    READELF = os.path.join(
        ROOT, 'prebuilts/clang/host/linux-x86/llvm-binutils-stable/llvm-readelf')
    ROOT_SRC = {'audio.bluetooth.bt16.so': 'hw/audio.bluetooth.default.so',
                'android.hardware.bluetooth.audio-impl.so':
                    'android.hardware.bluetooth.audio-impl.so'}
    by_new = {}
    for sub in ('', 'hw/'):
        d = os.path.join(SRC, 'lib64', sub)
        for n in os.listdir(d):
            if n.endswith('.so'):
                by_new.setdefault('b16' + n[3:], sub + n)
    same = 0
    for rel, f in sorted(island.items()):
        base = os.path.basename(f)
        orig = os.path.join(SRC, 'lib64', ROOT_SRC.get(base) or by_new.get(base, ''))
        if not os.path.isfile(orig):
            print(f'   FAIL {rel}: no unpatched source found')
            fail += 1
            continue
        ok = True
        for opt in ('-lW', '-SW'):
            a, b = (subprocess.run([READELF, opt, x], capture_output=True,
                                   text=True, check=True).stdout
                    for x in (orig, f))
            if a != b:
                print(f'   FAIL {rel}: llvm-readelf {opt} differs from {orig}')
                ok = False
        with open(orig, 'rb') as fh:
            od = fh.read()
        with open(f, 'rb') as fh:
            nd = fh.read()
            e = ELFFile(fh)
            ds = e.get_section_by_name('.dynstr')
            lo, hi = ds['sh_offset'], ds['sh_offset'] + ds['sh_size']
        if len(od) != len(nd) or od[:lo] != nd[:lo] or od[hi:] != nd[hi:]:
            print(f'   FAIL {rel}: bytes differ outside .dynstr')
            ok = False
        if ok:
            same += 1
        else:
            fail += 1
    print(f'   identical headers and bytes outside .dynstr: {same}/{len(island)}')
print('== (e) island verneed files')
sonames = set()
for f in island.values():
    with open(f, 'rb') as fh:
        d = ELFFile(fh).get_section_by_name('.dynamic')
        sonames |= {t.soname for t in d.iter_tags() if t.entry.d_tag == 'DT_SONAME'}
nvn = 0
for rel, f in sorted(island.items()):
    with open(f, 'rb') as fh:
        e = ELFFile(fh)
        needed = set(elf_info(f)[0])
        vr = e.get_section_by_name('.gnu.version_r')
        files = [v.name for v, _ in vr.iter_versions()] if vr else []
    for vf in files:
        nvn += 1
        if vf not in needed:
            print(f'   FAIL {rel}: verneed file {vf} is not in DT_NEEDED')
            fail += 1
        elif vf not in sonames and vf not in LLNDK:
            print(f'   FAIL {rel}: verneed file {vf} is neither island nor LLNDK')
            fail += 1
print(f'   verneed files checked: {nvn}')
print('RESULT:', 'PASS' if not fail else f'FAIL ({fail})')
sys.exit(1 if fail else 0)
