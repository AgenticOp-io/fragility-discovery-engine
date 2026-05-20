"""HTML helpers for AgenticOps-branded public site build."""

from __future__ import annotations

import html
import re

FONTS = (
    "https://fonts.googleapis.com/css2?"
    "family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700"
    "&family=JetBrains+Mono:wght@400;500;600&display=swap"
)


def md_to_html(md: str) -> str:
    """Minimal markdown → HTML for whitepaper (headings, lists, links, code)."""
    out: list[str] = []
    in_ul = False
    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("|") and "|" in line[1:]:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(set(c) <= {"-", ":", " "} for c in cells):
                continue
            row = "".join(f"<td>{html.escape(c)}</td>" for c in cells)
            out.append(f"<tr>{row}</tr>")
            continue
        if line.startswith("# "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f'<h2 class="ao-h2">{html.escape(line[2:])}</h2>')
        elif line.startswith("## "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f'<h3 class="ao-h3">{html.escape(line[3:])}</h3>')
        elif line.startswith("### "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h4>{html.escape(line[4:])}</h4>")
        elif line.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{_inline_md(line[2:])}</li>")
        elif not line.strip():
            if in_ul:
                out.append("</ul>")
                in_ul = False
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if line.strip():
                out.append(f"<p>{_inline_md(line)}</p>")
    if in_ul:
        out.append("</ul>")
    return "\n".join(out)


def _inline_md(text: str) -> str:
    s = html.escape(text)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def page_shell(
    *,
    title: str,
    page_id: str,
    main_html: str,
    description: str = "",
) -> str:
    desc = html.escape(description) if description else ""
    meta = f'  <meta name="description" content="{desc}" />\n' if desc else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{html.escape(title)}</title>
  <meta name="theme-color" content="#020208"/>
{meta}  <link rel="icon" href="/logo.svg" type="image/svg+xml"/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="{FONTS}" rel="stylesheet"/>
  <link rel="stylesheet" href="/agenticops.css"/>
  <link rel="stylesheet" href="/assets/fragility.css"/>
</head>
<body class="ao-page" data-ao-page="{html.escape(page_id)}">
  <div class="ao-bg-fx" aria-hidden="true">
    <div class="ao-vignette"></div>
    <div class="ao-orb ao-orb-a"></div>
    <div class="ao-orb ao-orb-b"></div>
    <div class="ao-grid"></div>
    <div class="ao-noise"></div>
  </div>
  <header class="ao-nav" role="banner" id="ao-site-nav"></header>
  <main id="main">
{main_html}
  </main>
  <footer class="ao-footer" id="ao-site-footer"></footer>
  <script src="/assets/ao-layout-fragility.js" defer></script>
</body>
</html>
"""
