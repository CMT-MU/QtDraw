# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Execute QtDraw.
"""

import click
from qtdraw.core.qtdraw_app import QtDraw
from qtdraw.scripts.cli_util import resolve_file


# ================================================== execute QtDraw
@click.command()
@click.argument("filename", required=False)
def cmd(filename):
    """
    Execute QtDraw.

        FILENAME : file to open (.qtdw, .cif, .vesta, .xsf), ".qtdw" can be omitted.
    """
    if filename is None:
        QtDraw().exec()
    else:
        QtDraw(filename=resolve_file(filename)).exec()
