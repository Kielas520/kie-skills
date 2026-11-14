// 只读解析模块：从设备日志目录读出全部记录，按时间戳升序返回
pub struct Entry {
    pub timestamp: u64,
    pub level: String,
    pub message: String,
}

pub fn read_entries(device: &str) -> std::io::Result<Vec<Entry>> {
    let path = format!("logs/{device}.log");
    let text = std::fs::read_to_string(path)?;
    let mut entries: Vec<Entry> = text
        .lines()
        .filter_map(|line| {
            let mut parts = line.splitn(3, ' ');
            let timestamp = parts.next()?.parse().ok()?;
            let level = parts.next()?.to_string();
            let message = parts.next().unwrap_or("").to_string();
            Some(Entry { timestamp, level, message })
        })
        .collect();
    entries.sort_by_key(|entry| entry.timestamp);
    Ok(entries)
}
