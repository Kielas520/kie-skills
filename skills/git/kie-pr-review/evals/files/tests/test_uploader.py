from unittest import mock

import uploader


def test_upload_success():
    resp = mock.MagicMock()
    resp.status = 200
    resp.__enter__.return_value = resp
    with mock.patch("urllib.request.urlopen", return_value=resp):
        assert uploader.upload([{"msg": "a"}]) is True
