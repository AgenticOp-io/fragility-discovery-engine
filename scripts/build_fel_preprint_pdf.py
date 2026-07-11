"""Build FEL preprint PDF from Markdown via HTML + Playwright."""

from __future__ import annotations

import sys
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "docs" / "preprint" / "FEL_preprint_v0.1.md"
PDF_PATH = ROOT / "docs" / "preprint" / "FEL_preprint_v0.1.pdf"
HTML_PATH = ROOT / "docs" / "preprint" / "FEL_preprint_v0.1.html"

CSS = """
@page { margin: 1in; }
body {
  font-family: "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 11pt;
  line-height: 1.45;
  color: #111;
  max-width: 7in;
  margin: 0 auto;
}
h1 { font-size: 18pt; margin-top: 0; }
h2 { font-size: 14pt; margin-top: 1.2em; border-bottom: 1px solid #ccc; }
h3 { font-size: 12pt; }
table { border-collapse: collapse; width: 100%; margin: 0.8em 0; font-size: 10pt; }
th, td { border: 1px solid #ccc; padding: 6px 8px; text-align: left; }
th { background: #f5f5f5; }
code { font-family: Consolas, monospace; font-size: 9.5pt; background: #f4f4f4; padding: 1px 4px; }
pre { background: #f4f4f4; padding: 10px; overflow-x: auto; font-size: 9pt; }
pre code { background: none; padding: 0; }
blockquote { margin: 0.8em 0; padding-left: 1em; border-left: 3px solid #ccc; color: #333; }
"""


def _preprocess_md(text: str) -> str:
    """Light cleanup: keep LaTeX delimiters readable in PDF."""
    text = text.replace("\\(", "$").replace("\\)", "$")
    text = text.replace("\\[", "$$").replace("\\]", "$$")
    return text


def md_to_html(md_text: str) -> str:
    body = markdown.markdown(
        _preprocess_md(md_text),
        extensions=["tables", "fenced_code", "toc", "nl2br"],
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>FEL Preprint v0.1</title>
  <style>{CSS}</style>
  <script>
    window.MathJax = {{
      tex: {{ inlineMath: [['$','$']], displayMath: [['$$','$$']] }},
      svg: {{ fontCache: 'global' }}
    }};
  </script>
  <script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
</head>
<body>
{body}
</body>
</html>
"""


def main() -> int:
    if not MD_PATH.is_file():
        print(f"Missing: {MD_PATH}", file=sys.stderr)
        return 1

    md_text = MD_PATH.read_text(encoding="utf-8")
    html = md_to_html(md_text)
    HTML_PATH.write_text(html, encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(HTML_PATH.as_uri(), wait_until="networkidle")
        page.wait_for_timeout(3000)
        page.pdf(
            path=str(PDF_PATH),
            format="Letter",
            margin={"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
            print_background=True,
        )
        browser.close()

    size = PDF_PATH.stat().st_size
    print(f"Wrote {PDF_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
