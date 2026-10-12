import copy
import lzma
from pathlib import Path
import tempfile
import unittest

from release_compression_probe import summarize as compression_summary, tar_digest
from release_phase_summary import summarize as phase_summary


class ReleaseThroughputTests(unittest.TestCase):
    def test_exclusive_scopes_do_not_double_count_children(self):
        metrics = {
            "system_stats": {"cpu_threads_count": 4},
            "invocations": [{
                "cmdline": "dist", "duration_including_children_sec": 101,
                "children": [{
                    "type": "bootstrap::dist::Docs", "duration_excluding_children_sec": 20,
                    "children": [{
                        "type": "bootstrap::compile::Rustc", "duration_excluding_children_sec": 80,
                    }],
                }],
            }],
        }
        row = phase_summary(metrics)["invocations"][0]
        self.assertEqual(row["exclusive_seconds"], {
            "assembly_and_compression": 20, "compiler_std_backends": 80,
        })
        self.assertEqual(row["unattributed_seconds"], 1)
        metrics["invocations"][0]["duration_including_children_sec"] = 50
        with self.assertRaisesRegex(ValueError, "exceed"):
            phase_summary(metrics)

    def test_compression_comparison_requires_complete_verified_pairs(self):
        samples = [
            {"package": "rustc", "profile": profile, "round": round_index,
             "exit_code": 0, "identical_tar_stream": True,
             "wall_seconds": seconds, "archive_bytes": size}
            for round_index in (0, 1)
            for profile, seconds, size in (("balanced", 10, 100), ("fast", 4, 120))
        ]
        result = compression_summary(samples)["rustc"]
        self.assertEqual(result["seconds_saved"], 6)
        self.assertEqual(result["compression_saving_percent"], 60)
        self.assertAlmostEqual(result["archive_growth_percent"], 20)
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            compression_summary(samples[:-1])
        broken = copy.deepcopy(samples)
        broken[0]["identical_tar_stream"] = False
        with self.assertRaisesRegex(RuntimeError, "invalid"):
            compression_summary(broken)

    def test_payload_digest_ignores_compression_but_detects_changed_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = b"identical tar byte stream\n" * 1000
            a, b, c = [root / name for name in ("a.xz", "b.xz", "c.xz")]
            a.write_bytes(lzma.compress(content, preset=6))
            b.write_bytes(lzma.compress(content, preset=1))
            c.write_bytes(lzma.compress(content + b"changed", preset=1))
            self.assertEqual(tar_digest(a), tar_digest(b))
            self.assertNotEqual(tar_digest(a), tar_digest(c))


if __name__ == "__main__":
    unittest.main()
