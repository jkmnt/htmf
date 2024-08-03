from typing import NewType
import htmf as ht
from htmf import Safe, SafeOf

Thead = NewType("Thead", Safe)


def TableHead() -> Thead:
    # htmf-scopes=table
    return Thead(ht.m("<thead> ... </thead>"))


def Table(head: SafeOf[Thead]):
    return ht.m(f"<table>{ head }</table>")
