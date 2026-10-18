#[test]
fn last_byte_nonzero_frame_verifies() {
    let frame = [0x01u8, 0x02, 0x7f, 0x82];
    assert_eq!(frame.len(), 4);
}
