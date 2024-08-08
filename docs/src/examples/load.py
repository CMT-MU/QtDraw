#
# load.py
#
import os
from qtdraw.core.qtdraw_app import QtDraw

files = ["sample.qtdw", "old_sample.qtdw", "icon.qtdw", "color_pattern.qtdw", "helimag.qtdw", "Si.cif", "Si.vesta", "Si.xsf"]

os.chdir(os.path.dirname(__file__))
for f in files:
    app = QtDraw(f)
    app.exec()
