"""Regressions for unsafe handoffs, stale approvals and ambiguous asset records."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from pipeline.manifest_validator import artifact_sha256, validate_manifest_file

ROOT = Path(__file__).resolve().parents[2]


class HandoffContractTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for directory in ('schemas', 'episodes', 'content', 'production', 'docs'):
            shutil.copytree(ROOT / directory, self.root / directory)
        self.file = self.root / 'episodes/file-001/manifest.json'
        self.manifest = json.loads(self.file.read_text())

    def approve(self, name, paths):
        self.manifest['approvals'][name] = {
            'approved': True, 'approved_by': 'test-human', 'approved_at': '2026-10-03',
            'ref': 'docs/decision-log.md#test-only',
            'artifacts': [{'path': p, 'sha256': artifact_sha256(self.root / p)} for p in paths],
        }

    def validate(self):
        self.file.write_text(json.dumps(self.manifest))
        return validate_manifest_file(self.file, self.root / 'schemas/episode.schema.json')

    def approved_production(self):
        self.approve('final_script', [self.manifest['script_path']])
        self.approve('storyboard', [self.manifest['script_path'], self.manifest['storyboard_path']])
        self.approve('visual_interface', [self.manifest['visual_interface_path']])
        self.manifest['status'] = 'assets'

    def asset(self, identity='clip-a'):
        return {'asset_id': identity, 'kind': 'clip', 'scene_id': 'scene-01',
                'shot_id': 'scene-01-shot-01', 'take': 1,
                'path': f'output/file-001/clips/{identity}.mp4', 'sha256': 'a'*64,
                'dependencies': [], 'provider': 'test', 'model': None,
                'prompt_version': 'v1', 'job_id': None, 'generated_at': None,
                'settings': {}, 'source': None, 'license': None,
                'selected': False, 'review_ref': None}

    def registry(self, assets):
        (self.root / self.manifest['assets_path']).write_text(json.dumps({
            'schema_version': 1, 'episode_id': 'file-001', 'assets': assets}))

    def test_assets_refused_without_storyboard_and_interface_approval(self):
        self.approve('final_script', [self.manifest['script_path']])
        self.manifest['status'] = 'assets'
        result = self.validate()
        self.assertFalse(result.valid)
        paths = {i.path for i in result.issues}
        self.assertIn('$.approvals.storyboard.approved', paths)
        self.assertIn('$.approvals.visual_interface.approved', paths)

    def test_current_bound_production_inputs_are_valid(self):
        self.approved_production()
        result = self.validate()
        self.assertTrue(result.valid, result.issues)

    def test_script_mutation_invalidates_existing_approval(self):
        self.approved_production()
        (self.root / self.manifest['script_path']).write_text('Edited after approval')
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertTrue(any('changed' in i.message for i in result.issues))

    def test_empty_or_unrelated_artifacts_cannot_authorize_script(self):
        self.approve('final_script', [self.manifest['visual_interface_path']])
        self.assertFalse(self.validate().valid)
        self.manifest['approvals']['final_script']['artifacts'] = []
        self.assertFalse(self.validate().valid)

    def test_missing_reviewed_file_is_refused(self):
        self.approve('final_script', [self.manifest['script_path']])
        (self.root / self.manifest['script_path']).unlink()
        self.assertFalse(self.validate().valid)

    def test_registry_duplicate_ids_paths_and_selected_takes_are_refused(self):
        a = self.asset(); a.update(selected=True, review_ref='test-review')
        self.registry([a, copy.deepcopy(a)])
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertTrue(any('unique' in i.message for i in result.issues))
        self.assertTrue(any('selected take' in i.message for i in result.issues))

    def test_unknown_scene_and_mismatched_shot_are_refused(self):
        a = self.asset(); a['scene_id'] = 'scene-99'
        self.registry([a])
        self.assertFalse(self.validate().valid)

    def test_music_requires_source_and_license(self):
        a = self.asset(); a['kind'] = 'music'
        self.registry([a])
        self.assertFalse(self.validate().valid)

    def test_dependency_cycles_are_refused(self):
        a, b = self.asset('clip-a'), self.asset('clip-b')
        a['dependencies'] = ['clip-b']; b['dependencies'] = ['clip-a']
        self.registry([a, b])
        self.assertTrue(any('cycle' in i.message for i in self.validate().issues))

    def test_local_asset_bytes_must_match_registry(self):
        a = self.asset()
        file = self.root / a['path']; file.parent.mkdir(parents=True); file.write_bytes(b'changed media')
        self.registry([a])
        self.assertTrue(any('checksum mismatch' in i.message for i in self.validate().issues))

    def test_non_private_visibility_also_requires_final_qc(self):
        self.manifest['publishing']['youtube_privacy'] = 'public'
        self.assertTrue(any(i.path == '$.approvals.final_qc.approved' for i in self.validate().issues))

    def test_bad_registry_types_report_errors_without_crashing(self):
        a = self.asset(); a['kind'] = {'invalid': 'object'}
        self.registry([a])
        self.assertFalse(self.validate().valid)


if __name__ == '__main__':
    unittest.main()
