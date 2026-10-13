use logfmt::{parse, render, stats};

#[test]
fn parse_keeps_level_and_message() {
    let entries = parse("INFO 启动完成\nWARN 队列积压\n");
    assert_eq!(entries.len(), 2);
    assert_eq!(entries[0].level, "INFO");
    assert_eq!(entries[1].message, "队列积压");
}

#[test]
fn parse_skips_blank_lines() {
    let entries = parse("INFO 启动完成\n\nDEBUG 收到心跳\n");
    assert_eq!(entries.len(), 2);
}

#[test]
fn parse_ignores_trailing_newline() {
    let entries = parse("INFO 启动完成\n");
    assert_eq!(entries.len(), 1);
}

#[test]
fn render_writes_one_line_per_entry() {
    let entries = parse("INFO 启动完成\nERROR 写入失败\n");
    assert_eq!(render(&entries), "INFO 启动完成\nERROR 写入失败\n");
}

#[test]
fn stats_counts_by_level() {
    let entries = parse("INFO a\nINFO b\nERROR c\n");
    assert_eq!(stats(&entries).get("INFO"), Some(&2));
    assert_eq!(stats(&entries).get("ERROR"), Some(&1));
}
