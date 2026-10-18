pub mod legacy;

pub fn parse_line(line: &str) -> Vec<(String, String)> {
    line.split_whitespace()
        .filter_map(|part| part.split_once('='))
        .map(|(key, value)| (key.to_string(), value.to_string()))
        .collect()
}

pub fn count_fields(line: &str) -> usize {
    return parse_line(line).len();
}
