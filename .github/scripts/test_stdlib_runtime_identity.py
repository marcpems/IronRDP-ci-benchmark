import hashlib
from pathlib import Path
import shutil
import struct
import unittest
import uuid

from stdlib_runtime_identity import HOST, compare_stdlib


class StdlibIdentityTests(unittest.TestCase):
    def setUp(self):
        self.root = Path.cwd() / f".stdlib-test-{uuid.uuid4().hex}"
        self.root.mkdir()
        self.addCleanup(shutil.rmtree, self.root)

    def package(self, arm, stamp, guid):
        root = self.root / arm
        lib = root / "lib/rustlib" / HOST / "lib"
        lib.mkdir(parents=True)
        dll = bytearray(1024)
        dll[:2] = b"MZ"
        struct.pack_into("<I", dll, 60, 128)
        dll[128:132] = b"PE\0\0"
        struct.pack_into("<HHI", dll, 132, 0x8664, 1, stamp)
        struct.pack_into("<H", dll, 148, 240)
        struct.pack_into("<H", dll, 152, 0x20B)
        struct.pack_into("<II", dll, 152 + 112 + 48, 4096, 28)
        struct.pack_into("<IIII", dll, 392 + 8, 512, 4096, 512, 512)
        cv = b"RSDS" + guid + struct.pack("<I", 1) + b"std-fixture.pdb\0"
        struct.pack_into("<IIHHIIII", dll, 512, 0, stamp, 0, 0, 2, len(cv), 4184, 600)
        dll[600:600 + len(cv)] = cv
        (lib / "std-fixture.dll").write_bytes(dll)
        pdb = bytearray(4096 * 4)
        pdb[:32] = b"Microsoft C/C++ MSF 7.00\r\n\x1aDS\0\0\0"
        struct.pack_into("<IIIIII", pdb, 32, 4096, 0, 4, 16, 0, 3)
        struct.pack_into("<IIII", pdb, 4096, 2, 0, 28, 2)
        struct.pack_into("<III", pdb, 8192, 20000404, stamp, 1)
        pdb[8204:8220] = guid
        struct.pack_into("<I", pdb, 12288, 1)
        (lib / "std-fixture.pdb").write_bytes(pdb)
        (lib / "libstd.rlib").write_bytes(b"identical runtime input")
        return root, {"stdlib": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in lib.iterdir()}}

    def test_only_linker_debug_metadata_may_differ_without_modifying_packages(self):
        a, ra = self.package("baseline", 100, b"a" * 16)
        b, rb = self.package("rust-thin", 200, b"b" * 16)
        result = compare_stdlib({"baseline": a, "rust-thin": b}, {"baseline": ra, "rust-thin": rb})
        self.assertTrue(result["complete"])
        self.assertFalse(result["binary_modifications"])
        self.assertFalse(result["stdlib_transplantation"])
        path = b / "lib/rustlib" / HOST / "lib/std-fixture.dll"
        data = bytearray(path.read_bytes())
        data[900] = 1
        path.write_bytes(data)
        rb["stdlib"][path.name] = hashlib.sha256(data).hexdigest()
        with self.assertRaisesRegex(RuntimeError, "runtime content differs"):
            compare_stdlib({"baseline": a, "rust-thin": b}, {"baseline": ra, "rust-thin": rb})

    def test_pdb_must_bind_to_its_own_dll(self):
        a, ra = self.package("baseline", 100, b"a" * 16)
        b, rb = self.package("rust-thin", 200, b"b" * 16)
        path = b / "lib/rustlib" / HOST / "lib/std-fixture.pdb"
        data = bytearray(path.read_bytes())
        data[8204] = ord("x")
        path.write_bytes(data)
        rb["stdlib"][path.name] = hashlib.sha256(data).hexdigest()
        with self.assertRaisesRegex(RuntimeError, "does not bind"):
            compare_stdlib({"baseline": a, "rust-thin": b}, {"baseline": ra, "rust-thin": rb})


if __name__ == "__main__":
    unittest.main()
