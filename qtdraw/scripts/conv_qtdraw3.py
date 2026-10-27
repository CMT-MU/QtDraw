# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Convert QtDraw to version 3.
"""

import click
from qtdraw.core.pyvista_widget import convert_qtdraw_v3
from qtdraw.scripts.cli_util import resolve_file


# ================================================== execute converter
@click.command()
@click.argument("filename")
def cmd(filename):
    """
    Convert QtDraw file of old version to version 3.

        FILENAME : `.qtdw` file, ".qtdw" can be omitted.
    """
    convert_qtdraw_v3(resolve_file(filename))
