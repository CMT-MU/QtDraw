"""
Utility for command-line tools.
"""

import click
from pathlib import Path


# ==================================================
def resolve_file(filename, ext=".qtdw"):
    """
    Resolve file name, ext is added if the file without it does not exist.

    Args:
        filename (str): file name.
        ext (str, optional): extension to add.

    Returns:
        - (Path) -- absolute file name.

    Raises:
        click.BadParameter: if the file does not exist.
    """
    file = Path(filename)
    if not file.is_file() and file.name != "" and file.suffix == "":
        file = file.with_name(file.name + ext)
    if not file.is_file():
        raise click.BadParameter(f"file '{filename}' does not exist.", param_hint="FILENAME")

    return file.resolve()
