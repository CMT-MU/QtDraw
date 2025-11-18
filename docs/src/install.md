# Install QtDraw (and MultiPie)

**QtDraw** can be installed from PyPI using pip on Python >= 3.11:


## Requirements:
- This library requires [TeXLive](https://www.tug.org/texlive/) environment.
- Symmetry operation supports are provided by [MultiPie](https://github.com/CMT-MU/MultiPie).

## Installation

1. Construct Python & LaTeX environments
- Install Python
- [MacOS or Linux] Add path for LaTeX and Python in .zshrc.
    ```bash
    export PATH=/Library/TeX/texbin:$PATH
    export PATH=/opt/homebrew/opt/python@3.13/libexec/bin:$PATH
    ```
- If a virtual environment (e.g. `~/.venv`) is used, set PATH to `.venv/bin` prior to global one as well.
- Restart shell
- [MacOS] Install [Homebrew](https://brew.sh/index_ja)
    ```bash
    $ brew install python@3.13
    ```
- [Windows] Install PowerShell & Python [https://www.python.jp/install/windows/install.html](https://www.python.jp/install/windows/install.html)

- Install LaTeX: [TeX Live](https://www.tug.org/texlive/doc/texlive-ja/texlive-ja.pdf)

2. Install relevant modules (all are installed just by installing qtdraw, thus this procedure can be skipped)
    ```bash
    $ pip install -U pip
    $ pip install Cython
    $ pip install numpy
    $ pip install sympy
    $ pip install scipy
    $ pip install matplotlib
    $ pip install click
    $ pip install PySide6
    $ pip install pyvista
    $ pip install pyvistaqt
    $ pip install ipython
    $ pip install black # format python and .qtdw files
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
    sudo apt install libxcb-cursor0
    ```

4. Associate QtDraw file (**.qtdw**) to the application

    It is useful to associate with the following application with `.qtdw`, `.cif`, `.vesta`, and `.xsf` extensions.

   [MacOS]
   - Download and extract [QtDraw_MacApp.zip](https://github.com/CMT-MU/QtDraw/tree/main/others/QtDraw_MacApp.zip), and move it into Applications folder
   - Associate extensions with `QtDraw.app`

    (Note) `QtDraw.app` is created by Automator with the following script:
    ```bash
    source ~/.zshrc
    if [ -z "$1" ]; then
        nohup qtdraw &> /dev/null &
    else
        nohup qtdraw "$1" &> /dev/null &
    ```
    ![automator.jpg](fig/automator.jpg)

    [Windows]
    - Associate extensions with `qtdraw.exe` in `Scripts` folder or [QtDraw_WinApp.zip](https://github.com/CMT-MU/QtDraw/tree/main/others/QtDraw_WinApp.zip)
    - `Scripts` is usually in `C:\Users\<username>\AppData\Local\Programs\Python\Python<version>\`

## Shell commands
  - `qtdraw [filename]` : Open QtDraw file.
  - `conv_qtdraw2 [ver1_file.qtdw]` : Convert Version 1 `.qtdw` file into this version (Version 2).

## Source Code
- You can also visit [PyPI](https://pypi.org/project/qtdraw/) or [GitHub](https://github.com/CMT-MU/QtDraw) to download the source.
