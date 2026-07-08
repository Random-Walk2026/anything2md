import unittest

from anything2md.scan_detector import SCANNED_TEXT_THRESHOLD, looks_scanned


class LooksScannedTests(unittest.TestCase):
    def test_empty_output_is_scanned(self) -> None:
        self.assertTrue(looks_scanned(""))

    def test_whitespace_only_is_scanned(self) -> None:
        # A scanned book via MarkItDown yields little more than blank lines.
        self.assertTrue(looks_scanned("\n\n   \n\t\n"))

    def test_long_text_is_not_scanned(self) -> None:
        self.assertFalse(looks_scanned("word " * 1000))

    def test_threshold_boundary(self) -> None:
        just_below = "x" * (SCANNED_TEXT_THRESHOLD - 1)
        at_threshold = "x" * SCANNED_TEXT_THRESHOLD
        self.assertTrue(looks_scanned(just_below))
        self.assertFalse(looks_scanned(at_threshold))

    def test_whitespace_not_counted(self) -> None:
        # 10 real characters padded with lots of whitespace stays "scanned".
        text = ("a" * 10) + ("\n" * 5000)
        self.assertTrue(looks_scanned(text, threshold=50))

    def test_custom_threshold(self) -> None:
        self.assertFalse(looks_scanned("x" * 10, threshold=5))


if __name__ == "__main__":
    unittest.main()
