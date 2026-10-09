use std::collections::HashMap;

pub fn parse_line(line: &str) -> Vec<(String, String)> {
    let mut fields = Vec::new();
    for part in line.split_whitespace() {
        if let Some((key, value)) = part.split_once('=') {
            fields.push((key.to_string(), value.to_string()));
        }
    }
    return fields;
}

pub fn parse_lines(lines: &[&str]) -> Vec<Vec<(String, String)>> {
    lines.iter().filter(|line| !line.trim().is_empty()).map(|line| parse_line(line)).collect()
}

pub fn to_map(fields: &[(String, String)]) -> HashMap<String, String> {
    fields.iter().cloned().collect()
}
