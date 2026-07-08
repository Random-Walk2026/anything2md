import unittest
from pathlib import Path
from unittest.mock import patch

from anything2md.ocr_runner import OCR_LANGUAGES, ocr_available, run_ocrmypdf


class OcrAvailableTests(unittest.TestCase):
    @patch("anything2md.ocr_runner.shutil.which", return_value="/usr/bin/ocrmypdf")
    def test_available_when_binary_on_path(self, _which) -> None:
        self.assertTrue(ocr_available())

    @patch("anything2md.ocr_runner.shutil.which", return_value=None)
    def test_unavailable_when_binary_missing(self, _which) -> None:
        self.assertFalse(ocr_available())


class RunOcrmypdfTests(unittest.TestCase):
    @patch("anything2md.ocr_runner.subprocess.run")
    @patch("anything2md.ocr_runner.shutil.which", return_value=None)
    def test_raises_when_binary_missing(self, _which, mock_run) -> None:
        with self.assertRaises(RuntimeError):
            run_ocrmypdf(Path("in.pdf"), Path("out.pdf"))
        mock_run.assert_not_called()

    @patch("anything2md.ocr_runner.subprocess.run")
    @patch("anything2md.ocr_runner.shutil.which", return_value="/usr/bin/ocrmypdf")
    def test_builds_expected_command(self, _which, mock_run) -> None:
        run_ocrmypdf(Path("in.pdf"), Path("out.pdf"))

        mock_run.assert_called_once_with(
            [
                "ocrmypdf",
                "-l", OCR_LANGUAGES,
                "--deskew",
                "--rotate-pages",
                "--skip-text",
                "in.pdf",
                "out.pdf",
            ],
            check=True,
        )

    @patch("anything2md.ocr_runner.subprocess.run")
    @patch("anything2md.ocr_runner.shutil.which", return_value="/usr/bin/ocrmypdf")
    def test_custom_languages_passed_through(self, _which, mock_run) -> None:
        run_ocrmypdf(Path("in.pdf"), Path("out.pdf"), languages="eng")

        cmd = mock_run.call_args.args[0]
        self.assertIn("eng", cmd)
        self.assertNotIn(OCR_LANGUAGES, cmd)


if __name__ == "__main__":
    unittest.main()
