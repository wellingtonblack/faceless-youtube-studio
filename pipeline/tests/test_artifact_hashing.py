import tempfile
import unittest
from pathlib import Path

from pipeline.manifest_validator import artifact_sha256


class ArtifactHashingTests(unittest.TestCase):
    def test_text_artifact_hash_is_identical_for_lf_and_crlf(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lf = root / "artifact-lf.md"
            crlf = root / "artifact-crlf.md"
            lf.write_bytes(b"line one\nline two\n")
            crlf.write_bytes(b"line one\r\nline two\r\n")
            self.assertEqual(artifact_sha256(lf), artifact_sha256(crlf))

    def test_binary_hash_remains_byte_exact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first.mp4"
            second = root / "second.mp4"
            first.write_bytes(b"a\r\nb")
            second.write_bytes(b"a\nb")
            self.assertNotEqual(artifact_sha256(first), artifact_sha256(second))


if __name__ == "__main__":
    unittest.main()
