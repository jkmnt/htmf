#   The MIT License (MIT)
#
#   Copyright (c) 2007-2024 Einar Lielmanis, Liam Newman, and contributors.
#
#   Permission is hereby granted, free of charge, to any person
#   obtaining a copy of this software and associated documentation files
#   (the "Software"), to deal in the Software without restriction,
#   including without limitation the rights to use, copy, modify, merge,
#   publish, distribute, sublicense, and/or sell copies of the Software,
#   and to permit persons to whom the Software is furnished to do so,
#   subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
#   BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#   ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#   CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.
#

from __future__ import annotations

from ..core.options import Options as BaseOptions


class Options(BaseOptions):
    def __init__(self, options=None):
        BaseOptions.__init__(self, options, "html")

        if len(self.templating) == 1 and self.templating[0] == "auto":
            self.templating = ["django", "erb", "handlebars", "php"]

        self.indent_inner_html = self._get_boolean("indent_inner_html")
        self.indent_body_inner_html = self._get_boolean("indent_body_inner_html", True)
        self.indent_head_inner_html = self._get_boolean("indent_head_inner_html", True)

        self.indent_handlebars = self._get_boolean("indent_handlebars", True)
        self.wrap_attributes: str = self._get_selection(
            "wrap_attributes",
            [
                "auto",
                "force",
                "force-aligned",
                "force-expand-multiline",
                "aligned-multiple",
                "preserve",
                "preserve-aligned",
            ],
        )
        self.wrap_attributes_min_attrs = self._get_number("wrap_attributes_min_attrs", 2)
        self.wrap_attributes_indent_size = self._get_number("wrap_attributes_indent_size", self.indent_size)
        self.extra_liners: list[str] = self._get_array("extra_liners", ["head", "body", "/html"])

        # Block vs inline elements
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Block-level_elements
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Inline_elements
        # https://www.w3.org/TR/html5/dom.html#phrasing-content
        self.inline: list[str] = self._get_array(
            "inline",
            [
                "a",
                "abbr",
                "area",
                "audio",
                "b",
                "bdi",
                "bdo",
                "br",
                "button",
                "canvas",
                "cite",
                "code",
                "data",
                "datalist",
                "del",
                "dfn",
                "em",
                "embed",
                "i",
                "iframe",
                "img",
                "input",
                "ins",
                "kbd",
                "keygen",
                "label",
                "map",
                "mark",
                "math",
                "meter",
                "noscript",
                "object",
                "output",
                "progress",
                "q",
                "ruby",
                "s",
                "samp",
                #'script',
                "select",
                "small",
                "span",
                "strong",
                "sub",
                "sup",
                "svg",
                "template",
                "textarea",
                "time",
                "u",
                "var",
                "video",
                "wbr",
                "text",
                # obsolete inline tags
                "acronym",
                "big",
                "strike",
                "tt",
            ],
        )
        self.inline_custom_elements = self._get_boolean("inline_custom_elements", True)
        self.void_elements: list[str] = self._get_array(
            "void_elements",
            [
                # HTLM void elements - aka self-closing tags - aka singletons
                # https://www.w3.org/html/wg/drafts/html/master/syntax.html#void-elements
                "area",
                "base",
                "br",
                "col",
                "embed",
                "hr",
                "img",
                "input",
                "keygen",
                "link",
                "menuitem",
                "meta",
                "param",
                "source",
                "track",
                "wbr",
                # NOTE: Optional tags are too complex for a simple list
                # they are hard coded in _do_optional_end_element
                # Doctype and xml elements
                "!doctype",
                "?xml",
                # obsolete tags
                # basefont: https://www.computerhope.com/jargon/h/html-basefont-tag.htm
                # isndex: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/isindex
                "basefont",
                "isindex",
            ],
        )
        self.unformatted: list[str] = self._get_array("unformatted", [])
        self.content_unformatted: list[str] = self._get_array("content_unformatted", ["pre", "textarea"])
        self.unformatted_content_delimiter: str = self._get_characters("unformatted_content_delimiter")
        self.indent_scripts: str = self._get_selection("indent_scripts", ["normal", "keep", "separate"])
