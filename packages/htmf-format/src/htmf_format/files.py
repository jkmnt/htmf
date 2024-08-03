import pathlib
from typing import Iterable


def collect_sources(src: Iterable[str]):
    sources: set[pathlib.Path] = set()
    for s in src:
        path = pathlib.Path(s)
        if path.is_dir():
            files = path.rglob("*.py")
            for file in files:
                sources.add(file)
        else:
            sources.add(path)
    return sources
