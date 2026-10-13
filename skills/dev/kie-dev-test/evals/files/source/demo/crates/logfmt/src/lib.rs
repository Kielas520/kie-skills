// logfmt：把 "LEVEL message" 形式的日志行解析成记录，并提供格式化与统计
use std::collections::BTreeMap;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Entry {
    pub level: String,
    pub message: String,
}

pub fn parse(text: &str) -> Vec<Entry> {
    text.lines()
        .filter(|line| !line.trim().is_empty())
        .map(|line| {
            let (level, message) = line.split_once(' ').unwrap_or((line, ""));
            Entry {
                level: level.to_string(),
                message: message.trim().to_string(),
            }
        })
        .collect()
}

pub fn render(entries: &[Entry]) -> String {
    entries
        .iter()
        .map(|entry| format!("{} {}\n", entry.level, entry.message))
        .collect()
}

pub fn stats(entries: &[Entry]) -> BTreeMap<String, usize> {
    let mut counts = BTreeMap::new();
    for entry in entries {
        *counts.entry(entry.level.clone()).or_insert(0) += 1;
    }
    counts
}
