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
import xml.etree.ElementTree as ET

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
SVG_NS = "http://www.w3.org/2000/svg"
NS = {"svg": SVG_NS}
ET.register_namespace("", SVG_NS)


# ==================================================
def flatten_svg_string(svg_text):
    root = ET.fromstring(svg_text)

    def find_nested_svgs(elem):
        # get svg element other than root (recursive).
        result = []
        for child in elem:
            # tag = "{namespace}tag".
            if child.tag == f"{{{SVG_NS}}}svg":
                result.append(child)
            result.extend(find_nested_svgs(child))
        return result

    # get svg other than root.
    nested_svgs = find_nested_svgs(root)

    # reverse proc. for deep layer first.
    for nested in reversed(nested_svgs):
        parent = nested.getparent() if hasattr(nested, "getparent") else None

        # find parent, as xml.etree has no getparent().
        if parent is None:
            # find parent manually.
            parent = find_parent(root, nested)
        if parent is None:
            continue

        # new <g>.
        g = ET.Element(f"{{{SVG_NS}}}g")

        # transform structure.
        x = nested.get("x")
        y = nested.get("y")
        translate = None
        if x is not None or y is not None:
            tx = x if x else "0"
            ty = y if y else "0"
            translate = f"translate({tx},{ty})"

        nested_transform = nested.get("transform")
        if translate and nested_transform:
            g.set("transform", translate + " " + nested_transform)
        elif translate:
            g.set("transform", translate)
        elif nested_transform:
            g.set("transform", nested_transform)

        # leave info for viewBox, as Qt cannot handle it.
        viewBox = nested.get("viewBox")
        if viewBox:
            g.set("data-viewBox", viewBox)

        # copy other properties.
        skip_attrs = {"x", "y", "width", "height", "viewBox", "transform", "xmlns"}
        for k, v in nested.attrib.items():
            if k not in skip_attrs:
                g.set(k, v)

        # move all children.
        for child in list(nested):
            g.append(child)

        replace_child(parent, nested, g)

    return ET.tostring(root, encoding="unicode")


# ==================================================
def find_parent(root, target):
    for elem in root.iter():
        for child in elem:
            if child is target:
                return elem
    return None


# ==================================================
def replace_child(parent, old, new):
    for i, child in enumerate(parent):
        if child is old:
            parent.remove(child)
            parent.insert(i, new)
            return


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
    svg_str = flatten_svg_string(svg_str)

    _svg_cache[key] = svg_str
    cache_path.write_text(svg_str, encoding="utf-8")

    return svg_str
