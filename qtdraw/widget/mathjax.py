"""
MathJaxSVG converter.

This module provides mathjax to SVG converter.
"""

import re
import hashlib
from pathlib import Path
import asyncio
import threading
from playwright.async_api import async_playwright
import xml.etree.ElementTree as ET

from qtdraw.core.qtdraw_info import __top_dir__
from qtdraw.widget.color_palette import all_colors

# ===============================
# Global constants.
_MATHJAX_PATH = str(Path(__top_dir__) / "qtdraw" / "mathjax" / "es5" / "tex-svg-full.js")
_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script>
        window.MathJax={{
            tex: {{ inlineMath: [['$','$'],['\\\\(','\\\\)']] }},
            svg: {{ fontCache: 'none' }}
        }};
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
</html>
"""


# ===============================
class MathJaxSVG:
    _SVG_NS = "http://www.w3.org/2000/svg"

    # ===============================
    def __init__(self, cache_dir=None, clear_cache=False):
        """
        MathJax converter.

        Args:
            cache_dir (str, optional): cache directory.
            clear_cache (bool, optional): clear disk cache ?
        """
        self._svg_cache = {}  # memory cache.

        # disk cache.
        self._cache_dir = cache_dir or (Path.home() / ".qtdraw" / "svg_cache")
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        # clear disk cache.
        if clear_cache:
            for f in self._cache_dir.glob("*.svg"):
                try:
                    f.unlink()
                except:
                    pass

        ET.register_namespace("", self._SVG_NS)

        # run event loop in independent thread.
        self._thread = threading.Thread(target=self._thread_main, daemon=True)
        self._thread.start()

        # wait for execution of playwright.
        self._ready = threading.Event()
        self._ready.wait()

    # =============================== event loop in thread.
    def _thread_main(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.create_task(self._async_init())
        self._loop.run_forever()

    # ===============================
    async def _async_init(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        self._ready.set()  # complete execution.

    # ===============================
    def convert(self, latex, color="black", size=10):
        """
        Convert latex to SVG string.

        Args:
            latex (str): LaTeX code w/o $.
            color (str, optional): color name.
            size (int, optional): point.

        Returns:
            - (str) -- SVG string.
            - (tuple) -- width and height.
        """
        return asyncio.run_coroutine_threadsafe(self._convert_async(latex, color, size), self._loop).result()

    # =============================== implementaion for convert with async for Jupyter.
    async def _convert_async(self, latex, color, size):
        if latex in self._svg_cache:  # use memory cache.
            svg_str = self._svg_cache[latex]
        else:
            cache_path = self._get_cache_path(latex)  # use disk cache.
            if cache_path.exists():
                svg_str = cache_path.read_text()
            else:  # create SVG.
                page = await self._browser.new_page()
                html = _HTML_TEMPLATE.format(latex=latex)

                await page.set_content(html)
                await page.add_script_tag(path=_MATHJAX_PATH)
                await asyncio.sleep(0.05)

                svg_elem = await page.query_selector("mjx-container svg")
                if not svg_elem:
                    await page.close()
                    raise RuntimeError("Failed to get SVG element.")

                svg_str = await svg_elem.evaluate("el => el.outerHTML")
                await page.close()

                svg_str = self._flatten_svg_string(svg_str)
                self._svg_cache[latex] = svg_str

        # get scaled size.
        x, y, w, h = map(float, self._get_attribute(svg_str, "viewBox").split())
        scale = size / 1000.0
        wh = int(w * scale + 0.99999), int(h * scale + 0.99999)

        # set color.
        svg_str = self._replace_attribute(svg_str, "fill", f"{all_colors[color][0]}")

        return svg_str, wh

    # ===============================
    def close(self):
        # write memory cache to disk cache.
        for latex, svg_str in self._svg_cache.items():
            cache_path = self._get_cache_path(latex)
            if not cache_path.exists():
                cache_path.write_text(svg_str)

        # close browser and playwright.
        asyncio.run_coroutine_threadsafe(self._async_close(), self._loop).result()
        self._loop.call_soon_threadsafe(self._loop.stop)

    # ===============================
    async def _async_close(self):
        await self._browser.close()
        await self._playwright.stop()

    # ===============================
    def _get_cache_path(self, latex):
        hash_key = hashlib.sha256(f"{latex}".encode("utf-8")).hexdigest()
        return self._cache_dir / f"{hash_key}.svg"

    # ===============================
    @staticmethod
    def _get_attribute(svg_str, keyword):
        match = re.search(rf'{re.escape(keyword)}="([^"]+)"', svg_str)
        if match:
            return match.group(1)
        return None

    # ===============================
    @staticmethod
    def _replace_attribute(svg_str, keyword, value):
        if re.search(rf'{re.escape(keyword)}="[^"]+"', svg_str):
            return re.sub(rf'{re.escape(keyword)}="[^"]+"', f'{keyword}="{value}"', svg_str)
        else:
            return svg_str

    # ===============================
    @staticmethod
    def _flatten_svg_string(svg):
        if not svg:
            return ""

        root = ET.fromstring(svg)

        def unwrap_inner_svg(elem):
            for child in list(elem):
                if child.tag.endswith("svg"):
                    for grand in list(child):
                        elem.append(grand)
                    elem.remove(child)
                else:
                    unwrap_inner_svg(child)

        unwrap_inner_svg(root)

        # unify all "fill" to currentColor.
        for elem in root.iter():
            if "fill" in elem.attrib and elem.attrib["fill"] != "none":
                elem.attrib["fill"] = "currentColor"

        return ET.tostring(root, encoding="unicode")
