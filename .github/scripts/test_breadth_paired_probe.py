import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tarfile
import unittest
import uuid
import zipfile
from unittest.mock import patch

import breadth_paired_probe as paired
from breadth_probe import save


class PairedProbeTests(unittest.TestCase):
    def setUp(self):
        self.root = Path.cwd() / f".paired-probe-tests-{uuid.uuid4().hex}"
        self.root.mkdir()
        self.addCleanup(shutil.rmtree, self.root)
        self.corpus_path = paired.ROOT / "ci-benchmark" / "breadth" / "corpus.json"
        self.release_path = paired.ROOT / "ci-benchmark" / "x64-pgo-replay-protocol.json"
        self.corpus = json.loads(self.corpus_path.read_text(encoding="utf-8"))
        self.replay = json.loads(self.release_path.read_text(encoding="utf-8"))
        self.protocol = {"host": paired.HOST, "rust_version": "1.94.1",
                         "rust_sha": self.replay["rust_sha"], "cores": 4,
                         "independent_vms": 5, "warmup_rounds": 1, "measured_rounds": 3,
                         "variants": ["base", "test"],
                         "projects": [p["id"] for p in self.corpus["projects"]],
                         "scenarios": [s["id"] for s in self.corpus["scenarios"]],
                         "corpus_sha256": paired.digest(self.corpus_path),
                         "release_protocol_sha256": paired.digest(self.release_path)}
        self.protocol_path = self.root / "protocol.json"
        save(self.protocol_path, self.protocol)

    def test_frozen_inputs_and_design_fail_closed(self):
        loaded = paired.load_inputs(self.protocol_path, self.corpus_path, self.release_path, "fd", 1)
        self.assertEqual(loaded[3]["id"], "fd")
        for key, value in (("corpus_sha256", "changed"), ("release_protocol_sha256", "changed"),
                           ("rust_version", "1.101.0"), ("variants", ["test", "base"]),
                           ("rust_sha", "wrong"), ("measured_rounds", 2),
                           ("projects", ["fd"]), ("scenarios", ["full-check"])):
            with self.subTest(key=key):
                save(self.protocol_path, {**self.protocol, key: value})
                with self.assertRaises(ValueError):
                    paired.load_inputs(self.protocol_path, self.corpus_path, self.release_path, "fd", 1)
        save(self.protocol_path, self.protocol)
        for replicate in (0, 6, True):
            with self.assertRaises(ValueError):
                paired.load_inputs(self.protocol_path, self.corpus_path, self.release_path, "fd", replicate)
        with self.assertRaises(ValueError):
            paired.load_inputs(self.protocol_path, self.corpus_path, self.release_path, "reserve", 1)

    def test_all_forty_rows_planned_and_order_balanced_across_independent_vms(self):
        first_counts = {"base": 0, "test": 0}
        for vm in range(1, 6):
            rows = paired.planned_rows(self.protocol, self.corpus["scenarios"], vm)
            self.assertEqual(len(rows), 40)
            self.assertEqual(len({row["path"] for row in rows}), 40)
            self.assertEqual(sum(row["warmup"] for row in rows), 10)
            prior = None
            for round_index in range(4):
                round_rows = [row for row in rows if row["round"] == round_index]
                first = round_rows[0]["variant"]
                if prior is not None:
                    self.assertNotEqual(first, prior)
                prior = first
                if round_index:
                    first_counts[first] += 1
                self.assertEqual({r["variant"] for r in round_rows}, {"base", "test"})
                for row in round_rows:
                    self.assertEqual(row["exclusion"], "preplanned-warmup" if row["warmup"] else None)
                    self.assertIn(f"r0-{row['variant']}-{row['scenario']}", row["correctness_path"])
        self.assertEqual(abs(first_counts["base"] - first_counts["test"]), 1)

    def test_reference_requires_exact_complete_qualified_replay_member(self):
        protocol = {**self.protocol, "reference_index_member": "x64-pgo-fresh-replay-1/index.json",
                    "reference_index_sha256": "45484afbf804350af86411197426be470cd9a570e97f4d887f5430a920610055"}
        archive = paired.ROOT / "ci-benchmark" / "x64-pgo-fresh-replay-evidence.zip"
        reference = paired.load_reference(archive, protocol, self.replay)
        self.assertEqual(reference["cargo_sha256"],
                         "43226f7efc5ea12b88c9156da97f8954b9af582673baadb3fb1a3ebec5d97348")
        self.assertEqual(set(reference["compiler_identity"]), {"base", "test"})
        self.assertEqual(len(reference["stdlib"]), 45)
        with self.assertRaisesRegex(ValueError, "checksum"):
            paired.load_reference(archive, {**protocol, "reference_index_sha256": "changed"}, self.replay)
        with zipfile.ZipFile(archive) as original:
            data = json.loads(original.read(protocol["reference_index_member"]))
        for i, (key, value) in enumerate((("complete", False), ("benchmark_run", "other"),
                                         ("attempt", "2"), ("protocol", {}))):
            bad = json.dumps({**data, key: value}).encode()
            corrupted = self.root / f"reference-{i}.zip"
            with zipfile.ZipFile(corrupted, "w") as bundle:
                bundle.writestr(protocol["reference_index_member"], bad)
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "incomplete qualified"):
                paired.load_reference(corrupted, {
                    **protocol, "reference_index_sha256": hashlib.sha256(bad).hexdigest()}, self.replay)

    def test_overrides_rejected_and_offline_profile_settings_preserved(self):
        for key in ("RUSTFLAGS", "RUSTDOC", "RUSTUP_TOOLCHAIN", "CARGO_PROFILE_DEV_DEBUG",
                    "CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_LINKER", "CARGO_INCREMENTAL",
                    "CARGO_BUILD_RUSTFLAGS", "CL", "CXXFLAGS", "RUSTC_WRAPPER"):
            with self.subTest(key=key), self.assertRaises((ValueError, RuntimeError)):
                base = paired.clean_environment({key: "override"}, self.root / "ch", self.root / "rh")
                paired.compiler_environment(base, Path("rustc.exe"), 4, "0")
        base = paired.clean_environment({"GH_TOKEN": "secret", "CARGO_HOME": "inherited"},
                                        self.root / "ch", self.root / "rh")
        env = paired.compiler_environment(base, self.root / "rustc.exe", 4, "1")
        self.assertNotIn("GH_TOKEN", env)
        self.assertNotIn("CARGO_PROFILE_DEV_DEBUG", env)
        self.assertEqual(env["CARGO_HOME"], str(self.root / "ch"))
        self.assertEqual(env["CARGO_NET_OFFLINE"], "true")
        self.assertEqual(env["CARGO_BUILD_JOBS"], "4")
        self.assertEqual(env["CARGO_INCREMENTAL"], "1")

    def tool_fixture(self):
        rustup = self.root / "rh"
        official = rustup / "toolchains" / "1.94.1-x86_64-pc-windows-msvc" / "bin" / "rustc.exe"
        official.parent.mkdir(parents=True)
        for name in ("rustc.exe", "rustc_driver-official.dll", "cargo.exe", "rustdoc.exe"):
            (official.parent / name).write_bytes(name.encode())
        standard = official.parent.parent / "lib" / "rustlib" / paired.HOST / "lib"
        standard.mkdir(parents=True)
        (standard / "libstd-common.rlib").write_bytes(b"common std")
        artifacts = self.root / "artifacts"
        dist = artifacts / "x64-pgo-local-dist"
        evidence = artifacts / "x64-pgo-local-evidence"
        dist.mkdir(parents=True)
        evidence.mkdir()
        archive = dist / f"rustc-1.94.1-{paired.HOST}.tar.xz"
        with tarfile.open(archive, "w:xz") as bundle:
            for name, data in (("rustc.exe", b"candidate"), ("rustc_driver-test.dll", b"driver")):
                entry = tarfile.TarInfo(f"{archive.name.removesuffix('.tar.xz')}/rustc/bin/{name}")
                entry.size = len(data)
                bundle.addfile(entry, io.BytesIO(data))
        result = {"complete": True, "variant": "local", "run_id": self.replay["release_run"],
                  "attempt": self.replay["release_attempt"], "rust_sha": self.replay["rust_sha"]}
        save(evidence / "result.json", result)
        save(evidence / "dist-manifest.json", [
            {"name": archive.name, "sha256": paired.digest(archive), "bytes": archive.stat().st_size}])
        replay = {**self.replay, "compiler_archive_sha256": {"local": paired.digest(archive)},
                  "compiler_metadata_sha256": {"local": paired.digest(evidence / "result.json")}}
        protocol = {**self.protocol, "cargo_sha256": paired.digest(official.with_name("cargo.exe")),
                    "rustdoc_sha256": paired.digest(official.with_name("rustdoc.exe")),
                    "stdlib": {p.name: paired.digest(p) for p in standard.iterdir()},
                    "compiler_identity": {
                        "base": {"rustc_sha256": paired.digest(official), "driver_sha256": {
                            "rustc_driver-official.dll": paired.digest(official.with_name("rustc_driver-official.dll"))}},
                        "test": {"rustc_sha256": hashlib.sha256(b"candidate").hexdigest(),
                                 "driver_sha256": {"rustc_driver-test.dll": hashlib.sha256(b"driver").hexdigest()}}}}
        version = (f"host: {paired.HOST}\nrelease: 1.94.1\n"
                   f"commit-hash: {self.replay['rust_sha']}\n")
        responses = [str(official), version, version, "cargo 1.94.1 (fixture)"]
        return artifacts, rustup, protocol, replay, responses

    def test_installs_exact_release_and_routes_official_cargo_and_common_std(self):
        artifacts, rustup, protocol, replay, responses = self.tool_fixture()
        output = self.root / "out"
        output.mkdir()
        base = paired.clean_environment({}, output / "ch", rustup)
        with patch.object(paired.subprocess, "check_output", side_effect=responses) as command:
            compilers, cargo, rustdoc, identity = paired.prepare_tools(
                artifacts, rustup, output, protocol, replay, base, protocol)
        self.assertEqual(compilers["base"], Path(responses[0]))
        self.assertTrue(compilers["test"].is_relative_to(output))
        self.assertEqual(cargo, compilers["base"].with_name("cargo.exe"))
        self.assertEqual(rustdoc, compilers["base"].with_name("rustdoc.exe"))
        self.assertEqual(identity["stdlib"], protocol["stdlib"])
        candidate_std = compilers["test"].parent.parent / "lib" / "rustlib" / paired.HOST / "lib"
        self.assertEqual({p.name: paired.digest(p) for p in candidate_std.iterdir()}, protocol["stdlib"])
        self.assertEqual(command.call_args_list[0].kwargs["env"]["RUSTUP_HOME"], str(rustup))
        self.assertEqual(command.call_args_list[1].kwargs["env"]["RUSTC"], str(compilers["base"]))
        self.assertEqual(command.call_args_list[2].kwargs["env"]["RUSTC"], str(compilers["test"]))

    def test_changed_artifact_std_tools_driver_and_versions_are_rejected(self):
        artifacts, rustup, original, replay, responses = self.tool_fixture()
        cases = [("cargo_sha256", "changed"), ("rustdoc_sha256", "changed"),
                 ("stdlib", {"libstd-common.rlib": "changed"})]
        changed = copy.deepcopy(original["compiler_identity"])
        changed["test"]["driver_sha256"] = {"rustc_driver-test.dll": "changed"}
        cases.append(("compiler_identity", changed))
        for i, (key, value) in enumerate(cases):
            with self.subTest(key=key):
                output = self.root / f"o{i}"
                output.mkdir()
                base = paired.clean_environment({}, output / "ch", rustup)
                with patch.object(paired.subprocess, "check_output", side_effect=responses), \
                        self.assertRaises(ValueError):
                    paired.prepare_tools(artifacts, rustup, output, {**original, key: value}, replay,
                                         base, {**original, key: value})
        for i, response_index in enumerate((1, 2, 3)):
            output = self.root / f"v{i}"
            output.mkdir()
            bad = responses.copy()
            bad[response_index] = bad[response_index].replace("1.94.1", "1.101.0")
            with patch.object(paired.subprocess, "check_output", side_effect=bad), \
                    self.assertRaisesRegex(ValueError, "version mismatch"):
                paired.prepare_tools(artifacts, rustup, output, original, replay,
                                     paired.clean_environment({}, output / "ch", rustup), original)
        next((artifacts / "x64-pgo-local-dist").iterdir()).write_bytes(b"corrupted")
        output = self.root / "corrupt"
        output.mkdir()
        with patch.object(paired.subprocess, "check_output", return_value=responses[0]), \
                self.assertRaisesRegex(RuntimeError, "differs from preregistered"):
            paired.prepare_tools(artifacts, rustup, output, original, replay,
                                 paired.clean_environment({}, output / "ch", rustup), original)

    def execute_fixture(self, fail_correctness=False, bad_noop=False):
        source, output = self.root / "source", self.root / "out"
        source.mkdir()
        output.mkdir()
        edit = source / "source.rs"
        edit.write_bytes(b"fn main() {}\r\n")
        project = {**self.corpus["projects"][0], "source_edit": "source.rs"}
        compilers = {name: self.root / name / "rustc.exe" for name in ("base", "test")}
        cargo, rustdoc = self.root / "official" / "cargo.exe", self.root / "official" / "rustdoc.exe"
        index = {"runs": paired.planned_rows(self.protocol, self.corpus["scenarios"], 1)}
        commands = []

        def metered(command, cwd, env, cores, prefix, background):
            self.assertEqual(cwd, source)
            self.assertEqual(cores, 4)
            self.assertEqual(env["CARGO_NET_OFFLINE"], "true")
            self.assertEqual(command[0], str(cargo))
            self.assertEqual(command[-2:], ["--target", paired.HOST])
            self.assertIn("--frozen", command)
            self.assertEqual(env["RUSTDOC"], str(rustdoc))
            variant = "base" if "-base-" in prefix.parent.name else "test"
            self.assertEqual(env["RUSTC"], str(compilers[variant]))
            target = Path(env["CARGO_TARGET_DIR"])
            target.mkdir(exist_ok=True)
            (target / "artifact").write_bytes(b"target")
            commands.append((command, prefix))
            noop = "incremental-noop" in prefix.parent.name and prefix.name == "measured"
            if "comment-edit" in prefix.parent.name and prefix.name == "measured":
                self.assertIn(b"breadth incremental comment-only edit", edit.read_bytes())
            prefix.with_suffix(".stdout").write_text(
                json.dumps({"reason": "compiler-artifact", "fresh": noop and not bad_noop}) + "\n"
                + json.dumps({"reason": "build-finished", "success": True}) + "\n", encoding="utf-8")
            measurement = {"exit_code": 0, "wall_seconds": 5000 if noop else 1, "command": command}
            save(prefix.with_suffix(".measurement.json"), measurement)
            if fail_correctness and prefix.name.startswith("correctness"):
                raise RuntimeError("original correctness failure")
            return measurement

        with patch.object(paired, "telemetry_executables", return_value=[]), \
                patch.object(paired, "verify_source", return_value="index"), \
                patch("breadth_probe.verify_source", return_value="index"), \
                patch("breadth_probe.metered", side_effect=metered):
            try:
                paired.execute_cells(source, output, project, self.corpus, self.protocol,
                                     compilers, cargo, rustdoc, {}, {}, index)
            finally:
                self.assertEqual(edit.read_bytes(), b"fn main() {}\r\n")
        return output, index, commands, project

    def test_full_matrix_routes_both_variants_noop_edit_and_unfiltered_warmup_correctness(self):
        output, index, commands, project = self.execute_fixture()
        self.assertTrue(all(row["status"] == "passed" for row in index["runs"]))
        checks = [(command, prefix) for command, prefix in commands if prefix.name.startswith("correctness")]
        self.assertEqual(len(checks), 2 * 5 * len(project["correctness"]))
        for command, prefix in checks:
            self.assertTrue(prefix.parent.name.startswith("r0-"))
            number = int(prefix.name.split("-")[-1])
            self.assertEqual(command[1:], [*project["correctness"][number], "--frozen", "--target", paired.HOST])
        for row in index["runs"]:
            result = json.loads((output / row["path"]).read_text(encoding="utf-8"))
            self.assertEqual(row["correctness_sha256"], paired.digest(output / row["correctness_path"]))
            self.assertFalse((output / row["path"]).parent.joinpath("target").exists())
            self.assertFalse((output / row["path"]).parent.joinpath("correctness-target").exists())
            if row["scenario"] == "incremental-noop":
                self.assertEqual(result["measurement"]["compiled_artifacts"], 0)
                self.assertEqual(row["measurement"]["wall_seconds"], 5000)
            self.assertEqual(len(result["correctness"]), len(project["correctness"]) if row["warmup"] else 0)
        self.assertEqual(len([1 for _, prefix in commands if prefix.name == "measured"]), 40)
        self.assertEqual(len([1 for _, prefix in commands if prefix.name == "seed"]), 16)

    def test_failed_correctness_retains_evidence_targets_and_all_planned_rows(self):
        with self.assertRaisesRegex(RuntimeError, "original correctness failure"):
            self.execute_fixture(fail_correctness=True)
        output = self.root / "out"
        index = json.loads((output / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(len(index["runs"]), 40)
        self.assertEqual(index["runs"][0]["status"], "failed")
        self.assertTrue(all(row["status"] == "pending" for row in index["runs"][1:]))
        cell = (output / index["runs"][0]["path"]).parent
        self.assertTrue((cell / "target").is_dir())
        self.assertTrue((cell / "correctness-target").is_dir())
        self.assertIn("original correctness failure", (cell / "results.json").read_text())

    def test_rebuilt_noop_is_a_failure_not_a_dropped_sample(self):
        with self.assertRaisesRegex(ValueError, "no-op must reuse"):
            self.execute_fixture(bad_noop=True)
        index = json.loads((self.root / "out" / "index.json").read_text(encoding="utf-8"))
        failed = [row for row in index["runs"] if row["status"] == "failed"]
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0]["scenario"], "incremental-noop")
        self.assertTrue((self.root / "out" / failed[0]["path"]).is_file())


if __name__ == "__main__":
    unittest.main()
