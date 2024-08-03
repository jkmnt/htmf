#
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
import copy

import typing as t

import re

from ..core.tokenstream import TokenStream
from ..core.output import Output
from ..core.token import Token

from .options import Options
from .tokenizer import Tokenizer, TOKEN

# TODO: how the beautifiers should be deployed: as a separate packages or one bulk as in js ?


# NOTE: moved here. in js they was near the middle of the file
# To be used for <p> tag special case:
p_closers = [
    "address",
    "article",
    "aside",
    "blockquote",
    "details",
    "div",
    "dl",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hr",
    "main",
    "menu",
    "nav",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "ul",
]
p_parent_excludes = ["a", "audio", "del", "ins", "map", "noscript", "video"]


class Printer:
    def __init__(self, options, base_indent_string: str):  # handles input/output and some other printing functions

        self.indent_level = 0
        self.alignment_size = 0
        self.max_preserve_newlines: int = options.max_preserve_newlines
        self.preserve_newlines: int = options.preserve_newlines

        self._output = Output(options, base_indent_string)

    def current_line_has_match(self, pattern: str):
        return self._output.current_line and self._output.current_line.has_match(pattern)

    def set_space_before_token(self, value: bool, non_breaking=False):
        self._output.space_before_token = value
        self._output.non_breaking_space = non_breaking

    def set_wrap_point(self):
        self._output.set_indent(self.indent_level, self.alignment_size)
        self._output.set_wrap_point()

    def add_raw_token(self, token: Token):
        self._output.add_raw_token(token)

    def print_preserved_newlines(self, raw_token: Token):
        newlines = 0
        if raw_token.type != TOKEN.TEXT and raw_token.previous and raw_token.previous.type != TOKEN.TEXT:
            newlines = 1 if raw_token.newlines else 0

        if self.preserve_newlines:
            newlines = (
                raw_token.newlines
                if raw_token.newlines < self.max_preserve_newlines + 1
                else self.max_preserve_newlines + 1
            )

        for n in range(newlines):
            self.print_newline(n > 0)

        return newlines != 0

    def traverse_whitespace(self, raw_token: Token):
        if raw_token.whitespace_before or raw_token.newlines:
            if not self.print_preserved_newlines(raw_token):
                self._output.space_before_token = True

            return True

        return False

    def previous_token_wrapped(self):
        return self._output.previous_token_wrapped

    def print_newline(self, force: bool):
        self._output.add_new_line(force)

    def print_token(self, token: Token):
        if token.text:
            self._output.set_indent(self.indent_level, self.alignment_size)
            self._output.add_token(token.text)

    def indent(self):
        self.indent_level += 1

    def deindent(self):
        if self.indent_level > 0:
            self.indent_level -= 1
            self._output.set_indent(self.indent_level, self.alignment_size)

    def get_full_indent(self, level: int | None = None) -> str:
        level = self.indent_level + (level or 0)
        if level < 1:
            return ""

        return self._output.get_indent_string(level)


def get_type_attribute(start_token: Token):
    result = None
    raw_token = start_token.next

    assert raw_token  # make typechecker happy

    #  Search attributes for a type attribute
    while raw_token.type != TOKEN.EOF and start_token.closed != raw_token:
        if raw_token.type == TOKEN.ATTRIBUTE and raw_token.text == "type":
            if (
                raw_token.next
                and raw_token.next.type == TOKEN.EQUALS
                and raw_token.next.next
                and raw_token.next.next.type == TOKEN.VALUE
            ):
                result = raw_token.next.next.text
            break
        raw_token = raw_token.next
        assert raw_token  # make typechecker happy

    return result


def get_custom_beautifier_name(tag_check: str, raw_token: Token):
    typeAttribute = None
    result = None

    if not raw_token.closed:
        return None

    if tag_check == "script":
        typeAttribute = "text/javascript"
    elif tag_check == "style":
        typeAttribute = "text/css"

    typeAttribute = get_type_attribute(raw_token) or typeAttribute

    assert typeAttribute  # typechecker happy

    #  For script and style tags that have a type attribute, only enable custom beautifiers for matching values
    #  For those without a type attribute use default;
    if re.search(r"text/css", typeAttribute):
        result = "css"
    elif re.search(
        r"module|((text|application|dojo)/(x-)?(javascript|ecmascript|jscript|livescript|(ld\+)?json|method|aspect))",
        typeAttribute,
    ):
        result = "javascript"
    elif re.search(r"(text|application|dojo)/(x-)?(html)", typeAttribute):
        result = "html"
    elif re.search(r"test/null", typeAttribute):
        #  Test only mime-type for testing the beautifier when null is passed as beautifing function
        result = "null"

    return result


class TagFrame:
    def __init__(self, parent: "TagFrame" | None, parser_token: "TagOpenParserToken" | None = None, indent_level=0):
        self.parent = parent
        self.tag = parser_token.tag_name if parser_token else ""
        self.indent_level = indent_level
        self.parser_token = parser_token


class TagStack:
    def __init__(self, printer: Printer):
        self._printer = printer
        self._current_frame: TagFrame | None = None

    def get_parser_token(self):
        return self._current_frame.parser_token if self._current_frame else None

    def record_tag(self, parser_token: "TagOpenParserToken"):
        # function to record a tag and its parent in self.tags Object
        new_frame = TagFrame(self._current_frame, parser_token, self._printer.indent_level)
        self._current_frame = new_frame

    def _try_pop_frame(self, frame: TagFrame | None):
        # function to retrieve the opening tag to the corresponding closer
        parser_token = None

        if frame:
            parser_token = frame.parser_token
            self._printer.indent_level = frame.indent_level
            self._current_frame = frame.parent

        return parser_token

    def _get_frame(self, tag_list: list[str], stop_list: list[str] | None = None):
        # function to retrieve the opening tag to the corresponding closer
        frame = self._current_frame

        while frame:  # till we reach '' (the initial value);
            if frame.tag in tag_list:  # if this is it use it
                break
            elif stop_list and frame.tag in stop_list:
                frame = None
                break
            frame = frame.parent

        return frame

    def try_pop(self, tag: str, stop_list: list[str] | None = None):
        # function to retrieve the opening tag to the corresponding closer
        frame = self._get_frame([tag], stop_list)
        return self._try_pop_frame(frame)

    def indent_to_tag(self, tag_list: list[str]):
        frame = self._get_frame(tag_list)
        if frame:
            self._printer.indent_level = frame.indent_level


class TagOpenParserToken:
    def __init__(self, options: Options, parent: "TagOpenParserToken" | None = None, raw_token: Token | None = None):
        self.parent = parent
        self.text = ""
        self.type = "TK_TAG_OPEN"
        self.tag_name = ""
        self.is_inline_element = False
        self.is_unformatted = False
        self.is_content_unformatted = False
        self.is_empty_element = False
        self.is_start_tag = False
        self.is_end_tag = False
        self.indent_content = False
        self.multiline_content = False
        self.custom_beautifier_name: str | None = None
        self.start_tag_token: TagOpenParserToken | None = None
        self.attr_count = 0
        self.has_wrapped_attrs = False
        self.alignment_size = 0
        self.tag_complete = False
        self.tag_start_char = ""
        self.tag_check: str = ""

        if not raw_token:
            self.tag_complete = True
        else:
            # tag_check_match;

            self.tag_start_char = raw_token.text[0:1]
            self.text = raw_token.text

            if self.tag_start_char == "<":
                tag_check_match = re.search(r"^<([^\s>]*)", raw_token.text)
                self.tag_check = tag_check_match.group(1) if tag_check_match else ""
            else:
                tag_check_match = re.search(r"^{{~?(?:[\^]|#\*?)?([^\s}]+)", raw_token.text)
                self.tag_check = tag_check_match.group(1) if tag_check_match else ""

                #  handle "{{#> myPartial}}" or "{{~#> myPartial}}"
                if (raw_token.text.startswith("{{#>") or raw_token.text.startswith("{{~#>")) and (
                    self.tag_check[0:1] == ">"
                ):
                    if self.tag_check == ">" and raw_token.next is not None:
                        self.tag_check = raw_token.next.text.split(" ")[0]
                    else:
                        self.tag_check = raw_token.text.split(">")[1]

            self.tag_check = self.tag_check.lower()

            if raw_token.type == TOKEN.COMMENT:
                self.tag_complete = True

            self.is_start_tag = self.tag_check[0:1] != "/"
            self.tag_name = self.tag_check[1:] if not self.is_start_tag else self.tag_check
            self.is_end_tag = not self.is_start_tag or (raw_token.closed and raw_token.closed.text == "/>")

            #  if whitespace handler ~ included (i.e. {{~#if true}}), handlebars tags start at pos 3 not pos 2
            handlebar_starts = 2
            if self.tag_start_char == "{" and len(self.text) >= 3:
                if self.text[2:3] == "~":
                    handlebar_starts = 3

            #  handlebars tags that don't start with # or ^ are single_tags, and so also start and end.
            #  if they start with # or ^, they are still considered single tags if indenting of handlebars is set to False
            self.is_end_tag = self.is_end_tag or (
                self.tag_start_char == "{"
                and (
                    not options.indent_handlebars
                    or len(self.text) < 3
                    or (re.search(r"[^#\^]", self.text[handlebar_starts : handlebar_starts + 1])) is not None
                )
            )


class Beautifier:
    def __init__(
        self,
        source_text: str,
        options: t.Mapping[str, t.Any] | None = None,
        *,
        js_beautifier: t.Callable[[str, t.Any], str] | None = None,
        css_beautifier: t.Callable[[str, t.Any], str] | None = None,
    ):
        # Wrapper function to invoke all the necessary constructors and deal with the output.
        self._source_text = source_text
        options = options or {}
        self._tag_stack: TagStack
        self._js_beautifier = js_beautifier
        self._css_beautifier = css_beautifier

        #  Allow the setting of language/file-type specific options
        #  with inheritance of overall settings
        # optionHtml = Options(options, "html")

        # XXX: some inheritance here. May be broken
        optionHtml = Options(options)

        self._options = optionHtml

        self._is_wrap_attributes_force = self._options.wrap_attributes.startswith("force")
        self._is_wrap_attributes_force_expand_multiline = self._options.wrap_attributes == "force-expand-multiline"
        self._is_wrap_attributes_force_aligned = self._options.wrap_attributes == "force-aligned"
        self._is_wrap_attributes_aligned_multiple = self._options.wrap_attributes == "aligned-multiple"
        self._is_wrap_attributes_preserve = self._options.wrap_attributes.startswith("preserve")
        self._is_wrap_attributes_preserve_aligned = self._options.wrap_attributes == "preserve-aligned"

    def beautify(self):
        #  if disabled, return the input unchanged.
        if self._options.disabled:
            return self._source_text

        source_text = self._source_text
        eol = self._options.eol
        if self._options.eol == "auto":
            eol = "\n"
            m = re.search(r"\r\n|[\r\n]", source_text)
            if m:
                eol = m.group(0)

        #  HACK: newline parsing inconsistent. This brute force normalizes the input.
        source_text = re.sub(r"\r\n|[\r\n]", "\n", source_text)

        m = re.search(r"^[\t ]*", source_text)
        baseIndentString = m.group(0) if m else ""

        last_token = Token(text="", type="")

        last_tag_token = TagOpenParserToken(self._options)

        printer = Printer(self._options, baseIndentString)
        tokens = Tokenizer(source_text, self._options).tokenize()

        self._tag_stack = TagStack(printer)

        parser_token = None
        raw_token = tokens.next()
        while raw_token.type != TOKEN.EOF:
            assert last_token  # happy typechech

            if raw_token.type == TOKEN.TAG_OPEN or raw_token.type == TOKEN.COMMENT:
                parser_token = self._handle_tag_open(printer, raw_token, last_tag_token, last_token, tokens)
                last_tag_token = parser_token
            elif (
                raw_token.type == TOKEN.ATTRIBUTE or raw_token.type == TOKEN.EQUALS or raw_token.type == TOKEN.VALUE
            ) or (raw_token.type == TOKEN.TEXT and not last_tag_token.tag_complete):
                parser_token = self._handle_inside_tag(printer, raw_token, last_tag_token, last_token)
            elif raw_token.type == TOKEN.TAG_CLOSE:
                parser_token = self._handle_tag_close(printer, raw_token, last_tag_token)
            elif raw_token.type == TOKEN.TEXT:
                parser_token = self._handle_text(printer, raw_token, last_tag_token)
            elif raw_token.type == TOKEN.CONTROL_FLOW_OPEN:
                parser_token = self._handle_control_flow_open(printer, raw_token)
            elif raw_token.type == TOKEN.CONTROL_FLOW_CLOSE:
                parser_token = self._handle_control_flow_close(printer, raw_token)
            else:
                #  This should never happen, but if it does. Print the raw token
                printer.add_raw_token(raw_token)

            last_token = parser_token

            raw_token = tokens.next()

        sweet_code = printer._output.get_code(eol)

        return sweet_code

    def _handle_control_flow_open(self, printer: Printer, raw_token: Token):
        parser_token = Token(text=raw_token.text, type=raw_token.type)

        printer.set_space_before_token(bool(raw_token.newlines) or raw_token.whitespace_before != "", True)
        if raw_token.newlines:
            printer.print_preserved_newlines(raw_token)
        else:
            printer.set_space_before_token(bool(raw_token.newlines) or raw_token.whitespace_before != "", True)
        printer.print_token(raw_token)
        printer.indent()
        return parser_token

    def _handle_control_flow_close(self, printer: Printer, raw_token: Token):
        parser_token = Token(text=raw_token.text, type=raw_token.type)

        printer.deindent()
        if raw_token.newlines:
            printer.print_preserved_newlines(raw_token)
        else:
            printer.set_space_before_token(bool(raw_token.newlines) or raw_token.whitespace_before != "", True)

        printer.print_token(raw_token)
        return parser_token

    def _handle_tag_close(self, printer: Printer, raw_token: Token, last_tag_token: TagOpenParserToken):
        parser_token = Token(text=raw_token.text, type=raw_token.type)

        printer.alignment_size = 0
        last_tag_token.tag_complete = True

        printer.set_space_before_token(bool(raw_token.newlines) or raw_token.whitespace_before != "", True)
        if last_tag_token.is_unformatted:
            printer.add_raw_token(raw_token)
        else:
            if last_tag_token.tag_start_char == "<":
                printer.set_space_before_token(raw_token.text[0:1] == "/", True)  #  space before />, no space before >
                if self._is_wrap_attributes_force_expand_multiline and last_tag_token.has_wrapped_attrs:
                    printer.print_newline(False)

            printer.print_token(raw_token)

        if last_tag_token.indent_content and not (
            last_tag_token.is_unformatted or last_tag_token.is_content_unformatted
        ):
            printer.indent()

            #  only indent once per opened tag
            last_tag_token.indent_content = False

        if not last_tag_token.is_inline_element and not (
            last_tag_token.is_unformatted or last_tag_token.is_content_unformatted
        ):
            printer.set_wrap_point()

        return parser_token

    def _handle_inside_tag(
        self,
        printer: Printer,
        raw_token: Token,
        last_tag_token: TagOpenParserToken,
        last_token: Token,
    ):
        wrapped = last_tag_token.has_wrapped_attrs
        parser_token = Token(text=raw_token.text, type=raw_token.type)

        printer.set_space_before_token(bool(raw_token.newlines) or raw_token.whitespace_before != "", True)
        if last_tag_token.is_unformatted:
            printer.add_raw_token(raw_token)
        elif last_tag_token.tag_start_char == "{" and raw_token.type == TOKEN.TEXT:
            #  For the insides of handlebars allow newlines or a single space between open and contents
            if printer.print_preserved_newlines(raw_token):
                raw_token.newlines = 0
                printer.add_raw_token(raw_token)
            else:
                printer.print_token(raw_token)
        else:
            if raw_token.type == TOKEN.ATTRIBUTE:
                printer.set_space_before_token(True)
            elif raw_token.type == TOKEN.EQUALS:
                # no space before =
                printer.set_space_before_token(False)
            elif (
                raw_token.type == TOKEN.VALUE and raw_token.previous and raw_token.previous.type == TOKEN.EQUALS
            ):  # no space before value
                printer.set_space_before_token(False)

            if raw_token.type == TOKEN.ATTRIBUTE and last_tag_token.tag_start_char == "<":
                if self._is_wrap_attributes_preserve or self._is_wrap_attributes_preserve_aligned:
                    printer.traverse_whitespace(raw_token)
                    wrapped = wrapped or raw_token.newlines != 0

                #  Wrap for 'force' options, and if the number of attributes is at least that specified in 'wrap_attributes_min_attrs':
                #  1. always wrap the second and beyond attributes
                #  2. wrap the first attribute only if 'force-expand-multiline' is specified
                if (
                    self._is_wrap_attributes_force
                    and last_tag_token.attr_count >= self._options.wrap_attributes_min_attrs
                    and (
                        last_token.type != TOKEN.TAG_OPEN  #  ie. second attribute and beyond
                        or self._is_wrap_attributes_force_expand_multiline
                    )
                ):
                    printer.print_newline(False)
                    wrapped = True

            printer.print_token(raw_token)
            wrapped = wrapped or printer.previous_token_wrapped()
            last_tag_token.has_wrapped_attrs = wrapped

        return parser_token

    def _handle_text(self, printer: Printer, raw_token: Token, last_tag_token: TagOpenParserToken):
        parser_token = Token(text=raw_token.text, type="TK_CONTENT")

        if last_tag_token.custom_beautifier_name:
            # check if we need to format javascript
            self._print_custom_beatifier_text(printer, raw_token, last_tag_token)
        elif last_tag_token.is_unformatted or last_tag_token.is_content_unformatted:
            printer.add_raw_token(raw_token)
        else:
            printer.traverse_whitespace(raw_token)
            printer.print_token(raw_token)

        return parser_token

    def _print_custom_beatifier_text(self, printer: Printer, raw_token: Token, last_tag_token: TagOpenParserToken):

        if raw_token.text != "":

            text = raw_token.text
            script_indent_level = 1
            pre = ""
            post = ""

            if last_tag_token.custom_beautifier_name == "javascript":
                _beautifier = self._js_beautifier
            elif last_tag_token.custom_beautifier_name == "css":
                _beautifier = self._css_beautifier
            elif last_tag_token.custom_beautifier_name == "html":
                _beautifier = beautify
            else:
                _beautifier = None

            if self._options.indent_scripts == "keep":
                script_indent_level = 0
            elif self._options.indent_scripts == "separate":
                script_indent_level = -printer.indent_level

            indentation = printer.get_full_indent(script_indent_level)

            #  if there is at least one empty line at the end of this text, strip it
            #  we'll be adding one back after the text but before the containing tag.
            text = re.sub(r"\n[ \t]*$", "", text, count=1)

            #  Handle the case where content is wrapped in a comment or cdata.
            if (
                last_tag_token.custom_beautifier_name != "html"
                and text[0:1] == "<"
                and re.search(r"^(<!--|<!\[CDATA\[)", text)
            ):
                matched = re.search(r"^(<!--[^\n]*|<!\[CDATA\[)(\n?)([ \t\n]*)([\s\S]*)(-->|]]>)$", text)

                #  if we start to wrap but don't finish, print raw
                if not matched:
                    printer.add_raw_token(raw_token)
                    return

                pre = indentation + matched.group(1) + "\n"
                text = matched.group(4)
                if matched.group(5):
                    post = indentation + matched.group(5)

                #  if there is at least one empty line at the end of this text, strip it
                #  we'll be adding one back after the text but before the containing tag.
                text = re.sub(r"\n[ \t]*$", "", text, count=1)

                if matched.group(2) or "\n" in matched.group(3):
                    #  if the first line of the non-comment text has spaces
                    #  use that as the basis for indenting in null case.
                    matched = re.search(r"[ \t]+$", matched.group(3))
                    if matched:
                        raw_token.whitespace_before = matched.group(0)

            if text:
                if _beautifier:
                    opts: t.Any = copy.deepcopy(self._options.raw_options)
                    try:
                        opts.eol = "\n"
                    except:
                        try:
                            opts = opts._asdict()
                            opts["eol"] = "\n"
                        except:
                            pass
                    text = _beautifier(indentation + text, opts)
                else:
                    #  simply indent the string otherwise
                    white = raw_token.whitespace_before
                    if white:
                        text = re.sub(rf"\n({ white })?", "\n", text)
                    text = indentation + text.replace("\n", "\n" + indentation)

            if pre:
                if not text:
                    text = pre + post
                else:
                    text = pre + text + "\n" + post

            printer.print_newline(False)
            if text:
                raw_token.text = text
                raw_token.whitespace_before = ""
                raw_token.newlines = 0
                printer.add_raw_token(raw_token)
                printer.print_newline(True)

    def _handle_tag_open(
        self,
        printer: Printer,
        raw_token: Token,
        last_tag_token: TagOpenParserToken,
        last_token: Token,
        tokens: TokenStream,
    ):
        parser_token = self._get_tag_open_token(raw_token)

        if (
            (last_tag_token.is_unformatted or last_tag_token.is_content_unformatted)
            and not last_tag_token.is_empty_element
            and raw_token.type == TOKEN.TAG_OPEN
            and not parser_token.is_start_tag
        ):
            #  End element tags for unformatted or content_unformatted elements
            #  are printed raw to keep any newlines inside them exactly the same.
            printer.add_raw_token(raw_token)
            parser_token.start_tag_token = self._tag_stack.try_pop(parser_token.tag_name)
        else:
            printer.traverse_whitespace(raw_token)
            self._set_tag_position(printer, raw_token, parser_token, last_tag_token, last_token)
            if not parser_token.is_inline_element:
                printer.set_wrap_point()

            printer.print_token(raw_token)

        #  count the number of attributes
        if parser_token.is_start_tag and self._is_wrap_attributes_force:
            peek_index = 0
            # peek_token;
            while True:
                peek_token = tokens.peek(peek_index)
                assert peek_token
                if peek_token.type == TOKEN.ATTRIBUTE:
                    parser_token.attr_count += 1
                peek_index += 1
                if peek_token.type == TOKEN.EOF or peek_token.type == TOKEN.TAG_CLOSE:
                    break

        # indent attributes an auto, forced, aligned or forced-align line-wrap
        if (
            self._is_wrap_attributes_force_aligned
            or self._is_wrap_attributes_aligned_multiple
            or self._is_wrap_attributes_preserve_aligned
        ):
            parser_token.alignment_size = len(raw_token.text) + 1

        if not parser_token.tag_complete and not parser_token.is_unformatted:
            printer.alignment_size = parser_token.alignment_size

        return parser_token

    def _get_tag_open_token(self, raw_token: Token):
        # function to get a full tag and parse its type
        parser_token = TagOpenParserToken(self._options, self._tag_stack.get_parser_token(), raw_token)

        parser_token.alignment_size = self._options.wrap_attributes_indent_size

        parser_token.is_end_tag = parser_token.is_end_tag or (parser_token.tag_check in self._options.void_elements)

        parser_token.is_empty_element = parser_token.tag_complete or (
            parser_token.is_start_tag and parser_token.is_end_tag
        )

        parser_token.is_unformatted = not parser_token.tag_complete and (
            parser_token.tag_check in self._options.unformatted
        )

        parser_token.is_content_unformatted = not parser_token.is_empty_element and (
            parser_token.tag_check in self._options.content_unformatted
        )

        parser_token.is_inline_element = (
            (parser_token.tag_name in self._options.inline)
            or (self._options.inline_custom_elements and ("-" in parser_token.tag_name))
            or parser_token.tag_start_char == "{"
        )

        return parser_token

    def _set_tag_position(
        self,
        printer: Printer,
        raw_token: Token,
        parser_token: TagOpenParserToken,
        last_tag_token: TagOpenParserToken,
        last_token: Token,
    ):

        if not parser_token.is_empty_element:
            if parser_token.is_end_tag:  # this tag is a double tag so check for tag-ending
                parser_token.start_tag_token = self._tag_stack.try_pop(
                    parser_token.tag_name
                )  # remove it and all ancestors
            else:  #  it's a start-tag
                #  check if this tag is starting an element that has optional end element
                #  and do an ending needed
                if self._do_optional_end_element(parser_token):
                    if not parser_token.is_inline_element:
                        printer.print_newline(False)

                self._tag_stack.record_tag(parser_token)
                # push it on the tag stack

                if (parser_token.tag_name == "script" or parser_token.tag_name == "style") and not (
                    parser_token.is_unformatted or parser_token.is_content_unformatted
                ):
                    parser_token.custom_beautifier_name = get_custom_beautifier_name(parser_token.tag_check, raw_token)

        if parser_token.tag_check in self._options.extra_liners:  # check if this double needs an extra line
            printer.print_newline(False)
            if not printer._output.just_added_blankline():
                printer.print_newline(True)

        if parser_token.is_empty_element:
            # if this tag name is a single tag type (either in the list or has a closing /)
            #  if you hit an else case, reset the indent level if you are inside an:
            #  'if', 'unless', or 'each' block.
            if parser_token.tag_start_char == "{" and parser_token.tag_check == "else":
                self._tag_stack.indent_to_tag(["if", "unless", "each"])
                parser_token.indent_content = True
                #  Don't add a newline if opening {{#if}} tag is on the current line
                foundIfOnCurrentLine = printer.current_line_has_match(r"{{#if")
                if not foundIfOnCurrentLine:
                    printer.print_newline(False)

            #  Don't add a newline before elements that should remain where they are.
            if (
                parser_token.tag_name == "!--"
                and last_token.type == TOKEN.TAG_CLOSE
                and last_tag_token.is_end_tag
                and "\n" in parser_token.text
            ):
                pass
                # Do nothing. Leave comments on same line.
            else:
                if not (parser_token.is_inline_element or parser_token.is_unformatted):
                    printer.print_newline(False)
                self._calcluate_parent_multiline(printer, parser_token)
        elif parser_token.is_end_tag:  # this tag is a double tag so check for tag-ending
            do_end_expand = False

            #  deciding whether a block is multiline should not be this hard
            do_end_expand = parser_token.start_tag_token and parser_token.start_tag_token.multiline_content
            do_end_expand = do_end_expand or (
                not parser_token.is_inline_element
                and not (last_tag_token.is_inline_element or last_tag_token.is_unformatted)
                and not (last_token.type == TOKEN.TAG_CLOSE and parser_token.start_tag_token == last_tag_token)
                and last_token.type != "TK_CONTENT"
            )

            if parser_token.is_content_unformatted or parser_token.is_unformatted:
                do_end_expand = False

            if do_end_expand:
                printer.print_newline(False)

        else:
            #  it's a start-tag
            parser_token.indent_content = not parser_token.custom_beautifier_name

            if parser_token.tag_start_char == "<":
                if parser_token.tag_name == "html":
                    parser_token.indent_content = self._options.indent_inner_html
                elif parser_token.tag_name == "head":
                    parser_token.indent_content = self._options.indent_head_inner_html
                elif parser_token.tag_name == "body":
                    parser_token.indent_content = self._options.indent_body_inner_html

            if not (parser_token.is_inline_element or parser_token.is_unformatted) and (
                last_token.type != "TK_CONTENT" or parser_token.is_content_unformatted
            ):
                printer.print_newline(False)

            self._calcluate_parent_multiline(printer, parser_token)

    def _calcluate_parent_multiline(self, printer: Printer, parser_token: TagOpenParserToken):
        if (
            parser_token.parent
            and printer._output.just_added_newline()
            and not (
                (parser_token.is_inline_element or parser_token.is_unformatted)
                and parser_token.parent.is_inline_element
            )
        ):
            parser_token.parent.multiline_content = True

    def _do_optional_end_element(self, parser_token: TagOpenParserToken):
        result = None
        #  NOTE: cases of "if there is no more content in the parent element"
        #  are handled automatically by the beautifier.
        #  It assumes parent or ancestor close tag closes all children.
        #  https:# www.w3.org/TR/html5/syntax.html#optional-tags
        if parser_token.is_empty_element or not parser_token.is_start_tag or not parser_token.parent:
            return

        if parser_token.tag_name == "body":
            #  A head element’s end tag may be omitted if the head element is not immediately followed by a space character or a comment.
            result = result or self._tag_stack.try_pop("head")

            # elif (parser_token.tag_name == 'body'):
            #  DONE: A body element’s end tag may be omitted if the body element is not immediately followed by a comment.
        elif parser_token.tag_name == "li":
            #  An li element’s end tag may be omitted if the li element is immediately followed by another li element or if there is no more content in the parent element.
            result = result or self._tag_stack.try_pop("li", ["ol", "ul", "menu"])
        elif parser_token.tag_name == "dd" or parser_token.tag_name == "dt":
            #  A dd element’s end tag may be omitted if the dd element is immediately followed by another dd element or a dt element, or if there is no more content in the parent element.
            #  A dt element’s end tag may be omitted if the dt element is immediately followed by another dt element or a dd element.
            result = result or self._tag_stack.try_pop("dt", ["dl"])
            result = result or self._tag_stack.try_pop("dd", ["dl"])
        elif parser_token.parent.tag_name == "p" and parser_token.tag_name in p_closers:
            #  IMPORTANT: this else-if works because p_closers has no overlap with any other element we look for in this method
            #  check for the parent element is an HTML element that is not an <a>, <audio>, <del>, <ins>, <map>, <noscript>, or <video> element,  or an autonomous custom element.
            #  To do this right, this needs to be coded as an inclusion of the inverse of the exclusion above.
            #  But to start with (if we ignore "autonomous custom elements") the exclusion would be fine.
            p_parent = parser_token.parent.parent
            if not p_parent or (p_parent.tag_name not in p_parent_excludes):
                result = result or self._tag_stack.try_pop("p")
        elif parser_token.tag_name == "rp" or parser_token.tag_name == "rt":
            #  An rt element’s end tag may be omitted if the rt element is immediately followed by an rt or rp element, or if there is no more content in the parent element.
            #  An rp element’s end tag may be omitted if the rp element is immediately followed by an rt or rp element, or if there is no more content in the parent element.
            result = result or self._tag_stack.try_pop("rt", ["ruby", "rtc"])
            result = result or self._tag_stack.try_pop("rp", ["ruby", "rtc"])
        elif parser_token.tag_name == "optgroup":
            #  An optgroup element’s end tag may be omitted if the optgroup element is immediately followed by another optgroup element, or if there is no more content in the parent element.
            #  An option element’s end tag may be omitted if the option element is immediately followed by another option element, or if it is immediately followed by an optgroup element, or if there is no more content in the parent element.
            result = result or self._tag_stack.try_pop("optgroup", ["select"])
            # result = result or self._tag_stack.try_pop('option', ['select']);
        elif parser_token.tag_name == "option":
            #  An option element’s end tag may be omitted if the option element is immediately followed by another option element, or if it is immediately followed by an optgroup element, or if there is no more content in the parent element.
            result = result or self._tag_stack.try_pop("option", ["select", "datalist", "optgroup"])
        elif parser_token.tag_name == "colgroup":
            #  DONE: A colgroup element’s end tag may be omitted if the colgroup element is not immediately followed by a space character or a comment.
            #  A caption element's end tag may be ommitted if a colgroup, thead, tfoot, tbody, or tr element is started.
            result = result or self._tag_stack.try_pop("caption", ["table"])
        elif parser_token.tag_name == "thead":
            #  A colgroup element's end tag may be ommitted if a thead, tfoot, tbody, or tr element is started.
            #  A caption element's end tag may be ommitted if a colgroup, thead, tfoot, tbody, or tr element is started.
            result = result or self._tag_stack.try_pop("caption", ["table"])
            result = result or self._tag_stack.try_pop("colgroup", ["table"])

            # elif (parser_token.tag_name == 'caption'):
            #  DONE: A caption element’s end tag may be omitted if the caption element is not immediately followed by a space character or a comment.
        elif parser_token.tag_name == "tbody" or parser_token.tag_name == "tfoot":
            #  A thead element’s end tag may be omitted if the thead element is immediately followed by a tbody or tfoot element.
            #  A tbody element’s end tag may be omitted if the tbody element is immediately followed by a tbody or tfoot element, or if there is no more content in the parent element.
            #  A colgroup element's end tag may be ommitted if a thead, tfoot, tbody, or tr element is started.
            #  A caption element's end tag may be ommitted if a colgroup, thead, tfoot, tbody, or tr element is started.
            result = result or self._tag_stack.try_pop("caption", ["table"])
            result = result or self._tag_stack.try_pop("colgroup", ["table"])
            result = result or self._tag_stack.try_pop("thead", ["table"])
            result = result or self._tag_stack.try_pop("tbody", ["table"])

            # elif (parser_token.tag_name == 'tfoot'):
            #  DONE: A tfoot element’s end tag may be omitted if there is no more content in the parent element.
        elif parser_token.tag_name == "tr":
            #  A tr element’s end tag may be omitted if the tr element is immediately followed by another tr element, or if there is no more content in the parent element.
            #  A colgroup element's end tag may be ommitted if a thead, tfoot, tbody, or tr element is started.
            #  A caption element's end tag may be ommitted if a colgroup, thead, tfoot, tbody, or tr element is started.
            result = result or self._tag_stack.try_pop("caption", ["table"])
            result = result or self._tag_stack.try_pop("colgroup", ["table"])
            result = result or self._tag_stack.try_pop("tr", ["table", "thead", "tbody", "tfoot"])
        elif parser_token.tag_name == "th" or parser_token.tag_name == "td":
            #  A td element’s end tag may be omitted if the td element is immediately followed by a td or th element, or if there is no more content in the parent element.
            #  A th element’s end tag may be omitted if the th element is immediately followed by a td or th element, or if there is no more content in the parent element.
            result = result or self._tag_stack.try_pop("td", ["table", "thead", "tbody", "tfoot", "tr"])
            result = result or self._tag_stack.try_pop("th", ["table", "thead", "tbody", "tfoot", "tr"])

        #  Start element omission not handled currently
        #  A head element’s start tag may be omitted if the element is empty, or if the first thing inside the head element is an element.
        #  A tbody element’s start tag may be omitted if the first thing inside the tbody element is a tr element, and if the element is not immediately preceded by a tbody, thead, or tfoot element whose end tag has been omitted. (It can’t be omitted if the element is empty.)
        #  A colgroup element’s start tag may be omitted if the first thing inside the colgroup element is a col element, and if the element is not immediately preceded by another colgroup element whose end tag has been omitted. (It can’t be omitted if the element is empty.)

        #  Fix up the parent of the parser token
        parser_token.parent = self._tag_stack.get_parser_token()

        return result


def beautify(input: str | None, options: t.Mapping[str, t.Any] | None = None):
    return Beautifier(input or "", options).beautify()
