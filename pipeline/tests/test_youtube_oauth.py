import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pipeline.providers.youtube.oauth import (
    YouTubeOAuthClient,
    YouTubeOAuthError,
    _set_local_env_value,
)


class YouTubeOAuthTests(unittest.TestCase):
    def test_reads_local_credentials_without_exposing_them(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text("YOUTUBE_CLIENT_ID=client-id\nYOUTUBE_CLIENT_SECRET=secret\n")
            with patch.dict("os.environ", {}, clear=True):
                client = YouTubeOAuthClient.from_local_environment(root)
            self.assertEqual(client.client_id, "client-id")
            self.assertEqual(client.client_secret, "secret")

    def test_missing_credentials_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict("os.environ", {}, clear=True):
                with self.assertRaises(YouTubeOAuthError):
                    YouTubeOAuthClient.from_local_environment(Path(directory))

    def test_refresh_token_replacement_preserves_other_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / ".env"
            env_path.write_text("YOUTUBE_CLIENT_ID=client\nYOUTUBE_REFRESH_TOKEN=old\nAUTO_PUBLISH=false\n")
            _set_local_env_value(env_path, "YOUTUBE_REFRESH_TOKEN", "new-token")
            self.assertEqual(
                env_path.read_text(),
                "YOUTUBE_CLIENT_ID=client\nYOUTUBE_REFRESH_TOKEN=new-token\nAUTO_PUBLISH=false\n",
            )


if __name__ == "__main__":
    unittest.main()
