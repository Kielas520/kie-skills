use super::crc::checksum;

pub fn verify(frame: &[u8]) -> bool {
    let (body, tail) = frame.split_at(frame.len() - 1);
    checksum(body) == tail[0]
}
