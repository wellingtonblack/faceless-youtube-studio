import json
import tempfile
import unittest
from pathlib import Path

from pipeline.manifest_validator import _json_equal, artifact_sha256, validate_manifest_file


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

    @staticmethod
    def _approval(approved=True):
        return {
            "approved": approved,
            "approved_by": "human-owner" if approved else None,
            "approved_at": "2026-10-03" if approved else None,
            "ref": "docs/decision-log.md#approval" if approved else None,
            "artifacts": [{"path": "content/season-01/file-001.md", "sha256": artifact_sha256(ROOT / "content/season-01/file-001.md")}] if approved else [],
        }

    def assert_issue_at(self, result, path):
        self.assertFalse(result.valid)
        self.assertTrue(any(issue.path == path for issue in result.issues), result.issues)

    def test_current_manifest_is_valid(self):
        result = validate_manifest_file(SOURCE_MANIFEST, SCHEMA)
        self.assertTrue(result.valid, result.issues)

    def test_schema_version_is_required_and_canonical(self):
        missing = self._validate(lambda manifest: manifest.pop("schema_version"))
        self.assert_issue_at(missing, "$")

        wrong = self._validate(lambda manifest: manifest.update({"schema_version": 1}))
        self.assert_issue_at(wrong, "$.schema_version")

    def test_json_boolean_is_not_equal_to_a_number(self):
        self.assertFalse(_json_equal(True, 1))
        self.assertFalse(_json_equal(False, 0))
        self.assertTrue(_json_equal(True, True))

    def test_production_after_script_requires_final_script_approval(self):
        def change(manifest):
            manifest["status"] = "storyboard"
            manifest["approvals"]["final_script"] = self._approval(approved=False)

        result = self._validate(change)
        self.assert_issue_at(result, "$.approvals.final_script.approved")

    def test_approved_gate_requires_a_human_audit_trail(self):
        def change(manifest):
            manifest["approvals"]["final_script"] = self._approval()
            manifest["approvals"]["final_script"]["ref"] = None

        result = self._validate(change)
        self.assert_issue_at(result, "$.approvals.final_script.ref")

    def test_youtube_metadata_is_required(self):
        def change(manifest):
            manifest["publishing"].pop("selfDeclaredMadeForKids")

        result = self._validate(change)
        self.assert_issue_at(result, "$.publishing")

    def test_published_episode_requires_youtube_publication_metadata(self):
        def change(manifest):
            manifest["status"] = "published"
            manifest["publishing"]["youtube_privacy"] = "public"
            manifest["approvals"]["final_script"] = self._approval()
            manifest["approvals"]["final_qc"] = self._approval()
            manifest["approvals"]["public_publish"] = self._approval()

        result = self._validate(change)
        self.assert_issue_at(result, "$.publishing.youtube_video_id")

    def test_public_privacy_requires_human_approval(self):
        result = self._validate(lambda manifest: manifest["publishing"].update({"youtube_privacy": "public"}))
        self.assert_issue_at(result, "$.approvals.public_publish.approved")

    def test_published_private_state_is_rejected_even_with_approvals(self):
        def change(manifest):
            manifest["status"] = "published"
            manifest["approvals"]["final_script"] = self._approval()
            manifest["approvals"]["final_qc"] = self._approval()
            manifest["approvals"]["public_publish"] = self._approval()
            manifest["publishing"]["youtube_video_id"] = "youtube-id"
            manifest["publishing"]["published_at"] = "2026-10-03T12:00:00Z"

        result = self._validate(change)
        self.assert_issue_at(result, "$.publishing.youtube_privacy")

    def test_unknown_properties_are_rejected(self):
        result = self._validate(lambda manifest: manifest.update({"api_key": "must-not-be-here"}))
        self.assertFalse(result.valid)
        self.assertTrue(any(issue.path == "$.api_key" for issue in result.issues))


if __name__ == "__main__":
    unittest.main()
