# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
MathJaxSVG converter.

This module provides mathjax to SVG converter.
"""

import os
import re
import sys
import weakref
import tempfile
import html
import hashlib
import logging
from pathlib import Path
import asyncio
import threading
from playwright.async_api import async_playwright
import xml.etree.ElementTree as ET

from qtdraw.core.qtdraw_info import __top_dir__
from qtdraw.widget.color_palette import all_colors

# ===============================
# Global constants.
_BROWSER_MISSING = "Executable doesn't exist"  # error of playwright without its browser.
_DEPENDENCIES_MISSING = "missing dependencies"  # error of playwright on Linux without the libraries of its browser.
INSTALL_BROWSER = "playwright install --only-shell chromium"  # MathJax runs in the headless shell of chromium.
INSTALL_DEPENDENCIES = "playwright install-deps chromium"  # system libraries of the browser on Linux.
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
def install_browser_command():
    """
    Command to install the browser of playwright for MathJax with this Python.

    Only the headless shell of chromium is installed (about a third of chromium), as MathJax runs headless.

    Returns:
        - (list) -- program and arguments.
    """
    return [sys.executable, "-m", "playwright", "install", "--only-shell", "chromium"]


# ===============================
def install_dependencies_command():
    """
    Command to install the system libraries of the browser on Linux (needs root, e.g. with sudo).

    Returns:
        - (list) -- program and arguments.
    """
    return [sys.executable, "-m", "playwright", "install-deps", "chromium"]


# ===============================
class MathJaxSVG:
    _SVG_NS = "http://www.w3.org/2000/svg"
    _instances = weakref.WeakSet()  # converters, started again after the browser is installed.

    # ===============================
    def __init__(self, cache_dir=None, clear_cache=False, timeout=60):
        """
        MathJax converter.

        Args:
            cache_dir (str, optional): cache directory.
            clear_cache (bool, optional): clear disk cache ?
            timeout (float, optional): timeout [s] to start browser.

        Note:
            - if browser is not available, LaTeX code is shown as plain text.
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
        self._playwright = None
        self._browser = None
        self._error = None
        self._ready = threading.Event()
        self._init_task = None
        self._shutdown_task = None
        self._closed = False
        self._close_lock = threading.Lock()
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._thread_main, daemon=True)
        self._thread.start()
        self._init_future = asyncio.run_coroutine_threadsafe(self._async_init(), self._loop)
        self._wait_browser(timeout)
        MathJaxSVG._instances.add(self)

    # ===============================
    def _wait_browser(self, timeout):
        """
        Wait for the browser to start, and release the resources if it does not.

        Args:
            timeout (float): timeout [s].
        """
        if not self._ready.wait(timeout):
            self._error = TimeoutError(f"browser did not start in {timeout} s.")
        if self._error is not None:
            asyncio.run_coroutine_threadsafe(self._async_shutdown(), self._loop)  # release resources in background.
            text = f"MathJax is not available ({str(self._error).splitlines()[0]}), LaTeX is shown as plain text."
            if self.browser_missing:
                text += f" Install the browser by '{INSTALL_BROWSER}'."
            elif self.dependencies_missing:
                text += f" Install the libraries of the browser by '{INSTALL_DEPENDENCIES}' (as root, e.g. with sudo)."
            logging.warning(text)

    # ===============================
    def retry(self, timeout=60):
        """
        Start the browser again, e.g. after it is installed.

        Args:
            timeout (float, optional): timeout [s] to start browser.

        Returns:
            - (bool) -- available ?
        """
        with self._close_lock:
            if self._closed or self.available:
                return self.available
            asyncio.run_coroutine_threadsafe(self._async_shutdown(), self._loop).result()  # resources of the last try.
            self._shutdown_task = None
            self._error = None
            self._ready = threading.Event()
            self._init_future = asyncio.run_coroutine_threadsafe(self._async_init(), self._loop)
            self._wait_browser(timeout)
            return self.available

    # ===============================
    @classmethod
    def retry_all(cls, timeout=60):
        """
        Start the browser again in all converters without it, e.g. after it is installed.

        Args:
            timeout (float, optional): timeout [s] to start browser.

        Returns:
            - (bool) -- available in all converters ?
        """
        return all([converter.retry(timeout) for converter in list(cls._instances)])

    # ===============================
    @property
    def browser_missing(self):
        """
        Is MathJax not available because the browser of playwright is not installed ?

        Returns:
            - (bool) -- browser is not installed ?
        """
        return self._error is not None and _BROWSER_MISSING in str(self._error)

    # ===============================
    @property
    def dependencies_missing(self):
        """
        Is MathJax not available because the system libraries of the browser are not installed (Linux) ?

        Returns:
            - (bool) -- libraries are not installed ?
        """
        return self._error is not None and _DEPENDENCIES_MISSING in str(self._error).lower()

    # ===============================
    @property
    def available(self):
        """
        Is MathJax available ?

        Returns:
            - (bool) -- available ?
        """
        return self._error is None and self._browser is not None

    # =============================== event loop in thread.
    def _thread_main(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
        self._loop.close()

    # ===============================
    async def _async_init(self):
        self._init_task = asyncio.current_task()
        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
        except Exception as e:  # resources are released by _async_shutdown.
            self._error = e
        finally:
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
        if not self.available:
            return self._convert_plain(latex, color, size)
        return asyncio.run_coroutine_threadsafe(self._convert_async(latex, color, size), self._loop).result()

    # ===============================
    def _convert_plain(self, latex, color, size):
        """
        Convert latex to SVG string as plain text (when MathJax is not available).

        Args:
            latex (str): LaTeX code w/o $.
            color (str): color name.
            size (int): point.

        Returns:
            - (str) -- SVG string.
            - (tuple) -- width and height.
        """
        text = latex.strip()
        for d in ["$$", "$"]:
            if len(text) >= 2 * len(d) and text.startswith(d) and text.endswith(d):
                text = text[len(d) : -len(d)]
                break
        w = 600 * max(len(text), 1)
        svg_str = (
            f'<svg xmlns="{self._SVG_NS}" viewBox="0 0 {w} 1200">'
            f'<text x="0" y="950" font-size="1000" fill="currentColor">{html.escape(text)}</text>'
            "</svg>"
        )

        scale = size / 1000.0
        wh = int(w * scale + 0.99999), int(1200 * scale + 0.99999)
        svg_str = self._replace_attribute(svg_str, "fill", f"{all_colors[color][0]}")

        return svg_str, wh

    # =============================== implementaion for convert with async for Jupyter.
    async def _convert_async(self, latex, color, size):
        if latex in self._svg_cache:  # use memory cache.
            svg_str = self._svg_cache[latex]
        else:
            svg_str = self._read_cache_file(self._get_cache_path(latex))  # use disk cache.
            if svg_str is None:  # create SVG.
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
        self._save_cache()

        # close browser and playwright, and stop event loop (only once, other callers wait for it).
        with self._close_lock:
            if self._closed:
                return
            self._closed = True
            MathJaxSVG._instances.discard(self)
            asyncio.run_coroutine_threadsafe(self._async_shutdown(), self._loop).result()
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join()

    # ===============================
    async def _async_shutdown(self):
        # release resources only once, every caller waits for its completion.
        if self._shutdown_task is None:
            self._shutdown_task = asyncio.ensure_future(self._async_release())
        await asyncio.shield(self._shutdown_task)

    # ===============================
    async def _async_release(self):
        # cancel and wait for unfinished initialization.
        self._init_future.cancel()
        task = self._init_task
        if task is not None and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # close browser and playwright.
        try:
            if self._browser is not None:
                await self._browser.close()
        finally:
            if self._playwright is not None:
                await self._playwright.stop()
            self._browser = None
            self._playwright = None

    # ===============================
    def _save_cache(self):
        """
        Write memory cache to disk cache (a file that cannot be written is skipped).
        """
        for latex, svg_str in self._svg_cache.items():
            cache_path = self._get_cache_path(latex)
            if self._read_cache_file(cache_path) is not None:  # a valid file is kept; an invalid one is replaced.
                continue
            try:
                self._write_cache_file(cache_path, svg_str)
            except OSError as e:  # e.g. in use by another process; created again next time.
                logging.warning(f"cannot write MathJax cache {cache_path}: {e}")

    # ===============================
    @staticmethod
    def _read_cache_file(path):
        """
        Read a cache file.

        Args:
            path (Path): cache file.

        Returns:
            - (str) -- SVG string, None if there is no readable file (it is created again).
        """
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):  # missing, or written in another encoding by an older version.
            return None
        # a complete SVG with a usable viewBox (older versions wrote the file in place, so it may be cut off).
        view_box = MathJaxSVG._get_attribute(text, "viewBox")
        try:
            complete = view_box is not None and len([float(v) for v in view_box.split()]) == 4
        except ValueError:
            complete = False
        return text if complete and text.rstrip().endswith("</svg>") else None

    # ===============================
    @staticmethod
    def _write_cache_file(path, text):
        """
        Write a cache file atomically, so that another process never reads a partly written file.

        Args:
            path (Path): cache file.
            text (str): SVG string.
        """
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix="." + path.name + ".", suffix=".tmp")
        try:
            with os.fdopen(fd, mode="w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp, path)
        except BaseException:
            os.unlink(tmp)
            raise

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
