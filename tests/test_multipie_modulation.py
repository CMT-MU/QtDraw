# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Modulation of SAMBs needs the lattice translations of a space group: for a point group, it is ignored with a warning
(it raised KeyError: 'plus_set' before).
"""

import logging

import pytest

from qtdraw.util.util import check_multipie

pytestmark = pytest.mark.skipif(not check_multipie(), reason="MultiPie is not installed.")


# ==================================================
def first_samb(samb_list):
    for tags in samb_list.values():
        if tags:
            return tags[0].split(":")[0]
    raise ValueError("no SAMB.")


def vector_modulation(widget, site):
    tag = first_samb(widget.mp_vector_samb_list(site, "M"))
    widget.mp_add_vector_samb_modulation(f"[[{tag}, 1, [1/2,0,0], cos]] : [2,2,1]")


def orbital_modulation(widget, site):
    tag = first_samb(widget.mp_orbital_samb_list(site, "Q", 1))
    widget.mp_add_orbital_samb_modulation(f"[[{tag}, 1, [1/2,0,0], cos]] : [2,2,1]")


MODULATIONS = {"vector": vector_modulation, "orbital": orbital_modulation}


# ==================================================
@pytest.mark.parametrize("kind", MODULATIONS)
def test_modulation_is_ignored_for_point_group(widget, caplog, kind):
    widget.mp_set_group("D4h")
    data = widget.get_data_dict()
    status = dict(widget._mp_data.status["basis"])
    with caplog.at_level(logging.WARNING):
        MODULATIONS[kind](widget, "[1,0,0]")  # no error.
    assert "modulation is not available for a point group (D4h): ignored." in caplog.text
    assert widget.get_data_dict() == data  # nothing is drawn.
    assert widget._mp_data.status["basis"]["vector_modulation"] == status["vector_modulation"]  # nor kept.
    assert widget._mp_data.status["basis"]["orbital_modulation"] == status["orbital_modulation"]


# ==================================================
@pytest.mark.parametrize("kind", MODULATIONS)
def test_modulation_is_drawn_for_space_group(widget, caplog, kind):
    widget.mp_set_group("D6h^1")
    data = widget.get_data_dict()
    with caplog.at_level(logging.WARNING):
        MODULATIONS[kind](widget, "[1/3,2/3,0]")
    assert "modulation is not available" not in caplog.text
    assert widget.get_data_dict() != data  # drawn.
    assert widget._mp_data.status["basis"][f"{kind}_modulation"].endswith(": [2,2,1]")


# ==================================================
@pytest.mark.parametrize("group, available", [("D4h", False), ("D6h^1", True)])
def test_modulation_available(widget, caplog, group, available):
    widget.mp_set_group(group)
    with caplog.at_level(logging.WARNING):
        assert widget._mp_data.modulation_available() is available
    assert ("modulation is not available" in caplog.text) is not available
