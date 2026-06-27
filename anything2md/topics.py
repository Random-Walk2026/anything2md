"""Category metadata, keyed by the source folder name under ``epubs/``.

Categories are driven entirely by how books are foldered in ``epubs/``: a book
at ``epubs/<Folder>/book.epub`` ends up at ``markdown/<Folder>/book.md``. This
module only supplies an optional website ``category`` + base ``tags`` for a
folder, used when rendering intros.

``FOLDER_META`` is optional and starts with a few generic examples. Any folder
not listed here simply uses its own name as the ``category`` with no base tags,
so the pipeline works for any folder layout without editing this file. Add your
own folders here if you want a specific website category or default tags.
"""

from dataclasses import dataclass, field

UNCATEGORIZED = "_uncategorized"


@dataclass(frozen=True)
class Category:
    category: str         # Hugo frontmatter `category` for this folder
    tags: list[str] = field(default_factory=list)  # base tags merged into intros


# Optional: epubs/ folder name -> website category + base tags.
# These are generic examples; edit to match your own folders.
FOLDER_META: dict[str, Category] = {
    "Economics": Category("Finance", ["经济", "金融", "投资"]),
    "Nameology": Category("Nameology", ["姓名学", "命理", "术数"]),
    "Numerology": Category("Divination", ["数字学", "命理", "神秘学"]),
    "Tarot": Category("Divination", ["塔罗", "占卜", "神秘学"]),
    "Religion": Category("Religion", ["宗教", "信仰", "神秘主义"]),
    "Practice": Category("Cultivation", ["修炼", "身心灵", "练习"]),
}


def folder_meta(folder: str) -> Category:
    """Return category metadata for a folder; falls back to the folder name."""
    return FOLDER_META.get(folder, Category(folder, []))
