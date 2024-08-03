"""Format HTML in Python f-strings"""

# Licenced under the MIT License: https://www.opensource.org/licenses/mit-license.php

__version__ = "0.1.0"

from dataclasses import dataclass
import io
import pathlib
import re
import sys
import tokenize
import traceback

import click


from .formatter import FragmentFormatter, process
from .beautifiers import get_css_formatter, get_js_formatter, get_html_formatter
from .output import err, out
from .report import Report
from .clicky import option, CommandWithSections
from .files import collect_sources

GENERAL_SECTION = "Basic options"
COMMON_SECTION = "Common beautifiers options"
HTML_SECTION = "HTML beautifier options"
JS_SECTION = "JS beautifier options"
CSS_SECTION = "CSS beautifier options"


@dataclass
class Cfg:
    writeback: bool
    ast_check: bool
    formatters: list[FragmentFormatter]
    report: Report


# infra stuff adopted from black
def decode_bytes(src: bytes) -> tuple[str, str, str]:
    srcbuf = io.BytesIO(src)
    encoding, lines = tokenize.detect_encoding(srcbuf.readline)
    if not lines:
        return "", encoding, "\n"

    newline = "\r\n" if b"\r\n" == lines[0][-2:] else "\n"
    srcbuf.seek(0)
    with io.TextIOWrapper(srcbuf, encoding) as tiow:
        return tiow.read(), encoding, newline


def format_file(path: pathlib.Path, cfg: Cfg):
    src, encoding, newline = decode_bytes(path.read_bytes())

    try:
        dst = process(src, cfg.formatters, verify_ast=cfg.ast_check)
        changed = dst != src
        cfg.report.done(path, changed=changed)
        if changed and cfg.writeback:
            path.write_text(dst, encoding=encoding, newline=newline)
    except Exception as e:
        if cfg.report.verbose:
            traceback.print_exc()
        cfg.report.failed(path, str(e))


def format_stdin_to_stdout(cfg: Cfg):
    path = pathlib.Path("<string>")
    src, encoding, newline = decode_bytes(sys.stdin.buffer.read())

    try:
        dst = process(src, cfg.formatters, verify_ast=cfg.ast_check)
        cfg.report.done(path, changed=dst != src)

        if cfg.writeback:
            f = io.TextIOWrapper(sys.stdout.buffer, encoding=encoding, newline=newline, write_through=True)
            # Make sure there's a newline after the content
            if dst and dst[-1] != "\n":
                dst += "\n"
            f.write(dst)
            f.detach()
    except Exception as e:
        if cfg.report.verbose:
            traceback.print_exc()
        cfg.report.failed(path, str(e))


def validate_regex(ctx: click.Context, param: click.Parameter, value: str | None):
    try:
        return re.compile(value) if value else None
    except re.error as e:
        raise click.BadParameter(f"Not a valid regular expression: {e}") from e


# main cli
@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    cls=CommandWithSections,
)
@click.argument(
    "src",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True, allow_dash=True),
    is_eager=True,
    metavar="SRC ...",
)
#
@option(
    "-w",
    "--wrap-line-length",
    type=int,
    help="Wrap lines [default: unlimited]",
    section=GENERAL_SECTION,
)
@option(
    "-q",
    "--quiet",
    is_flag=True,
    help="Stop emitting all non-critical output. Error messages will still be emitted",
    section=GENERAL_SECTION,
)
@option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Emit messages about files that were not changed",
    section=GENERAL_SECTION,
)
@option(
    "--check",
    is_flag=True,
    help=(
        "Don't write the files back, just return the status. Return code 0 means"
        " nothing would change. Return code 1 means some files would be reformatted."
        " Return code 123 means there was an internal error."
    ),
    section=GENERAL_SECTION,
)
@option(
    "--ast-check/--no-ast-check",
    is_flag=True,
    default=True,
    show_default="yes",
    help="Perform AST check after formatting the code",
    section=GENERAL_SECTION,
)
#
@option(
    "--html/--no-html",
    default=True,
    show_default="yes",
    help="Enable HTML formatting",
    section=GENERAL_SECTION,
)
@option(
    "--js/--no-js",
    default=True,
    show_default="yes",
    help="Enable JS formatting",
    section=GENERAL_SECTION,
)
@option(
    "--css/--no-css",
    default=True,
    show_default="yes",
    help="Enable CSS formatting",
    section=GENERAL_SECTION,
)
@option(
    "--html-trigger",
    type=str,
    default=r"htmf\.m|htmf\.markup|ht\.m|ht\.markup|htmf\.document|ht\.document",
    show_default=True,
    metavar="RE",
    callback=validate_regex,
    help="Regex for detecting the HTML wrapper function",
    section=GENERAL_SECTION,
)
@option(
    "--js-trigger",
    type=str,
    default=r"htmf\.script|ht\.script|htmf\.handler|ht\.handler",
    show_default=True,
    metavar="RE",
    callback=validate_regex,
    help="Regex for detecting the JS wrapper function",
    section=GENERAL_SECTION,
)
@option(
    "--css-trigger",
    type=str,
    default=r"htmf\.stylesheet|ht\.stylesheet|htmf\.style|ht\.style",
    show_default=True,
    metavar="RE",
    callback=validate_regex,
    help="Regex for detecting the CSS wrapper function",
    section=GENERAL_SECTION,
)
#
@option(
    "--preserve-newlines/--no-preserve-newlines",
    default=True,
    show_default=True,
    help="Preserve line-breaks",
    section=COMMON_SECTION,
)
@option(
    "--indent-size",
    type=int,
    default=4,
    show_default=True,
    help="Indentation size",
    section=COMMON_SECTION,
)
@option(
    "--end-with-newline",
    is_flag=True,
    help="End output with newline",
    section=COMMON_SECTION,
)
@option(
    "--indent-empty-lines",
    is_flag=True,
    help="Keep indentation on empty lines",
    section=COMMON_SECTION,
)
@option(
    "--indent-inner-html",
    is_flag=True,
    help="Indent content of <html>",
    section=HTML_SECTION,
)
@option(
    "--indent-body-inner-html/--no-indent-body-inner-html",
    default=True,
    show_default=True,
    help="Indent content of <body>",
    section=HTML_SECTION,
)
@option(
    "--indent-head-inner-html/--no-indent-head-inner-html",
    default=True,
    show_default=True,
    help="Indent content of <head>",
    section=HTML_SECTION,
)
@option(
    "--indent-scripts",
    type=click.Choice(["keep", "separate", "normal"]),
    default="normal",
    show_default=True,
    section=HTML_SECTION,
)
@option(
    "--wrap-attributes",
    type=click.Choice(["auto", "force", "force-aligned", "force-expand-multiline", "aligned-multiple", "preserve", "preserve-aligned"]),
    # default="auto",
    default="preserve-aligned",
    show_default=True,
    help="Wrap html tag attributes to new lines",
    section=HTML_SECTION,
)
@option(
    "--wrap-attributes-min-attrs",
    type=int,
    default=2,
    show_default=True,
    help="Minimum number of html tag attributes for force wrap attribute options",
    section=HTML_SECTION,
)
@option(
    "--wrap-attributes-indent-size",
    type=int,
    help="Indent wrapped tags to after N characters [default: --indent-size]",
    section=HTML_SECTION,
)
@option(
    "--max-preserve-newlines",
    type=int,
    default=1,
    show_default=True,
    help="Number of line-breaks to be preserved in one chunk",
    section=HTML_SECTION,
)
@option(
    "--unformatted",
    help="List of tags (defaults to inline) that should not be reformatted",
    section=HTML_SECTION,
)
@option(
    "--content-unformatted",
    help="List of tags (defaults to pre, textarea) whose content should not be reformatted",
    section=HTML_SECTION,
)
@option(
    "--extra-liners",
    help="List of tags (defaults to [head,body,html]) that should have an extra newline",
    section=HTML_SECTION,
)
@option(
    "--unformatted-content-delimiter",
    help="Keep text content together between this string",
    section=HTML_SECTION,
)
# js
@option(
    "--brace-style",
    type=click.Choice(["collapse", "expand", "end-expand", "none", "preserve-inline"]),
    default=["collapse", "preserve-inline"],
    multiple=True,
    show_default=True,
    help="Brace style",
    section=JS_SECTION,
)
@option(
    "--space-in-paren",
    is_flag=True,
    help="Add padding spaces within paren, ie. f( a, b )",
    section=JS_SECTION,
)
@option(
    "--space-in-empty-paren",
    is_flag=True,
    help="Add a single space inside empty paren, ie. f( )",
    section=JS_SECTION,
)
@option(
    "--jslint-happy",
    is_flag=True,
    help="Enable jslint-stricter mode",
    section=JS_SECTION,
)
@option(
    "--space-after-anon-function",
    is_flag=True,
    help="Add a space before an anonymous function's parens, ie. function ()",
    section=JS_SECTION,
)
@option(
    "--space-after-named-function",
    is_flag=True,
    help="Add a space before a named function's parens, ie. function example ()",
    section=JS_SECTION,
)
@option(
    "--unindent-chained-methods",
    is_flag=True,
    help="Don't indent chained method calls",
    section=JS_SECTION,
)
@option(
    "--break-chained-methods",
    is_flag=True,
    help="Break chained method calls across subsequent lines",
    section=JS_SECTION,
)
@option(
    "--keep-array-indentation",
    is_flag=True,
    help="Preserve array indentation",
    section=JS_SECTION,
)
@option(
    "--unescape-strings",
    is_flag=True,
    help="Decode printable characters encoded in xNN notation",
    section=JS_SECTION,
)
# @option("--wrap-line-length", is_flag=True, help="Wrap lines that exceed N characters [0]")
@option(
    "--e4x",
    is_flag=True,
    help="Pass E4X xml literals through untouched",
    section=JS_SECTION,
)
@option(
    "--comma-first",
    is_flag=True,
    help="Put commas at the beginning of new line instead of end",
    section=JS_SECTION,
)
@option(
    "--operator-position",
    type=click.Choice(["before-newline", "after-newline", "preserve-newline"]),
    default="before-newline",
    show_default=True,
    help="Set operator position",
    section=JS_SECTION,
)
# css
@option(
    "--selector-separator-newline/--no-selector-separator-newline",
    default=True,
    show_default=True,
    help="Print each selector on a separate line",
    section=CSS_SECTION,
)
@option(
    "--newline-between-rules/--no-newline-between-rules",
    default=True,
    show_default=True,
    help="Print empty line between rules",
    section=CSS_SECTION,
)
@option(
    "--space-around-combinator",
    is_flag=True,
    help="Print spaces around combinator",
    section=CSS_SECTION,
)
@click.pass_context
def main(
    ctx: click.Context,
    *,
    src: tuple[str, ...],
    html: bool,
    js: bool,
    css: bool,
    html_trigger: re.Pattern[str],
    js_trigger: re.Pattern[str],
    css_trigger: re.Pattern[str],
    quiet: bool,
    verbose: bool,
    check: bool,
    ast_check: bool,
    brace_style: list[str],  # this one must be processed
    **kwargs,
):
    """Inline HTML/JS/CSS templates formatter"""

    ctx.ensure_object(dict)

    report = Report(check=check, quiet=quiet, verbose=verbose)

    beautifiers_args = {k: v for k, v in kwargs.items() if v is not None}
    beautifiers_args |= {
        # "indent_char": "=",  # - debug
        "indent_with_tabs": False,
        "brace-style": ",".join(brace_style),
        "eol": "\n",
    }

    js_formatter = None
    js_beautifier = None

    if js:
        js_formatter, js_beautifier = get_js_formatter(beautifiers_args, trigger=js_trigger)

    css_formatter = None
    css_beautifier = None

    if css:
        css_formatter, css_beautifier = get_css_formatter(beautifiers_args, trigger=css_trigger)

    html_formatter = None
    if html:
        html_formatter = get_html_formatter(
            beautifiers_args,
            trigger=html_trigger,
            js_beautifier=js_beautifier,
            css_beautifier=css_beautifier,
        )

    formatters: list[FragmentFormatter] = []
    if html_formatter:
        formatters.append(html_formatter)
    if js_formatter:
        formatters.append(js_formatter)
    if css_formatter:
        formatters.append(css_formatter)

    cfg = Cfg(
        ast_check=ast_check,
        writeback=not check,
        formatters=formatters,
        report=report,
    )

    if "-" in src:
        if len(src) > 1:
            err("Can't mix files and stdin")
            ctx.exit(1)
        format_stdin_to_stdout(cfg)
    else:
        for s in collect_sources(src):
            format_file(s, cfg)

    if verbose or not quiet:
        if verbose or report.change_count or report.failure_count:
            out()
        out("Oh no!" if report.return_code else "All done!")
        click.echo(str(report), err=True)
    ctx.exit(report.return_code)


if __name__ == "__main__":
    main()
