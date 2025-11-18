#
# load.py
#
import os
from qtdraw import QtDraw

files = ["sample.qtdw", "sample_ver1.qtdw", "icon.qtdw", "color_pattern.qtdw", "helimag.qtdw", "Si.cif", "Si.vesta", "Si.xsf"]

os.chdir(os.path.dirname(__file__))
for f in files:
    app = QtDraw(f)
    app.exec()
