import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pipeline.providers.youtube.publish import (
    PublicPublishPlan,
    _record_public_publication,
    _set_public_visibility,
)


class _Response:
    def __init__(self, payload=b""):
        self._payload = payload

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class YouTubePublishTests(unittest.TestCase):
    def test_visibility_update_uses_status_only_and_confirms_public(self):
        plan = PublicPublishPlan("file-001", "abc123", "Title", False, True)
        with patch(
            "pipeline.providers.youtube.publish.urlopen",
            return_value=_Response(b'{"id":"abc123","status":{"privacyStatus":"public"}}'),
        ) as request:
            _set_public_visibility("access-token", plan)
        update = request.call_args.args[0]
        self.assertEqual(update.method, "PUT")
        self.assertIn("part=status", update.full_url)
        self.assertIn(b'"privacyStatus": "public"', update.data)
        self.assertNotIn(b'"snippet"', update.data)

    def test_record_public_publication_advances_lifecycle_only_after_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "episodes/file-001"
            path.mkdir(parents=True)
            (path / "manifest.json").write_text(json.dumps({
                "status": "approved_for_publish",
                "publishing": {"youtube_video_id": "abc123", "youtube_privacy": "private", "published_at": None},
            }))
            _record_public_publication(root, PublicPublishPlan("file-001", "abc123", "Title", False, True))
            manifest = json.loads((path / "manifest.json").read_text())
            self.assertEqual(manifest["status"], "published")
            self.assertEqual(manifest["publishing"]["youtube_privacy"], "public")
            self.assertTrue(manifest["publishing"]["published_at"].endswith("Z"))


if __name__ == "__main__":
    unittest.main()
