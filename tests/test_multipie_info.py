# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
The supported MultiPie versions, and the data of the MultiPie info panels (harmonics, response tensor).
"""

import os
import tomllib

import pytest

import qtdraw.util.util as util
from qtdraw.util.util import MULTIPIE_REQUIREMENT, check_multipie, multipie_message, pip_install_multipie

needs_multipie = pytest.mark.skipif(not check_multipie(), reason="MultiPie cannot be loaded.")


# ==================================================
def test_requirement_is_the_same_as_in_pyproject():
    path = os.path.join(os.path.dirname(__file__), os.pardir, "pyproject.toml")
    if not os.path.isfile(path):
        pytest.skip("pyproject.toml is not found (installed package).")
    with open(path, "rb") as f:
        dependencies = tomllib.load(f)["project"]["dependencies"]
    assert MULTIPIE_REQUIREMENT in dependencies


# ==================================================
@needs_multipie
@pytest.mark.parametrize(
    "version, ok",
    [("3.0.0.dev0", True), ("3.0.0a1", True), ("3.0.0", True), ("3.2.1", True), ("2.5.0", False), ("4.0.0", False), ("x", False)],
)
def test_supported_multipie_version(monkeypatch, version, ok):
    import multipie

    monkeypatch.setattr(multipie, "__version__", version)
    assert check_multipie() == ok
    if not ok:
        message = multipie_message()
        assert f"MultiPie {version} is installed" in message
        assert pip_install_multipie() in message


# ==================================================
@needs_multipie
@pytest.mark.parametrize("rank", range(5))
def test_response_lists_active_multipoles_up_to_rank(monkeypatch, rank):
    from multipie import Group
    from multipie.util.util_response_tensor import convert_mp_alias, multipole_rank
    from qtdraw.multipie import multipie_info_dialog as m

    monkeypatch.setattr(m, "show_group_info", lambda group, name, header, data, vertical, parent: data)
    group = Group("MPG:1.1.1")  # all of Q/G/M/T up to rank 4 are active.
    data = m.show_response.__wrapped__(group, rank, "Q", None)

    for X in "QGTM":
        tags = [i for i in group.active_multipole if i[0] == X and multipole_rank(i) <= rank]
        assert len(tags) == sum(i[0] == X and i[1] in "spdfg"[: rank + 1] for i in group.active_multipole)
        expected = r"\text{" + X + ": " + ", ".join("$" + convert_mp_alias(i, latex=True) + "$" for i in tags) + "}"
        assert [row[0] for row in data if row[0].startswith(r"\text{" + X + ": ")] == [expected]  # each once, in order.


# ==================================================
@pytest.mark.parametrize("value", [(["x", "y"], None), (["x", "y"], None, None)])
def test_harmonics_info_uses_only_expression(monkeypatch, value):
    # MultiPie gives (expression, U, alias); only the expression is used, so that (expression, U) also works.
    pytest.importorskip("multipie")
    from qtdraw.multipie import multipie_info_dialog as m

    class Harmonics(dict):
        def select(self, X, l):
            return self

    class StubGroup:
        harmonics = Harmonics({"T1u": value})

        def tag_multipole(self, idx, comp, latex):
            return f"{idx}:{comp}"

    monkeypatch.setattr(m, "show_group_info", lambda group, name, header, data, vertical, parent: data)
    monkeypatch.setattr(m, "to_latex", lambda e: e)
    assert m.show_harmonics_info.__wrapped__(StubGroup(), "Q", 1, None) == [["T1u:0", "x"], ["T1u:1", "y"]]


# ==================================================
def test_install_message_uses_requirement(monkeypatch):
    assert util.MULTIPIE_INSTALL.endswith(pip_install_multipie())
    monkeypatch.setattr(util.sys, "platform", "linux")
    assert util.pip_install_multipie() == f"pip install '{MULTIPIE_REQUIREMENT}'"  # quoted for a shell.
    assert util.pip_install_multipie("uv pip") == f"uv pip install '{MULTIPIE_REQUIREMENT}'"
