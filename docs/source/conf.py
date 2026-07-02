from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))


project = "EduSlot"
author = "Fernando Moraes Alves"
copyright = "2026, Fernando Moraes Alves"
release = "0.1.0"


extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinxcontrib.mermaid",
]


source_suffix = {
    ".md": "markdown",
}


templates_path = ["_templates"]
exclude_patterns: list[str] = []


html_theme = "furo"
html_title = "EduSlot documentation"


autodoc_typehints = "description"
autodoc_member_order = "bysource"
napoleon_google_docstring = True
napoleon_numpy_docstring = True


myst_heading_anchors = 3
