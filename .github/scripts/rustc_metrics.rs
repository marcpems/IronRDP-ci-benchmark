use std::env;
use std::fs;
use std::io;
use std::path::PathBuf;
use std::process::{Child, Command};
use std::time::{Instant, SystemTime, UNIX_EPOCH};

#[cfg(target_os = "linux")]
fn compiler_cpu(child: &mut Child) -> io::Result<(f64, f64)> {
    unsafe extern "C" {
        fn waitid(kind: i32, id: u32, info: *mut std::ffi::c_void, options: i32) -> i32;
        fn sysconf(name: i32) -> i64;
    }
    let mut info = [0_u64; 16];
    loop {
        // Leave the exited child waitable so /proc retains its own thread CPU totals.
        let result = unsafe { waitid(1, child.id(), info.as_mut_ptr().cast(), 4 | 0x0100_0000) };
        if result == 0 {
            break;
        }
        let error = io::Error::last_os_error();
        if error.kind() != io::ErrorKind::Interrupted {
            return Err(error);
        }
    }
    let stat = fs::read_to_string(format!("/proc/{}/stat", child.id()))?;
    let (_, fields) = stat.rsplit_once(") ").ok_or_else(|| io::Error::other("bad process stat"))?;
    let fields: Vec<_> = fields.split_whitespace().collect();
    let ticks = unsafe { sysconf(2) };
    if ticks <= 0 {
        return Err(io::Error::other("invalid CPU tick frequency"));
    }
    let parse = |index: usize| -> io::Result<f64> {
        fields.get(index).ok_or_else(|| io::Error::other("missing process CPU field"))?
            .parse::<f64>().map(|v| v / ticks as f64).map_err(io::Error::other)
    };
    Ok((parse(11)?, parse(12)?))
}

#[cfg(target_os = "windows")]
fn compiler_cpu(child: &mut Child) -> io::Result<(f64, f64)> {
    use std::os::windows::io::AsRawHandle;
    #[repr(C)]
    #[derive(Default)]
    struct FileTime { low: u32, high: u32 }
    #[link(name = "kernel32")]
    unsafe extern "system" {
        fn GetProcessTimes(
            process: *mut std::ffi::c_void, creation: *mut FileTime,
            exit: *mut FileTime, kernel: *mut FileTime, user: *mut FileTime,
        ) -> i32;
    }
    child.wait()?;
    let (mut created, mut exited, mut kernel, mut user) =
        (FileTime::default(), FileTime::default(), FileTime::default(), FileTime::default());
    if unsafe { GetProcessTimes(child.as_raw_handle(), &mut created, &mut exited, &mut kernel, &mut user) } == 0 {
        return Err(io::Error::last_os_error());
    }
    let seconds = |v: FileTime| ((u64::from(v.high) << 32) | u64::from(v.low)) as f64 / 10_000_000.0;
    Ok((seconds(user), seconds(kernel)))
}

fn json_string(value: &str) -> String {
    let mut output = String::from("\"");
    for ch in value.chars() {
        match ch {
            '"' => output.push_str("\\\""),
            '\\' => output.push_str("\\\\"),
            '\n' => output.push_str("\\n"),
            '\r' => output.push_str("\\r"),
            '\t' => output.push_str("\\t"),
            ch if ch < ' ' => output.push_str(&format!("\\u{:04x}", u32::from(ch))),
            ch => output.push(ch),
        }
    }
    output.push('"');
    output
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let arguments: Vec<String> = env::args().skip(1).collect();
    let executable = arguments.first().ok_or("missing compiler executable")?;
    let directory = PathBuf::from(env::var("RUST_METRICS_DIR")?);
    let start = Instant::now();
    let mut child = Command::new(executable).args(&arguments[1..]).spawn()?;
    let (user, kernel) = compiler_cpu(&mut child)?;
    let status = child.wait()?;
    let elapsed = start.elapsed().as_secs_f64();
    let timestamp = SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos();
    let environment = [
        "CARGO_MANIFEST_DIR", "CARGO_MANIFEST_PATH", "CARGO_PKG_NAME",
        "CARGO_PKG_VERSION", "CARGO_PKG_VERSION_MAJOR", "CARGO_PKG_VERSION_MINOR",
        "CARGO_PKG_VERSION_PATCH", "CARGO_PKG_VERSION_PRE", "OUT_DIR",
    ].iter().filter_map(|key| env::var(key).ok().map(|value| {
        format!("{}:{}", json_string(key), json_string(&value))
    })).collect::<Vec<_>>().join(",");
    let json = format!(
        "{{\"argv\":[{}],\"cwd\":{},\"environment\":{{{}}},\"wall_seconds\":{},\"user_seconds\":{},\"kernel_seconds\":{},\"exit_code\":{}}}\n",
        arguments.iter().map(|a| json_string(a)).collect::<Vec<_>>().join(","),
        json_string(&env::current_dir()?.to_string_lossy()), environment, elapsed, user, kernel,
        status.code().unwrap_or(-1),
    );
    fs::write(directory.join(format!("{}-{timestamp}.json", std::process::id())), json)?;
    std::process::exit(status.code().unwrap_or(1));
}
