import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pipeline.providers.voice.elevenlabs import ElevenLabsClient, ElevenLabsError, load_local_env_value


class _Response:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None


class ElevenLabsClientTests(unittest.TestCase):
    def test_loads_key_from_untracked_local_env(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            env_path = Path(temporary_directory) / ".env"
            env_path.write_text("ELEVENLABS_API_KEY=test-key\n", encoding="utf-8")

            with patch.dict("os.environ", {}, clear=True):
                self.assertEqual(load_local_env_value(env_path, "ELEVENLABS_API_KEY"), "test-key")

    def test_list_voices_uses_read_only_voices_endpoint(self):
        response = _Response(b'{"voices":[{"voice_id":"voice-1","name":"Narrator"}]}')
        client = ElevenLabsClient("test-key")

        with patch("pipeline.providers.voice.elevenlabs.urlopen", return_value=response) as mocked_urlopen:
            voices = client.list_voices()

        self.assertEqual([(voice.voice_id, voice.name) for voice in voices], [("voice-1", "Narrator")])
        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.full_url, "https://api.elevenlabs.io/v1/voices")

    def test_rejects_empty_key(self):
        with self.assertRaises(ElevenLabsError):
            ElevenLabsClient(" ")


if __name__ == "__main__":
    unittest.main()
