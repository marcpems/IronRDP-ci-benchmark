"""Compare stdlib runtime inputs without mistaking MSVC debug identities for code."""

import hashlib
import struct
from pathlib import Path

HOST = "x86_64-pc-windows-msvc"


def u32(data, offset):
    return struct.unpack_from("<I", data, offset)[0]


def dll_identity(data):
    image = bytearray(data)
    if image[:2] != b"MZ":
        raise RuntimeError("Not a PE image")
    pe = u32(image, 60)
    optional = pe + 24
    if (image[pe:pe + 4] != b"PE\0\0"
            or struct.unpack_from("<H", image, pe + 4)[0] != 0x8664
            or struct.unpack_from("<H", image, optional)[0] != 0x20B):
        raise RuntimeError("Expected AMD64 PE32+")
    timestamp = u32(image, pe + 8)
    ranges = [(pe + 8, 4)]
    sections = optional + struct.unpack_from("<H", image, pe + 20)[0]
    rva, size = struct.unpack_from("<II", image, optional + 112 + 6 * 8)
    debug = None
    for index in range(struct.unpack_from("<H", image, pe + 6)[0]):
        offset = sections + index * 40
        virtual_size, address, raw_size, raw = struct.unpack_from("<IIII", image, offset + 8)
        if address <= rva < address + max(virtual_size, raw_size):
            debug = raw + rva - address
    if debug is None or size % 28 or debug + size > len(image):
        raise RuntimeError("Invalid PE debug directory")
    codeview = []
    for entry in range(debug, debug + size, 28):
        if u32(image, entry + 4) != timestamp:
            raise RuntimeError("Unexpected inconsistent PE debug timestamp")
        ranges.append((entry + 4, 4))
        kind, length, _, pointer = struct.unpack_from("<IIII", image, entry + 12)
        if kind == 2:
            if pointer + length > len(image) or image[pointer:pointer + 4] != b"RSDS" or length < 25:
                raise RuntimeError("Invalid CodeView record")
            codeview.append({
                "guid": image[pointer + 4:pointer + 20].hex(),
                "age": u32(image, pointer + 20),
                "pdb": bytes(image[pointer + 24:pointer + length]).rstrip(b"\0").decode("utf-8"),
            })
            ranges.append((pointer + 4, 16))
    if len(codeview) != 1:
        raise RuntimeError("Expected exactly one bound PDB record")
    for offset, length in ranges:
        image[offset:offset + length] = b"\0" * length
    return {
        "canonical_sha256": hashlib.sha256(image).hexdigest(),
        "timestamp": timestamp, "codeview": codeview[0], "ignored_metadata_ranges": ranges,
    }


def pdb_identity(data):
    if data[:32] != b"Microsoft C/C++ MSF 7.00\r\n\x1aDS\0\0\0":
        raise RuntimeError("Expected Microsoft MSF 7 PDB")
    block_size, _, blocks, directory_size, _, block_map = struct.unpack_from("<IIIIII", data, 32)
    if block_size not in (512, 1024, 2048, 4096) or blocks * block_size != len(data):
        raise RuntimeError("Invalid PDB block layout")
    count = (directory_size + block_size - 1) // block_size
    if count * 4 > block_size:
        raise RuntimeError("Unsupported multiblock PDB directory map")
    indices = struct.unpack_from(f"<{count}I", data, block_map * block_size)
    directory = b"".join(data[index * block_size:(index + 1) * block_size] for index in indices)
    sizes = struct.unpack_from(f"<{u32(directory, 0)}I", directory, 4)
    cursor = 4 + len(sizes) * 4
    for stream, size in enumerate(sizes):
        pages = 0 if size == 0xFFFFFFFF else (size + block_size - 1) // block_size
        indices = struct.unpack_from(f"<{pages}I", directory, cursor)
        cursor += pages * 4
        if stream == 1:
            content = b"".join(data[index * block_size:(index + 1) * block_size] for index in indices)[:size]
            return {"signature": u32(content, 4), "age": u32(content, 8), "guid": content[12:28].hex()}
    raise RuntimeError("PDB information stream is missing")


def compare_stdlib(packages, records):
    arms = {}
    for arm, package in packages.items():
        root = Path(package) / "lib/rustlib" / HOST / "lib"
        data = {path.name: path.read_bytes() for path in sorted(root.iterdir()) if path.is_file()}
        raw = {name: hashlib.sha256(value).hexdigest() for name, value in data.items()}
        if raw != records[arm]["stdlib"]:
            raise RuntimeError("Actual stdlib differs from its original package manifest")
        canonical, dlls, excluded = {}, {}, {}
        for name, value in data.items():
            if name.endswith(".pdb"):
                dll_name = name[:-4] + ".dll"
                if not name.startswith("std-") or dll_name not in data:
                    raise RuntimeError("Unexpected PDB outside native std runtime")
                dll = dll_identity(data[dll_name])
                pdb = pdb_identity(value)
                if (pdb["guid"] != dll["codeview"]["guid"] or pdb["age"] != dll["codeview"]["age"]
                        or pdb["signature"] != dll["timestamp"]
                        or dll["codeview"]["pdb"] != name):
                    raise RuntimeError("PDB does not bind to its own standard-library DLL")
                excluded[name] = {"sha256": raw[name], "identity": pdb, "reason": "Non-runtime debug symbols"}
            elif name.endswith(".dll"):
                if not name.startswith("std-") or name[:-4] + ".pdb" not in data:
                    raise RuntimeError("Unexpected native stdlib DLL")
                dlls[name] = dll_identity(value)
                canonical[name] = dlls[name]["canonical_sha256"]
            else:
                canonical[name] = raw[name]
        arms[arm] = {"raw": raw, "canonical_runtime": canonical, "dlls": dlls,
                     "excluded_debug_files": excluded}
    if arms["baseline"]["canonical_runtime"] != arms["rust-thin"]["canonical_runtime"]:
        raise RuntimeError("Native stdlib runtime content differs beyond permitted linker debug metadata")
    if set(arms["baseline"]["excluded_debug_files"]) != set(arms["rust-thin"]["excluded_debug_files"]):
        raise RuntimeError("Native stdlib debug-file populations differ")
    return {
        "complete": True, "policy": "Exact rlib/import-library bytes; DLL bytes equal after zeroing only "
        "COFF/debug timestamps and RSDS GUID; retain each arm's bound non-runtime PDB unchanged",
        "binary_modifications": False, "stdlib_transplantation": False, "arms": arms,
    }
