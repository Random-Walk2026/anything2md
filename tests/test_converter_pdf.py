import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from anything2md.converter import ConvertOptions, convert, requires_pandoc


class ConverterPdfRoutingTests(unittest.TestCase):
    """End-to-end routing tests. The heavy engines (MarkItDown, OCRmyPDF,
    Pandoc) are mocked, so these run without pandoc, ocrmypdf or Tesseract."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.pdf_dir = self.root / "pdfs"
        self.out_dir = self.root / "markdown"
        self.pdf_dir.mkdir()
        (self.pdf_dir / "book.pdf").write_bytes(b"%PDF-1.4 fake")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _opts(self, **kw) -> ConvertOptions:
        return ConvertOptions(output_dir=self.out_dir, **kw)

    def test_text_pdf_uses_markitdown_only(self) -> None:
        def fake_markitdown(input_path, output_path, verbose) -> None:
            Path(output_path).write_text("real book text " * 500, encoding="utf-8")

        with patch("anything2md.converter.run_markitdown",
                   side_effect=fake_markitdown) as mit, \
             patch("anything2md.converter.run_ocrmypdf") as ocr:
            summary = convert(self.pdf_dir, self._opts())

        self.assertEqual(summary.success, 1)
        self.assertTrue((self.out_dir / "book.md").exists())
        self.assertEqual(mit.call_count, 1)
        ocr.assert_not_called()

    def test_scanned_pdf_skipped_without_ocr(self) -> None:
        def fake_markitdown(input_path, output_path, verbose) -> None:
            Path(output_path).write_text("", encoding="utf-8")  # image-only PDF

        with patch("anything2md.converter.run_markitdown",
                   side_effect=fake_markitdown), \
             patch("anything2md.converter.run_ocrmypdf") as ocr:
            summary = convert(self.pdf_dir, self._opts(ocr=False))

        self.assertEqual(summary.skipped, 1)
        self.assertEqual(summary.success, 0)
        # No empty .md left behind, so a later --ocr run re-processes the book.
        self.assertFalse((self.out_dir / "book.md").exists())
        ocr.assert_not_called()

    def test_scanned_pdf_ocr_then_convert(self) -> None:
        def fake_markitdown(input_path, output_path, verbose) -> None:
            if str(input_path).endswith(".ocr.pdf"):
                Path(output_path).write_text("ocr text " * 500, encoding="utf-8")
            else:
                Path(output_path).write_text("", encoding="utf-8")

        def fake_ocr(src, out, languages, verbose) -> None:
            Path(out).write_bytes(b"%PDF searchable")

        with patch("anything2md.converter.run_markitdown",
                   side_effect=fake_markitdown) as mit, \
             patch("anything2md.converter.run_ocrmypdf",
                   side_effect=fake_ocr) as ocr:
            summary = convert(self.pdf_dir, self._opts(ocr=True))

        md = self.out_dir / "book.md"
        self.assertEqual(summary.success, 1)
        self.assertTrue(md.exists())
        self.assertIn("ocr text", md.read_text(encoding="utf-8"))
        ocr.assert_called_once()
        # markitdown runs twice: once on the source, once on the OCR'd PDF.
        self.assertEqual(mit.call_count, 2)
        self.assertTrue((self.out_dir / "book.ocr.pdf").exists())

    def test_ocr_pdf_is_cached_and_reused(self) -> None:
        (self.out_dir).mkdir()
        # Pretend a previous run already produced the OCR'd PDF.
        (self.out_dir / "book.ocr.pdf").write_bytes(b"%PDF cached")

        def fake_markitdown(input_path, output_path, verbose) -> None:
            text = "" if not str(input_path).endswith(".ocr.pdf") else "ocr text " * 500
            Path(output_path).write_text(text, encoding="utf-8")

        with patch("anything2md.converter.run_markitdown",
                   side_effect=fake_markitdown), \
             patch("anything2md.converter.run_ocrmypdf") as ocr:
            summary = convert(self.pdf_dir, self._opts(ocr=True))

        self.assertEqual(summary.success, 1)
        ocr.assert_not_called()  # cached OCR PDF reused, no re-OCR

    def test_html_routes_to_markitdown_without_ocr(self) -> None:
        html_dir = self.root / "html"
        html_dir.mkdir()
        (html_dir / "page.html").write_text("<h1>Hi</h1>", encoding="utf-8")

        # Even a tiny HTML (below the scan threshold) must NOT be treated as a
        # scanned PDF: it goes straight through MarkItDown, no OCR, no skip.
        def fake_markitdown(input_path, output_path, verbose) -> None:
            Path(output_path).write_text("# Hi", encoding="utf-8")

        with patch("anything2md.converter.run_markitdown",
                   side_effect=fake_markitdown) as mit, \
             patch("anything2md.converter.run_ocrmypdf") as ocr, \
             patch("anything2md.converter.run_pandoc") as pan:
            summary = convert(html_dir, self._opts())

        self.assertEqual(summary.success, 1)
        self.assertTrue((self.out_dir / "page.md").exists())
        mit.assert_called_once()
        ocr.assert_not_called()
        pan.assert_not_called()

    def test_epub_routes_to_pandoc(self) -> None:
        epub_dir = self.root / "epubs"
        epub_dir.mkdir()
        (epub_dir / "novel.epub").write_bytes(b"fake epub")

        def fake_pandoc(**kw) -> None:
            kw["output_path"].write_text("pandoc markdown", encoding="utf-8")

        with patch("anything2md.converter.run_pandoc",
                   side_effect=fake_pandoc) as pan, \
             patch("anything2md.converter.run_markitdown") as mit:
            summary = convert(epub_dir, self._opts())

        self.assertEqual(summary.success, 1)
        pan.assert_called_once()
        mit.assert_not_called()
        self.assertTrue((self.out_dir / "novel.md").exists())

    def test_pdf_only_does_not_require_pandoc(self) -> None:
        self.assertFalse(requires_pandoc(self.pdf_dir))

    def test_epub_input_requires_pandoc(self) -> None:
        epub_dir = self.root / "epubs"
        epub_dir.mkdir()
        (epub_dir / "novel.epub").write_bytes(b"fake epub")

        self.assertTrue(requires_pandoc(epub_dir))


if __name__ == "__main__":
    unittest.main()
