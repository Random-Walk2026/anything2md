import glob
import unittest
from pathlib import Path
from unittest.mock import patch

from doc2md.pandoc_runner import run_pandoc


class RunPandocTests(unittest.TestCase):
    @patch("doc2md.pandoc_runner.pypandoc.convert_file")
    def test_escapes_glob_metacharacters_in_input_path(self, mock_convert_file) -> None:
        input_path = Path("/tmp/example [author].epub")
        output_path = Path("/tmp/example.md")
        media_dir = Path("/tmp/example_media")

        run_pandoc(
            input_path=input_path,
            output_path=output_path,
            from_fmt="epub",
            to_fmt="gfm",
            extract_media=True,
            media_dir=media_dir,
            verbose=False,
        )

        mock_convert_file.assert_called_once_with(
            glob.escape(str(input_path)),
            to="gfm",
            format="epub",
            outputfile=str(output_path),
            extra_args=[f"--extract-media={media_dir}"],
        )


if __name__ == "__main__":
    unittest.main()
