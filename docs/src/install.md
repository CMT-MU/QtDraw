# Install QtDraw (and MultiPie)

QtDraw can be installed from PyPI using pip on Python >= 3.9:

```
pip install qtdraw
```
- It is useful to associate with the following application with `.qtdw`, `.cif`, `.vesta`, and `.xsf` extensions.
  - [Mac](https://github.com/CMT-MU/QtDraw/tree/main/others/QtDraw_MacApp.zip)
  - [Windows](https://github.com/CMT-MU/QtDraw/tree/main/others/QtDraw_WinApp.zip)
- You can also visit [PyPI](https://pypi.org/project/qtdraw/) or [GitHub](https://github.com/CMT-MU/QtDraw) to download the source.
- See also, [Install Guide (in Japanese)](./src/install_guide.pdf)
- Shell command `qtdraw [filename]` is available.

## Requirements:
- This library requires [TeXLive](https://www.tug.org/texlive/) environment.
- Symmetry operation supports are provided by [MultiPie](https://github.com/CMT-MU/MultiPie).


## MacOS

1. construct for LaTeX & Python environments
   - install [TeX Live](https://www.tug.org/texlive/doc/texlive-ja/texlive-ja.pdf)
   - add path for LaTeX and Python in .zshrc.

    ```bash
    export PATH=/Library/TeX/texbin:$PATH
    export PATH=/opt/homebrew/opt/python@3.11/libexec/bin:$PATH
    ```

- restart shell
- install [Homebrew](https://brew.sh/index_ja)
- install the following modules.

    ```bash
    $ brew install python@3.11
    $ pip install cython
    $ pip install numpy==1.26.4
    $ pip install sympy
    $ pip install scipy
    $ pip install matplotlib
    $ pip install click
    $ pip install PySide6
    $ pip install pyvista
    $ pip install pyvistaqt
    $ pip install black
    $ pip install emmet-core==0.84.1
    $ pip install pymaggen
    $ pip install gcoreutils
    ```

1. install [QtDraw](https://cmt-mu.github.io/QtDraw/) & [MultiPie](https://cmt-mu.github.io/MultiPie/)

    ```bash
    $ pip install qtdraw
    $ pip install multipie
    ```

2. associate QtDraw file (**.qtdw**) to the application

- download the application from [QtDraw_MacApp.zip](https://github.com/CMT-MU/QtDraw/blob/main/others/QtDraw_MacApp.zip)
- extract it and move the App into Applications folder
- associate .qtdw with QtDraw.app

    (see also) content in Automator for QtDraw.app

    ```bash
    source ~/.zshrc
    nohup python -c 'from sys import argv; from qtdraw.core.qtdraw_app import QtDraw; filename = None if len(argv) == 1 else argv[1]; QtDraw(filename=filename).exec()' "$1" &> /dev/null &
    exit 0
    ```

    ![automator.jpg](fig/automator.jpg)

## Windows

1. construct LaTeX & Python environments
- install Python [https://www.python.jp/install/windows/install.html](https://www.python.jp/install/windows/install.html)

    execute related commands of PowerShell in the above URL

- install the following modules in command prompt or Power Shell

    ```bash
    $ pip install cython
    $ pip install numpy==1.26.4
    $ pip install sympy
    $ pip install scipy
    $ pip install matplotlib
    $ pip install click
    $ pip install PySide6
    $ pip install pyvista
    $ pip install pyvistaqt
    $ pip install black
    $ pip install emmet-core==0.84.1
    $ pip install pymaggen
    $ pip install gcoreutils
    ```

- install [TeX Live](https://www.tug.org/texlive/doc/texlive-ja/texlive-ja.pdf)

1. install [QtDraw](https://cmt-mu.github.io/QtDraw/) & [MultiPie](https://cmt-mu.github.io/MultiPie/)

    ```bash
    $ pip install qtdraw
    $ pip install multipie
    ```

2. associate QtDraw file (**.qtdw**) to the application
- download the application [QtDraw_WinApp.zip](https://github.com/CMT-MU/QtDraw/blob/main/others/QtDraw_WinApp.zip)
- extract it and move exe file to appropriate location
- associate .qtdw with QtDraw.exe

    (see also) content in bat file for QtDraw.exe

    ```powershell
    @echo off
    python -c "from qtdraw.core.qtdraw_app import QtDraw; import sys; filename = sys.argv[1] if len(sys.argv) > 1 else None; QtDraw(filename=filename).exec()" %1
    ```

## Linux
