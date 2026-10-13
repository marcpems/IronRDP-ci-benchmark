"""Same-VM cold LLVM/LLD comparisons using the upstream final-build configuration."""

import copy
import json
from pathlib import Path
import shutil
import subprocess
import time
import tomllib

from build_arm_compilers import digest, save
from native_ci_probe import telemetry_executables
from process_metrics import measure, measurement_session
from release_phase_summary import summarize
from upstream_release_probe import BUILD_SCRIPT, SETTINGS, validate_config


def trial_order(first):
    index = SETTINGS.index(first)
    return SETTINGS[index:] + SETTINGS[:index]


def normalized_config(config):
    result = copy.deepcopy(config)
    result["build"].pop("jobs", None)
    result["llvm"].pop("link-jobs", None)
    # Configure records its arguments as well as the resulting settings.
    for section in result.values():
        if not isinstance(section, dict):
            continue
        for value in section.values():
            if isinstance(value, list):
                for knob in ("build.jobs=6", "llvm.link-jobs=1"):
                    if knob in value:
                        index = value.index(knob)
                        if index == 0 or value[index - 1] != "--set":
                            raise RuntimeError("malformed recorded scheduling override")
                        del value[index - 1:index + 1]
    return result


def cmake_cache(path):
    values = {}
    for line in path.read_text(errors="replace").splitlines():
        if not line or line.startswith(("//", "#")) or "=" not in line:
            continue
        key, value = line.split("=", 1)
        name, kind = key.split(":", 1)
        values[name] = {"type": kind, "value": value}
    return values


def normalized_cache(cache):
    return {k: v for k, v in cache.items()
            if k not in ("LLVM_PARALLEL_COMPILE_JOBS", "LLVM_PARALLEL_LINK_JOBS")}


def run_crossover(source, output, first, env, provenance, original_config):
    if provenance["host"] != "x86_64-pc-windows-msvc" or original_config is None:
        raise RuntimeError("crossover requires the validated x64 baseline profile/configuration")
    validate_config(original_config, provenance["host"], "baseline")
    prefix = "RUST_BACKTRACE=full python x.py dist bootstrap --include-default-paths"
    if not env["SCRIPT"].startswith(prefix):
        raise RuntimeError("missing validated upstream final-build command")
    command = env["SCRIPT"].replace(
        prefix, "RUST_BACKTRACE=full python x.py build src/llvm-project/llvm src/llvm-project/lld", 1)
    order = trial_order(first)
    provenance = {
        **provenance, "production_mode": "same-VM LLVM/LLD component crossover",
        "coverage": "LLVM/LLD component checks only; not a qualified full distribution",
        "profile_setting": "baseline", "order": order, "script": command,
        "cache": "fresh LLVM/LLD object trees and sccache per trial; common prepared bootstrap and OS cache",
        "timing_caveat": "component timing, not full release; compare within VM, not raw times across CPUs",
    }
    save(output / "provenance.json", provenance)
    host_build = source / "build" / provenance["host"]
    for name in ("llvm", "lld"):
        if (host_build / name).exists():
            raise RuntimeError(f"crossover did not start with a fresh {name} build")
    profile = source / "opt-artifacts/llvm-pgo.profdata"
    profile_hash = digest(profile)
    base_args = env["RUST_CONFIGURE_ARGS"]
    deadline = provenance["job_started_unix"] + 340 * 60
    tools = provenance["tools"]

    def execute(script, trial_env, folder):
        remaining = deadline - time.time()
        if remaining <= 0:
            raise TimeoutError("crossover reached the hosted safety deadline")
        save(output / "active-stage.json", {"stage": folder.name, "unix": time.time()})
        with measurement_session([*telemetry_executables(), tools["sccache.exe"]["path"]]) as session:
            row = measure(
                [r"C:\Program Files\Git\bin\bash.exe", "--noprofile", "--norc", "-c", BUILD_SCRIPT],
                source, {**trial_env, "SCRIPT": script}, 4, folder / "command",
                session=session, timeout=remaining)
        save(folder / "command.json", row)
        if row["exit_code"] != 0:
            raise RuntimeError(f"{folder.name} command failed: {row['exit_code']}; see retained logs")
        return row

    preparation = output / "preparation"
    preparation.mkdir()
    execute(command.replace("x.py build ", "x.py build --dry-run ", 1), env, preparation)
    baseline_config = tomllib.loads((source / "bootstrap.toml").read_text())
    if baseline_config != original_config:
        raise RuntimeError("prepared baseline differs from pinned production configuration")
    retained = source.parent / "llvm-crossover-retained"
    retained.mkdir()
    # Preserve even dry-run directories; never delete a directory to force a clean build.
    for name in ("llvm", "lld"):
        path = host_build / name
        if path.exists():
            if any(path.rglob("*.obj")):
                raise RuntimeError("preparation unexpectedly compiled LLVM or LLD objects")
            path.rename(retained / f"preparation-{name}")
    samples = []
    expected_caches = None
    expected_outputs = None
    expected_objects = None
    expected_signature = None
    for setting in order:
        folder = output / setting
        folder.mkdir()
        for name in ("llvm", "lld"):
            if (host_build / name).exists():
                raise RuntimeError(f"{setting} would reuse {name} build products")
        if shutil.disk_usage(source).free < 60 * 1024**3:
            raise RuntimeError("insufficient space for another independent LLVM/LLD build")
        cache = source.parent / f"crossover-cache-{setting}"
        cache.mkdir()
        override = {"baseline": "", "jobs6": " --set build.jobs=6",
                    "link1": " --set llvm.link-jobs=1"}[setting]
        trial_env = {**env, "SCCACHE_DIR": str(cache), "RUST_CONFIGURE_ARGS": base_args + override}
        metrics = source / "build/metrics.json"
        # Keep per-invocation evidence separate without assuming metrics append semantics.
        if metrics.exists():
            metrics.rename(folder / "previous-metrics.json")
        row = execute(command, trial_env, folder)
        config = tomllib.loads((source / "bootstrap.toml").read_text())
        validate_config(config, provenance["host"], setting)
        if normalized_config(config) != normalized_config(original_config):
            raise RuntimeError(f"{setting} changed a non-scheduling production option")
        shutil.copy2(source / "bootstrap.toml", folder / "bootstrap.toml")
        shutil.copy2(metrics, folder / "metrics.json")
        phases = summarize(json.loads(metrics.read_text()))
        llvm_seconds = sum(i["exclusive_seconds"].get("llvm_and_lld", 0)
                           for i in phases["invocations"])
        if llvm_seconds <= 0:
            raise RuntimeError("missing fresh LLVM/LLD bootstrap timing")
        caches = {name: cmake_cache(host_build / name / "build/CMakeCache.txt")
                  for name in ("llvm", "lld")}
        llvm_cache = caches["llvm"]
        if Path(llvm_cache["LLVM_PROFDATA_FILE"]["value"]).resolve() != profile.resolve():
            raise RuntimeError("LLVM did not use the pinned PGO profile")
        if llvm_cache["LLVM_PARALLEL_COMPILE_JOBS"]["value"] != ("6" if setting == "jobs6" else "4"):
            raise RuntimeError("LLVM build-job setting was not applied")
        if setting == "link1" and llvm_cache["LLVM_PARALLEL_LINK_JOBS"]["value"] != "1":
            raise RuntimeError("LLVM single-link setting was not applied")
        normalized = {name: normalized_cache(value) for name, value in caches.items()}
        if expected_caches is not None and normalized != expected_caches:
            save(folder / "cmake-caches.json", caches)
            raise RuntimeError("CMake configuration changed beyond the scheduling knobs")
        expected_caches = normalized
        save(folder / "cmake-caches.json", caches)
        objects = {name: sorted(p.relative_to(host_build / name).as_posix()
                               for p in (host_build / name).rglob("*.obj"))
                   for name in ("llvm", "lld")}
        if len(objects["llvm"]) < 1000 or not objects["lld"]:
            raise RuntimeError("component build did not produce the expected fresh object graph")
        if expected_objects is not None and objects != expected_objects:
            raise RuntimeError("fresh object-name sets differ between scheduling settings")
        expected_objects = objects
        installed = {name: sorted(p.relative_to(host_build / name).as_posix()
                                 for tree in ("bin", "lib", "include")
                                 for p in (host_build / name / tree).rglob("*") if p.is_file())
                     for name in ("llvm", "lld")}
        if expected_outputs is not None and installed != expected_outputs:
            raise RuntimeError("installed output-name sets differ between scheduling settings")
        expected_outputs = installed
        binary = host_build / "llvm/bin"
        signature = {}
        for option in ("--version", "--targets-built"):
            signature[option] = subprocess.check_output(
                [binary / "llvm-config.exe", option], text=True, timeout=30).strip()
        fixture = folder / "probe.ll"
        fixture.write_text("define i32 @main() {\n  ret i32 42\n}\n", encoding="utf-8")
        bitcode, restored, obj, exe = (folder / name for name in ("probe.bc", "restored.ll", "probe.obj", "probe.exe"))
        for probe in (
            [binary / "llvm-as.exe", fixture, "-o", bitcode],
            [binary / "llvm-dis.exe", bitcode, "-o", restored],
            [binary / "llc.exe", "-mtriple=x86_64-pc-windows-msvc", "-filetype=obj", bitcode, "-o", obj],
            [host_build / "lld/bin/lld.exe", "-flavor", "link", "/entry:main",
             "/subsystem:console", "/nodefaultlib", f"/out:{exe}", obj],
        ):
            subprocess.run(probe, check=True, timeout=60)
        if "ret i32 42" not in restored.read_text() or subprocess.run([exe], timeout=30).returncode != 42:
            raise RuntimeError("fresh LLVM/LLD roundtrip or executable probe failed")
        if expected_signature is not None and signature != expected_signature:
            raise RuntimeError("LLVM version or enabled targets changed")
        expected_signature = signature
        if digest(profile) != profile_hash:
            raise RuntimeError("the common PGO profile changed during the crossover")
        subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
        sample = {
            "setting": setting, "position": len(samples), "measurement": row,
            "llvm_lld_seconds": llvm_seconds, "phases": phases, "signature": signature,
            "fresh_objects": {name: len(paths) for name, paths in objects.items()},
            "installed_outputs": installed, "component_checks_passed": True,
            "profile_sha256": profile_hash,
        }
        save(folder / "sample.json", sample)
        samples.append(sample)
        save(output / "samples.json", samples)
        for name in ("llvm", "lld"):
            (host_build / name).rename(retained / f"{setting}-{name}")
    baseline = next(s["llvm_lld_seconds"] for s in samples if s["setting"] == "baseline")
    save(output / "result.json", {
        **provenance, "complete": True, "full_distribution_qualified": False,
        "full_release_timing_complete": False,
        "profile_sha256": profile_hash, "samples": samples,
        "paired_component_change_percent": {
            s["setting"]: 100 * (s["llvm_lld_seconds"] / baseline - 1) for s in samples},
        "completed_unix": time.time(),
    })
