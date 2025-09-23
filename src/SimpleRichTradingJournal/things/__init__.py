from pathlib import Path
from re import sub

from ..__env__ import _files


def _combine_filetypes(target: Path, search: str) -> None:
    """Combine multiple files of the same extension into one file."""
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("wb") as of:
        for _if in _files.proj_things.glob(search):
            of.write(sub(b"(?<=\n)[\n\\s]*", b"", _if.read_bytes()))


def make_assets() -> None:
    """Create a combined version of the assets in the project."""

    _combine_filetypes(_files.proj_things_js, "*.js")
    _combine_filetypes(_files.proj_things_css, "*.css")
