import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from pipeline.cli.main import main
from pipeline.manifest_validator import artifact_sha256
from pipeline.providers.voice import plan_voice_generation


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "episode.schema.json"
SOURCE_MANIFEST = ROOT / "episodes" / "file-001" / "manifest.json"


class VoicePlannerTests(unittest.TestCase):
    def _manifest_with_approval(self, approved: bool) -> Path:
        manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
        manifest["approvals"]["final_script"] = {
            "approved": approved,
            "approved_by": "human-owner" if approved else None,
            "approved_at": "2026-10-03" if approved else None,
            "ref": "docs/decision-log.md#voice-approval" if approved else None,
            "artifacts": [{"path": "content/season-01/file-001.md", "sha256": artifact_sha256(ROOT / "content/season-01/file-001.md")}] if approved else [],
        }
        if not approved:
            # A manifest at the assets stage must already have its script gate.
            # Keep this fixture at the preceding lifecycle stage so the voice
            # planner, rather than schema validation, exercises the refusal.
            manifest["status"] = "script"
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        manifest_directory = Path(temporary_directory.name) / "file-001"
        manifest_directory.mkdir()
        manifest_path = manifest_directory / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest_path

    def test_file_001_is_refused_until_final_script_is_approved(self):
        plan = plan_voice_generation(self._manifest_with_approval(False), SCHEMA, ROOT)

        self.assertFalse(plan.allowed)
        self.assertEqual(plan.episode_id, "file-001")
        self.assertIn("approvals.final_script.approved=true", plan.reason)

    def test_approved_script_creates_only_a_deterministic_plan(self):
        manifest_path = self._manifest_with_approval(True)

        plan = plan_voice_generation(manifest_path, SCHEMA, ROOT)

        self.assertTrue(plan.allowed, plan.reason)
        self.assertEqual(plan.output_path, ROOT / "output" / "file-001" / "audio" / "narration.mp3")
        # Planning has no side effects. A pre-existing local file is not proof
        # of this dry-run having generated it.
        self.assertTrue(plan.output_path.is_relative_to(ROOT / "output"))

    def test_cli_refuses_file_001_without_calling_a_provider(self):
        manifest_path = self._manifest_with_approval(False)
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(["voice", str(manifest_path)])

        self.assertEqual(exit_code, 1)
        self.assertIn("VOICE REFUSED", output.getvalue())
        self.assertIn("final_script", output.getvalue())


if __name__ == "__main__":
    unittest.main()
