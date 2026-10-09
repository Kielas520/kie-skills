use demo_crate::{parse_line, parse_lines};

#[test]
fn parses_single_line() {
    let fields = parse_line("a=1 b=2");
    assert_eq!(fields.len(), 2);
}

#[test]
fn skips_blank_lines() {
    let rows = parse_lines(&["a=1", "", "b=2"]);
    assert_eq!(rows.len(), 2);
}
