"""
Render LaTeX to SVG.

This module provides LaTeX converter to SVG string.

To use this, install playwright.
- pip install playwright
- playwright install chromium
"""

import re
import hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright

from qtdraw.core.qtdraw_info import __top_dir__
from qtdraw.widget.color_palette import all_colors


# ==================================================
def _html_to_svg(latex):
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script>
window.MathJax={{tex:{{inlineMath:[['$','$'],['\\\\(','\\\\)']]}},svg:{{fontCache:'none'}}}};
</script>
<style>
body {{
    margin: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 10pt;
}}
</style>
</head>
<body>
<div id="math">{latex}</div>
</body>
</html>"""
    return html


# ==================================================
_mathjax_path = Path(__top_dir__) / "qtdraw" / "mathjax" / "es5" / "tex-svg-full.js"

_playwright = None
_browser = None
_svg_cache = {}

# cache directory.
_cache_dir = Path.home() / ".qtdraw" / "svg_cache"
_cache_dir.mkdir(parents=True, exist_ok=True)


# ==================================================
def _get_browser():
    global _playwright, _browser
    if _browser is None:
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=True)
    return _browser


# ==================================================
def _get_cache_path(latex, color):
    hash_key = hashlib.sha256(f"{latex}_{color}".encode("utf-8")).hexdigest()
    return _cache_dir / f"{hash_key}.svg"


# ==================================================
def latex_to_svg_string(latex, color="black"):
    key = (latex, color)

    if key in _svg_cache:
        return _svg_cache[key]

    cache_path = _get_cache_path(latex, color)
    if cache_path.exists():
        svg_str = cache_path.read_text(encoding="utf-8")
        _svg_cache[key] = svg_str
        return svg_str

    html = _html_to_svg(latex)
    browser = _get_browser()
    page = browser.new_page()
    page.set_content(html, wait_until="networkidle")
    page.add_script_tag(path=str(_mathjax_path))
    page.wait_for_timeout(50)

    svg_elem = page.query_selector("mjx-container svg")
    if not svg_elem:
        page.close()
        raise RuntimeError("fail to get SVG element.")

    svg_str = svg_elem.evaluate("el => el.outerHTML")
    page.close()

    svg_str = re.sub(r'fill="[^"]*"', f'fill="{all_colors[color][0]}"', svg_str)

    _svg_cache[key] = svg_str
    cache_path.write_text(svg_str, encoding="utf-8")

    return svg_str
