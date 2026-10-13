// v0.1.0 的解析与输出：空行会被当成一条 level 与 message 都空的记录
use std::collections::BTreeMap;
use std::env;
use std::fs;

struct Entry {
    level: String,
    message: String,
}

fn parse(text: &str) -> Vec<Entry> {
    text.lines()
        .map(|line| {
            let (level, message) = line.split_once(' ').unwrap_or((line, ""));
            Entry {
                level: level.to_string(),
                message: message.trim().to_string(),
            }
        })
        .collect()
}

fn main() {
    let path = env::args().nth(1).expect("用法: logfmt-0.1.0 <日志文件>");
    let text = fs::read_to_string(&path).expect("读取日志文件失败");
    let entries = parse(&text);
    for entry in &entries {
        println!("{} {}", entry.level, entry.message);
    }
    let mut counts: BTreeMap<&str, usize> = BTreeMap::new();
    for entry in &entries {
        *counts.entry(entry.level.as_str()).or_insert(0) += 1;
    }
    for (level, count) in counts {
        println!("统计 {level}\t{count}");
    }
}
