// log export 子命令：读取设备日志，逐条格式化后打印到标准输出
use crate::parser::{read_entries, Entry};

pub struct ExportArgs {
    pub device: String,
}

pub fn run(args: &ExportArgs) -> std::io::Result<()> {
    let entries: Vec<Entry> = read_entries(&args.device)?;
    for entry in &entries {
        println!("{} {} {}", entry.timestamp, entry.level, entry.message);
    }
    Ok(())
}
