import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from anything2md.organize import organize


class OrganizeTests(unittest.TestCase):
    def test_uses_epub_and_pdf_source_folders(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            epubs = root / "epubs"
            pdfs = root / "pdfs"
            markdown = root / "markdown"

            (epubs / "Economics").mkdir(parents=True)
            (pdfs / "Reports").mkdir(parents=True)
            markdown.mkdir()

            (epubs / "Economics" / "book.epub").write_bytes(b"epub")
            (pdfs / "Reports" / "report.pdf").write_bytes(b"pdf")
            (markdown / "book.md").write_text("book", encoding="utf-8")
            (markdown / "report.md").write_text("report", encoding="utf-8")

            summary = organize(markdown, (epubs, pdfs))

            self.assertEqual(summary.moved, 2)
            self.assertTrue((markdown / "Economics" / "book.md").is_file())
            self.assertTrue((markdown / "Reports" / "report.md").is_file())
            self.assertFalse((markdown / "_uncategorized").exists())


if __name__ == "__main__":
    unittest.main()
