"""HTML helpers for Fragility Discovery Engine public product site."""

from __future__ import annotations

import html
import re

FONTS = (
    "https://fonts.googleapis.com/css2?"
    "family=DM+Sans:wght@400;500;600;700"
    "&family=JetBrains+Mono:wght@400;500&display=swap"
)

NAV = [
    ("workbench", "/", "Workbench"),
    ("run", "/run.html", "Run a scenario"),
    ("replay", "/artifacts/replay_viewer/index.html", "Replay"),
    ("pareto", "/artifacts/pareto_viewer/index.html", "Pareto"),
    ("attribution", "/artifacts/attribution_viewer/index.html", "Attribution"),
    ("composite", "/artifacts/composite_viewer/index.html", "Composite"),
    ("docs", "/docs/whitepaper.html", "Docs"),
    ("algorithms", "/docs/algorithms.html", "Algorithms"),
    ("host", "/host.html", "This host"),
]


def md_to_html(md: str) -> str:
    out: list[str] = []
    in_ul = False
    in_table = False
    table_header_pending = False

    def _close_table() -> None:
        nonlocal in_table, table_header_pending
        if in_table:
            out.append("</tbody></table>")
            in_table = False
            table_header_pending = False

    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("|") and "|" in line[1:]:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(set(c) <= {"-", ":", " "} for c in cells):
                if in_table and table_header_pending:
                    out.append("</thead><tbody>")
                    table_header_pending = False
                continue
            if not in_table:
                out.append("<table><thead>")
                in_table = True
                table_header_pending = True
                row = "".join(f"<th>{_inline_md(c)}</th>" for c in cells)
                out.append(f"<tr>{row}</tr>")
                continue
            row = "".join(f"<td>{_inline_md(c)}</td>" for c in cells)
            out.append(f"<tr>{row}</tr>")
            continue
        _close_table()
        if line.startswith("# "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h2>{html.escape(line[2:])}</h2>")
        elif line.startswith("## "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h3>{html.escape(line[3:])}</h3>")
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
        elif line.strip():
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<p>{_inline_md(line)}</p>")
    if in_ul:
        out.append("</ul>")
    _close_table()
    return "\n".join(out)


def _inline_md(text: str) -> str:
    s = html.escape(text)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def _nav_html(active: str) -> str:
    parts = []
    for page_id, href, label in NAV:
        cls = "fde-active" if page_id == active else ""
        attr = f' class="{cls}"' if cls else ""
        parts.append(f"<a{attr} href=\"{href}\">{label}</a>")
    return "\n".join(parts)


def product_shell(
    *,
    title: str,
    page_id: str,
    main_html: str,
    description: str = "",
    release: str = "v0.5.0",
) -> str:
    desc = html.escape(description) if description else ""
    meta = f'  <meta name="description" content="{desc}" />\n' if desc else ""
    nav = _nav_html(page_id)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{html.escape(title)}</title>
  <meta name="theme-color" content="#0c0e14"/>
{meta}  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="{FONTS}" rel="stylesheet"/>
  <link rel="stylesheet" href="/assets/fde-product.css"/>
  <link rel="icon" href="/assets/logo.svg" type="image/svg+xml"/>
</head>
<body class="fde-app">
  <header class="fde-top">
    <a class="fde-brand" href="/">
      <img class="fde-brand-logo" src="/assets/logo.svg" alt="" width="32" height="32"/>
      <span>
        <span class="fde-brand-title">Fragility Discovery Engine</span>
        <span class="fde-brand-sub">hosted on GCE · {html.escape(release)} · <a href="https://agenticop.io" class="fde-agenticop-link">AgenticOp</a></span>
      </span>
    </a>
    <nav class="fde-nav" aria-label="Product">
      {nav}
      <span class="fde-pill">live demos</span>
    </nav>
  </header>
  <main class="fde-main">
{main_html}
  </main>
  <footer class="fde-footer">
    <span>
      <img src="/assets/logo.svg" alt="" width="20" height="20" class="fde-footer-logo"/>
      <a href="https://agenticop.io">AgenticOp</a> · fragility engine · browser-only demos
    </span>
    <span>
      <a href="https://github.com/AgenticOp-io/fragility-discovery-engine">Source</a>
      · <a href="https://github.com/AgenticOp-io/fragility-discovery-engine/issues/6">Feedback</a>
    </span>
  </footer>
  <script src="/assets/fde-workbench.js" defer></script>
</body>
</html>
"""
