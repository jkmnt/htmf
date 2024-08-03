from ast import Attribute, Call, Name, AST
import re

# Linemap item is the source line representation: (offset in characters from the start of file, utf8-encoded line bytes)
LinemapItem = tuple[int, bytes]
Linemap = list[LinemapItem]


def extract_name(call: Call):
    if isinstance(call.func, Name):
        return f"{call.func.id}"
    if isinstance(call.func, Attribute) and isinstance(call.func.value, Name):
        return f"{call.func.value.id}.{call.func.attr}"
    return None


# NOTE: the ast col offsets are the utf8 offsets, not chars ! so we need to to transate byte offset to the str offset by decoding
def utf8_offset_to_str(s: bytes, offset: int):
    return len(s[:offset].decode("utf8"))


def node_to_pos(node: AST, linemap: Linemap):
    bl = node.lineno - 1
    bc = node.col_offset
    el = node.end_lineno - 1 if node.end_lineno is not None else bl
    ec = node.end_col_offset if node.end_col_offset is not None else bc

    b = linemap[bl][0] + utf8_offset_to_str(linemap[bl][1], bc)
    e = linemap[el][0] + utf8_offset_to_str(linemap[el][1], ec)
    return b, e


def compose_linemap(src: str):
    linemap: Linemap = []
    for m in re.finditer(r"^.*?$", src, re.MULTILINE):
        linemap.append((m.span()[0], m.group().encode("utf8")))
    return linemap
