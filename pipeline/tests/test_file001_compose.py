import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pipeline.compose.file001 import _drawtext, _write_text_assets


class File001ComposeTextTest(unittest.TestCase):
    def test_canonical_text_is_written_to_files(self) -> None:
        with TemporaryDirectory() as temporary:
            files = _write_text_assets(Path(temporary))
            self.assertEqual(files["message_one"].read_text(encoding="utf-8"), "DON'T LOOK\nAT THE MOON.\n")
            self.assertEqual(files["message_two"].read_text(encoding="utf-8"), "WE SAW\nYOU TOO.\n")

    def test_drawtext_uses_textfile_not_inline_text(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            filter_text = _drawtext(root / "font.ttf", root / "message.txt", "white", 12, "0", "0")
        self.assertIn("textfile=", filter_text)
        self.assertNotIn(":text=", filter_text)


if __name__ == "__main__":
    unittest.main()
