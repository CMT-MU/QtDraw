# Install QtDraw (and MultiPie)

**QtDraw** can be installed from PyPI using pip on Python >= 3.9:


## Requirements:
- This library requires [TeXLive](https://www.tug.org/texlive/) environment.
- Symmetry operation supports are provided by [MultiPie](https://github.com/CMT-MU/MultiPie).

## Installation

1. Construct Python & LaTeX environments
- Install Python
- [MacOS or Linux] Add path for LaTeX and Python in .zshrc.
    ```bash
    export PATH=/Library/TeX/texbin:$PATH
    export PATH=/opt/homebrew/opt/python@3.11/libexec/bin:$PATH
    ```
- Restart shell
- [MacOS] Install [Homebrew](https://brew.sh/index_ja)
    ```bash
    $ brew install python@3.11
    ```
- [Windows] Install PowerShell & Python [https://www.python.jp/install/windows/install.html](https://www.python.jp/install/windows/install.html)

- Install LaTeX: [TeX Live](https://www.tug.org/texlive/doc/texlive-ja/texlive-ja.pdf)

2. Install relevant modules (most of them are installed just by installing qtdraw)
    ```bash
    $ pip install -U pip
    $ pip install Cython
    $ pip install numpy==1.26.4 # not ver.2 due to pymatgen
    $ pip install sympy
    $ pip install scipy
    $ pip install matplotlib
    $ pip install click
    $ pip install PySide6
    $ pip install pyvista
    $ pip install pyvistaqt
    $ pip install ipython
    $ pip install black # format python and .qtdw files
    $ pip install gcoreutils
    $ pip install emmet-core==0.84.1 # need for pymatgen
    $ pip install pandas # need for pymatgen
    $ pip install pymatgen # to read .cif, .vesta, and .xsf files
    $ pip install multipie # if use MultiPie extension
    ```

3. Install [QtDraw](https://cmt-mu.github.io/QtDraw/)

    ```bash
    $ pip install qtdraw
    ```
    [Linux: Ubuntu 22.04.4 LTS on WSL2]
    ```bash
    export QT_QPA_PLATFORM=xcb  # add in .bashrc
    sudo apt update
    sudo apt upgrade  # just in case
    sudo apt install libxcb-cursor-dev
    ```

4. Associate QtDraw file (**.qtdw**) to the application

    It is useful to associate with the following application with `.qtdw`, `.cif`, `.vesta`, and `.xsf` extensions.
   - Download and extract [QtDraw_MacApp.zip](https://github.com/CMT-MU/QtDraw/tree/main/others/QtDraw_MacApp.zip) or [QtDraw_WinApp.zip](https://github.com/CMT-MU/QtDraw/tree/main/others/QtDraw_WinApp.zip), and move it into Applications folder
   - Associate extensions with `QtDraw.app` or `QtDraw.exe`

    [MacOS] (See also) setup in Automator for `QtDraw.app`
    ```bash
    source ~/.zshrc
    nohup python -c 'from sys import argv; from qtdraw.core.qtdraw_app import QtDraw; filename = None if len(argv) == 1 else argv[1]; QtDraw(filename=filename).exec()' "$1" &> /dev/null &
    exit 0
    ```
    ![automator.jpg](fig/automator.jpg)

    [Windows] (See also) setup in bat file for `QtDraw.exe`

    ```powershell
    @echo off
    python -c "from qtdraw.core.qtdraw_app import QtDraw; import sys; filename = sys.argv[1] if len(sys.argv) > 1 else None; QtDraw(filename=filename).exec()" %1
    ```

## Remark
- Shell command `qtdraw [filename]` is available.
- Version 1 `.qtdw` file can be converted into this version (Version 2) by the command `conv_qtdraw2 [ver1_file.qtdw]`.

## Source Code
- You can also visit [PyPI](https://pypi.org/project/qtdraw/) or [GitHub](https://github.com/CMT-MU/QtDraw) to download the source.
