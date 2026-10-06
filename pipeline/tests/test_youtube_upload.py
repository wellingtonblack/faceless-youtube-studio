import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pipeline.providers.youtube.upload import (
    PrivateUploadPlan,
    YouTubeUploadError,
    _record_private_upload,
    _resumable_upload,
    private_upload_plan,
)


ROOT = Path(__file__).resolve().parents[2]


class _Response:
    def __init__(self, payload=b"", headers=None):
        self._payload = payload
        self.headers = headers or {}

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class YouTubeUploadTests(unittest.TestCase):
    def test_uploaded_episode_refuses_a_duplicate_upload(self):
        with self.assertRaisesRegex(YouTubeUploadError, "status 'qc'"):
            private_upload_plan(
                ROOT, "file-001", description="FILE #001 is a work of fiction from The Impossible Files.", tags=("mystery",),
            )

    def test_upload_refuses_when_auto_publish_is_enabled(self):
        with patch.dict(os.environ, {"AUTO_PUBLISH": "true"}):
            with self.assertRaisesRegex(YouTubeUploadError, "AUTO_PUBLISH"):
                private_upload_plan(ROOT, "file-001", description="This is fiction.")

    def test_upload_request_is_private_and_disables_notifications(self):
        with tempfile.TemporaryDirectory() as directory:
            video = Path(directory) / "video.mp4"
            video.write_bytes(b"mp4")
            plan = PrivateUploadPlan("file-001", video, "Title", "This is fiction.", ("mystery",), "24", False, True)
            responses = [_Response(headers={"Location": "https://upload.example/session"}), _Response(b'{"id":"abc123"}')]
            with patch("pipeline.providers.youtube.upload.urlopen", side_effect=responses) as request:
                self.assertEqual(_resumable_upload("access-token", plan), "abc123")
            start_request = request.call_args_list[0].args[0]
            self.assertIn("notifySubscribers=false", start_request.full_url)
            self.assertIn(b'"privacyStatus": "private"', start_request.data)
            self.assertIn(b'"containsSyntheticMedia": true', start_request.data)

    def test_record_private_upload_sets_lifecycle_and_frozen_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "episodes/file-001"
            path.mkdir(parents=True)
            (path / "manifest.json").write_text(json.dumps({
                "status": "qc", "publishing": {"youtube_video_id": None, "youtube_privacy": "private", "published_at": None},
            }))
            plan = PrivateUploadPlan("file-001", root / "video.mp4", "Title", "This is fiction.", (), "24", False, True)
            _record_private_upload(root, plan, "abc123")
            manifest = json.loads((path / "manifest.json").read_text())
            metadata = json.loads((path / "publishing-metadata.json").read_text())
            self.assertEqual(manifest["status"], "upload_private")
            self.assertEqual(manifest["publishing"]["youtube_video_id"], "abc123")
            self.assertEqual(metadata["youtube_video_id"], "abc123")


if __name__ == "__main__":
    unittest.main()
