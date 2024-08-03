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

import re
from dataclasses import dataclass

from ..core.tokenizer import Token
from ..core.tokenizer import TokenTypes as BaseTokenTypes
from ..core.tokenizer import Tokenizer as BaseTokenizer
from ..core.directives import Directives

from ..core.pattern import Pattern
from ..core.templatablepattern import TemplatablePattern

from .options import Options


class TokenTypes(BaseTokenTypes):
    TAG_OPEN = "TK_TAG_OPEN"
    TAG_CLOSE = "TK_TAG_CLOSE"
    CONTROL_FLOW_OPEN = "TK_CONTROL_FLOW_OPEN"
    CONTROL_FLOW_CLOSE = "TK_CONTROL_FLOW_CLOSE"
    ATTRIBUTE = "TK_ATTRIBUTE"
    EQUALS = "TK_EQUALS"
    VALUE = "TK_VALUE"
    COMMENT = "TK_COMMENT"
    TEXT = "TK_TEXT"
    UNKNOWN = "TK_UNKNOWN"


TOKEN = TokenTypes()

directives_core = Directives(r"<!--", r"-->")


@dataclass
class TokenizerPatterns:
    word: Pattern
    word_control_flow_close_excluded: Pattern
    single_quote: Pattern
    double_quote: Pattern
    attribute: Pattern
    element_name: Pattern
    angular_control_flow_start: Pattern
    handlebars_comment: Pattern
    handlebars: Pattern
    handlebars_open: Pattern
    handlebars_raw_close: Pattern
    comment: Pattern
    cdata: Pattern
    conditional_comment: Pattern
    processing: Pattern

    unformatted_content_delimiter: Pattern | None


class Tokenizer(BaseTokenizer):
    def __init__(self, input_string, options: Options):
        super().__init__(input_string, options)
        self._current_tag_name = ""
        self._options: Options

        # Words end at whitespace or when a tag starts
        # if we are indenting handlebars, they are considered tags
        templatable_reader = TemplatablePattern(self._input).read_options(self._options)
        pattern_reader = Pattern(self._input)

        self.__patterns = TokenizerPatterns(
            word=templatable_reader.until(r"[\n\r\t <]"),
            word_control_flow_close_excluded=templatable_reader.until(r"[\n\r\t <}]"),
            single_quote=templatable_reader.until_after(r"'"),
            double_quote=templatable_reader.until_after(r'"'),
            attribute=templatable_reader.until(r"[\n\r\t =>]|/>"),
            element_name=templatable_reader.until(r"[\n\r\t >/]"),
            angular_control_flow_start=pattern_reader.matching(r"\@[a-zA-Z]+[^({]*[({]"),
            handlebars_comment=pattern_reader.starting_with(r"{{!--").until_after(r"--}}"),
            handlebars=pattern_reader.starting_with(r"{{").until_after(r"}}"),
            handlebars_open=pattern_reader.until(r"[\n\r\t }]"),
            handlebars_raw_close=pattern_reader.until(r"}}"),
            comment=pattern_reader.starting_with(r"<!--").until_after(r"-->"),
            cdata=pattern_reader.starting_with(r"<!\[CDATA\[").until_after(r"]]>"),
            # https:#en.wikipedia.org/wiki/Conditional_comment
            conditional_comment=pattern_reader.starting_with(r"<!\[").until_after(r"]>"),
            processing=pattern_reader.starting_with(r"<\?").until_after(r"\?>"),
            unformatted_content_delimiter=None,
        )

        if self._options.indent_handlebars:
            #  NOTE: assuming the Pattern is TemplatablePattern, not the base Pattern
            assert isinstance(self.__patterns.word, TemplatablePattern)
            assert isinstance(self.__patterns.word_control_flow_close_excluded, TemplatablePattern)
            self.__patterns.word = self.__patterns.word.exclude("handlebars")
            self.__patterns.word_control_flow_close_excluded = self.__patterns.word_control_flow_close_excluded.exclude(
                "handlebars"
            )

        self._unformatted_content_delimiter = None

        if self._options.unformatted_content_delimiter:
            regexp = self._input.get_literal_regexp(self._options.unformatted_content_delimiter)
            if regexp:
                self.__patterns.unformatted_content_delimiter = pattern_reader.matching(regexp).until_after(regexp)

    def _is_comment(self, current_token: Token):
        return False  # current_token.type == TOKEN.COMMENT or current_token.type == TOKEN.UNKNOWN;

    def _is_opening(self, current_token: Token):
        return current_token.type == TOKEN.TAG_OPEN or current_token.type == TOKEN.CONTROL_FLOW_OPEN

    def _is_closing(self, current_token: Token, open_token: Token | None):
        return (
            current_token.type == TOKEN.TAG_CLOSE
            and (
                open_token
                and (
                    ((current_token.text == ">" or current_token.text == "/>") and open_token.text[0:1] == "<")
                    or (current_token.text == "}}" and open_token.text[0:1] == "{" and open_token.text[1:2] == "{")
                )
            )
        ) or (
            current_token.type == TOKEN.CONTROL_FLOW_CLOSE
            and (current_token.text == "}" and open_token and open_token.text.endswith("{"))
        )

    def _reset(self):
        self._current_tag_name = ""

    def _get_next_token(self, previous_token: Token, open_token: Token | None):
        token = None
        self._readWhitespace()
        c = self._input.peek()

        if c is None:
            return self._create_token(TOKEN.EOF, "")

        token = token or self._read_open_handlebars(c, open_token)
        token = token or self._read_attribute(c, previous_token, open_token)
        token = token or self._read_close(c, open_token)
        token = token or self._read_script_and_style(c, previous_token)
        token = token or self._read_control_flows(c, open_token)
        token = token or self._read_raw_content(c, previous_token, open_token)
        token = token or self._read_content_word(c, open_token)
        token = token or self._read_comment_or_cdata(c)
        token = token or self._read_processing(c)
        token = token or self._read_open(c, open_token)
        token = token or self._create_token(TOKEN.UNKNOWN, self._input.next())

        return token

    def _read_comment_or_cdata(self, c: str):
        token = None
        resulting_string = None
        directives = None

        if c == "<":
            peek1 = self._input.peek(1)
            # We treat all comments as literals, even more than preformatted tags
            # we only look for the appropriate closing marker
            if peek1 == "!":
                resulting_string = self.__patterns.comment.read()

                # only process directive on html comments
                if resulting_string:
                    directives = directives_core.get_directives(resulting_string)
                    if directives and directives["ignore"] == "start":
                        resulting_string += directives_core.readIgnored(self._input)
                else:
                    resulting_string = self.__patterns.cdata.read()

            if resulting_string:
                token = self._create_token(TOKEN.COMMENT, resulting_string)
                token.directives = directives

        return token

    def _read_processing(self, c: str):
        token = None
        resulting_string = None
        directives = None

        if c == "<":
            peek1 = self._input.peek(1)
            if peek1 == "!" or peek1 == "?":
                resulting_string = self.__patterns.conditional_comment.read()
                resulting_string = resulting_string or self.__patterns.processing.read()

            if resulting_string:
                token = self._create_token(TOKEN.COMMENT, resulting_string)
                token.directives = directives

        return token

    def _read_open(self, c: str, open_token: Token | None):
        resulting_string = None
        token = None
        if not open_token or open_token.type == TOKEN.CONTROL_FLOW_OPEN:
            if c == "<":

                resulting_string = self._input.next()
                if self._input.peek() == "/":
                    resulting_string += self._input.next()

                resulting_string += self.__patterns.element_name.read()
                token = self._create_token(TOKEN.TAG_OPEN, resulting_string)

        return token

    def _read_open_handlebars(self, c: str, open_token: Token | None):
        resulting_string = None
        token = None
        if not open_token or open_token.type == TOKEN.CONTROL_FLOW_OPEN:
            if (
                ("angular" in self._options.templating or self._options.indent_handlebars)
                and c == "{"
                and self._input.peek(1) == "{"
            ):
                if self._options.indent_handlebars and self._input.peek(2) == "!":
                    resulting_string = self.__patterns.handlebars_comment.read()
                    resulting_string = resulting_string or self.__patterns.handlebars.read()
                    token = self._create_token(TOKEN.COMMENT, resulting_string)
                else:
                    resulting_string = self.__patterns.handlebars_open.read()
                    token = self._create_token(TOKEN.TAG_OPEN, resulting_string)

        return token

    def _read_control_flows(self, c: str, open_token: Token | None):
        resulting_string = ""
        token = None
        # Only check for control flows if angular templating is set
        if "angular" not in self._options.templating:
            return token

        if c == "@":
            resulting_string = self.__patterns.angular_control_flow_start.read()
            if resulting_string == "":
                return token

            opening_parentheses_count = 1 if resulting_string.endswith("(") else 0
            closing_parentheses_count = 0
            # The opening brace of the control flow is where the number of opening and closing parentheses equal
            # e.g. @if({value: true} !== null) {
            while not (resulting_string.endswith("{") and opening_parentheses_count == closing_parentheses_count):
                next_char = self._input.next()
                if next_char is None:
                    break
                elif next_char == "(":
                    opening_parentheses_count += 1
                elif next_char == ")":
                    closing_parentheses_count += 1
                resulting_string += next_char
            token = self._create_token(TOKEN.CONTROL_FLOW_OPEN, resulting_string)
        elif c == "}" and open_token and open_token.type == TOKEN.CONTROL_FLOW_OPEN:
            resulting_string = self._input.next()
            token = self._create_token(TOKEN.CONTROL_FLOW_CLOSE, resulting_string)

        return token

    def _read_close(self, c: str, open_token: Token | None):
        resulting_string = None
        token = None
        if open_token and open_token.type == TOKEN.TAG_OPEN:
            if open_token.text[0:1] == "<" and (c == ">" or (c == "/" and self._input.peek(1) == ">")):
                resulting_string = self._input.next()
                if c == "/":  #  for close tag "/>"
                    resulting_string += self._input.next()
                token = self._create_token(TOKEN.TAG_CLOSE, resulting_string)
            elif open_token.text[0:1] == "{" and c == "}" and self._input.peek(1) == "}":
                self._input.next()
                self._input.next()
                token = self._create_token(TOKEN.TAG_CLOSE, "}}")

        return token

    def _read_attribute(self, c, previous_token: Token, open_token: Token | None):
        token = None
        resulting_string = ""
        if open_token and open_token.text[0:1] == "<":

            if c == "=":
                token = self._create_token(TOKEN.EQUALS, self._input.next())
            elif c == '"' or c == "'":
                content = self._input.next()
                if c == '"':
                    content += self.__patterns.double_quote.read()
                else:
                    content += self.__patterns.single_quote.read()

                token = self._create_token(TOKEN.VALUE, content)
            else:
                resulting_string = self.__patterns.attribute.read()

                if resulting_string:
                    if previous_token.type == TOKEN.EQUALS:
                        token = self._create_token(TOKEN.VALUE, resulting_string)
                    else:
                        token = self._create_token(TOKEN.ATTRIBUTE, resulting_string)

        return token

    def _is_content_unformatted(self, tag_name: str):
        # void_elements have no content and so cannot have unformatted content
        # script and style tags should always be read as unformatted content
        # finally content_unformatted and unformatted element contents are unformatted
        return tag_name not in self._options.void_elements and (
            tag_name in self._options.content_unformatted or tag_name in self._options.unformatted
        )

    def _read_raw_content(self, c, previous_token: Token, open_token: Token | None):
        resulting_string = ""
        if open_token and open_token.text[0:1] == "{":
            resulting_string = self.__patterns.handlebars_raw_close.read()
        elif (
            previous_token.type == TOKEN.TAG_CLOSE
            and previous_token.opened
            and previous_token.opened.text[0:1] == "<"
            and previous_token.text[0:1] != "/"
        ):
            # ^^ empty tag has no content
            tag_name = previous_token.opened.text[1:].lower()
            if self._is_content_unformatted(tag_name):
                resulting_string = self._input.readUntil(re.compile(rf"</{ tag_name }[\n\r\t ]*?>", re.IGNORECASE))
        if resulting_string:
            return self._create_token(TOKEN.TEXT, resulting_string)

        return None

    def _read_script_and_style(self, c: str, previous_token: Token):
        if (
            previous_token.type == TOKEN.TAG_CLOSE
            and previous_token.opened
            and previous_token.opened.text[0:1] == "<"
            and previous_token.text[0:1] != "/"
        ):
            tag_name = previous_token.opened.text[1:].lower()
            if tag_name == "script" or tag_name == "style":
                # Script and style tags are allowed to have comments wrapping their content
                # or just have regular content.
                token = self._read_comment_or_cdata(c)
                if token:
                    token.type = TOKEN.TEXT
                    return token
                resulting_string = self._input.readUntil(re.compile(rf"</{ tag_name }[\n\r\t ]*?>", re.IGNORECASE))
                if resulting_string:
                    return self._create_token(TOKEN.TEXT, resulting_string)

        return None

    def _read_content_word(self, c, open_token: Token | None):
        resulting_string = ""
        if self._options.unformatted_content_delimiter and self.__patterns.unformatted_content_delimiter:
            if c == self._options.unformatted_content_delimiter[0]:
                resulting_string = self.__patterns.unformatted_content_delimiter.read()

        if not resulting_string:
            resulting_string = (
                self.__patterns.word_control_flow_close_excluded.read()
                if (open_token and open_token.type == TOKEN.CONTROL_FLOW_OPEN)
                else self.__patterns.word.read()
            )

        if resulting_string:
            return self._create_token(TOKEN.TEXT, resulting_string)

        return None
