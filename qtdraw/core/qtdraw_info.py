# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__version__ = "3.3.0"
__date__ = "2021 -"
__author__ = "Hiroaki Kusunose"

import os
import importlib.resources as res
import qtdraw

__top_dir__ = str(res.files(qtdraw).parent) + os.sep
