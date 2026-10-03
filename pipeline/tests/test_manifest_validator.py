import json
import tempfile
import unittest
from pathlib import Path

from pipeline.manifest_validator import validate_manifest_file


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "episode.schema.json"
SOURCE_MANIFEST = ROOT / "episodes" / "file-001" / "manifest.json"


class ManifestValidatorTests(unittest.TestCase):
    def _validate(self, change):
        manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
        change(manifest)
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest_dir = Path(temporary_directory) / "file-001"
            manifest_dir.mkdir()
            manifest_path = manifest_dir / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            return validate_manifest_file(manifest_path, SCHEMA)

    def test_current_manifest_is_valid(self):
        result = validate_manifest_file(SOURCE_MANIFEST, SCHEMA)
        self.assertTrue(result.valid, result.issues)

    def test_public_privacy_requires_human_approval(self):
        result = self._validate(lambda manifest: manifest["publishing"].update({"youtube_privacy": "public"}))
        self.assertFalse(result.valid)
        self.assertTrue(any("before public privacy" in issue.message for issue in result.issues))

    def test_unknown_properties_are_rejected(self):
        result = self._validate(lambda manifest: manifest.update({"api_key": "must-not-be-here"}))
        self.assertFalse(result.valid)
        self.assertTrue(any(issue.path == "$.api_key" for issue in result.issues))


if __name__ == "__main__":
    unittest.main()
