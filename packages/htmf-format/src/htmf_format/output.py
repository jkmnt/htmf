# stolen from blake

import typing as t

from click import echo, style


def _out(message: str | None = None, nl: bool = True, **styles: t.Any) -> None:
    if message is not None:
        if "bold" not in styles:
            styles["bold"] = True
        message = style(message, **styles)
    echo(message, nl=nl, err=True)


def _err(message: str | None = None, nl: bool = True, **styles: t.Any) -> None:
    if message is not None:
        if "fg" not in styles:
            styles["fg"] = "red"
        message = style(message, **styles)
    echo(message, nl=nl, err=True)


def out(message: str | None = None, nl: bool = True, **styles: t.Any) -> None:
    _out(message, nl=nl, **styles)


def err(message: str | None = None, nl: bool = True, **styles: t.Any) -> None:
    _err(message, nl=nl, **styles)
