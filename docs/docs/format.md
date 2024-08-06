# Formatting

HTML formatting is useful not only for aestetic, but also for reducing git diff noise. So htmf supplies the formatter tool based on well-known [js-beautify](https://github.com/beautifier/js-beautify). The tool is able to format HTML, JS and CSS.

## Installation

``` { .text, .copy }
pip install htmf-format
```

## Usage

```
htmf-format <file or dir>
```

htmf-format borrows some conventions (and code :-) from the [Black](https://github.com/psf/black) formatter. So you will find the output quite familiar.

Tool formats strings found in `ht.m()`, `ht.script()`, `ht.stylesheet()` wrappers. Contents of `<script>` and `<style>` HTML tags found in `ht.m()` are formatted too. Wrappers names may be configured.

By default, htmf-format compares the AST before and after formatting to be sure the only changes are the whitespaces and line breaks in markup.

htmf-format is not opinionated and exposes most options of the js-beautify.


## Example
Before
<!--
ht.m(
    f"""
    <div class="row"    >       <div class="col-md-6">
{ ht.t(memo) }
        <div id="up-wizard-progress">
    &lt;!-- progress --&gt;
            </div>
                    <hr />
            <div id="up-wizard-page"    hx-get="{ url_for('.upload', file=file) }"
                        hx-trigger="load"
                    hx-target="this">
&lt!-- .upload target --&gt;
        </div>


            </div>     </div  >
    """
)
 -->
<div class="htmf-code"><div><span style="color: #267f99;">ht</span><span style="color: #000000;">.</span><span style="color: #001080;">m</span><span style="color: #000000;">(</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #0000ff;">f</span><span style="color: #a31515;">"""</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #800000;">&lt;div</span><span style="color: #000000;"> </span><span style="color: #ff0000;">class</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"row"</span><span style="color: #000000;"> &nbsp; &nbsp;</span><span style="color: #800000;">&gt;</span><span style="color: #000000;"> &nbsp; &nbsp; &nbsp; </span><span style="color: #800000;">&lt;div</span><span style="color: #000000;"> </span><span style="color: #ff0000;">class</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"col-md-6"</span><span style="color: #800000;">&gt;</span></div><div><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> </span><span style="color: #267f99;">ht</span><span style="color: #000000;">.</span><span style="color: #001080;">t</span><span style="color: #000000;">(memo) </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #800000;">&lt;div</span><span style="color: #000000;"> </span><span style="color: #ff0000;">id</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"up-wizard-progress"</span><span style="color: #800000;">&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #008000;">&lt;!-- progress --&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #800000;">&lt;/div&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #800000;">&lt;hr</span><span style="color: #000000;"> </span><span style="color: #800000;">/&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #800000;">&lt;div</span><span style="color: #000000;"> </span><span style="color: #ff0000;">id</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"up-wizard-page"</span><span style="color: #000000;"> &nbsp; &nbsp;</span><span style="color: #ff0000;">hx-get</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"</span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> url_for(</span><span style="color: #a31515;">'.upload'</span><span style="color: #000000;">, </span><span style="color: #001080;">file</span><span style="color: #000000;">=</span><span style="color: #001080;">file</span><span style="color: #000000;">) </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span><span style="color: #0000ff;">"</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #ff0000;">hx-trigger</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"load"</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #ff0000;">hx-target</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"this"</span><span style="color: #800000;">&gt;</span></div><div><span style="color: #008000;">&lt;!-- .upload target --&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #800000;">&lt;/div&gt;</span></div><br><br><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #800000;">&lt;/div&gt;</span><span style="color: #000000;"> &nbsp; &nbsp; </span><span style="color: #800000;">&lt;/div</span><span style="color: #000000;"> &nbsp;</span><span style="color: #800000;">&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #a31515;">"""</span></div><div><span style="color: #000000;">)</span></div></div>

After `htmf-format -w 88  --wrap-attributes=force-aligned --max-preserve-newlines=0 <file>`
<!--
ht.m(
    f"""
    <div class="row">
        <div class="col-md-6">
            { ht.t(memo) }
            <div id="up-wizard-progress">
                &lt;!-- progress --&gt;
            </div>
            <hr />
            <div id="up-wizard-page"
                 hx-get="{ url_for('.upload', file=file) }"
                 hx-trigger="load"
                 hx-target="this">
                &lt;!-- .upload target --&gt;
            </div>
        </div>
    </div>
    """
)
 -->
<div class="htmf-code"><div><span style="color: #267f99;">ht</span><span style="color: #000000;">.</span><span style="color: #001080;">m</span><span style="color: #000000;">(</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #0000ff;">f</span><span style="color: #a31515;">"""</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #800000;">&lt;div</span><span style="color: #000000;"> </span><span style="color: #ff0000;">class</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"row"</span><span style="color: #800000;">&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #800000;">&lt;div</span><span style="color: #000000;"> </span><span style="color: #ff0000;">class</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"col-md-6"</span><span style="color: #800000;">&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> </span><span style="color: #267f99;">ht</span><span style="color: #000000;">.</span><span style="color: #001080;">t</span><span style="color: #000000;">(memo) </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #800000;">&lt;div</span><span style="color: #000000;"> </span><span style="color: #ff0000;">id</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"up-wizard-progress"</span><span style="color: #800000;">&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #008000;">&lt;!-- progress --&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #800000;">&lt;/div&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #800000;">&lt;hr</span><span style="color: #000000;"> </span><span style="color: #800000;">/&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #800000;">&lt;div</span><span style="color: #000000;"> </span><span style="color: #ff0000;">id</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"up-wizard-page"</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span><span style="color: #ff0000;">hx-get</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"</span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> url_for(</span><span style="color: #a31515;">'.upload'</span><span style="color: #000000;">, </span><span style="color: #001080;">file</span><span style="color: #000000;">=</span><span style="color: #001080;">file</span><span style="color: #000000;">) </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span><span style="color: #0000ff;">"</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span><span style="color: #ff0000;">hx-trigger</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"load"</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span><span style="color: #ff0000;">hx-target</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"this"</span><span style="color: #800000;">&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #008000;">&lt;!-- .upload target --&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #800000;">&lt;/div&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #800000;">&lt;/div&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #800000;">&lt;/div&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #a31515;">"""</span></div><div><span style="color: #000000;">)</span></div></div>

## Options

Dump of `htmf-format --help` follows:

```
Basic options:
  -w, --wrap-line-length INTEGER  Wrap lines [default: unlimited]
  -q, --quiet                     Stop emitting all non-critical output. Error
                                  messages will still be emitted
  -v, --verbose                   Emit messages about files that were not
                                  changed
  --check                         Don't write the files back, just return the
                                  status. Return code 0 means nothing would
                                  change. Return code 1 means some files would
                                  be reformatted. Return code 123 means there
                                  was an internal error.
  --ast-check / --no-ast-check    Perform AST check after formatting the code
                                  [default: (yes)]
  --html / --no-html              Enable HTML formatting  [default: (yes)]
  --js / --no-js                  Enable JS formatting  [default: (yes)]
  --css / --no-css                Enable CSS formatting  [default: (yes)]
  --html-trigger RE               Regex for detecting the HTML wrapper
                                  function  [default: htmf\.m|htmf\.markup|ht\
                                  .m|ht\.markup|htmf\.document|ht\.document]
  --js-trigger RE                 Regex for detecting the JS wrapper function
                                  [default: htmf\.script|ht\.script|htmf\.hand
                                  ler|ht\.handler]
  --css-trigger RE                Regex for detecting the CSS wrapper function
                                  [default: htmf\.stylesheet|ht\.stylesheet|ht
                                  mf\.style|ht\.style]

Common beautifiers options:
  --preserve-newlines / --no-preserve-newlines
                                  Preserve line-breaks  [default: preserve-
                                  newlines]
  --indent-size INTEGER           Indentation size  [default: 4]
  --end-with-newline              End output with newline
  --indent-empty-lines            Keep indentation on empty lines

HTML beautifier options:
  --indent-inner-html             Indent content of <html>
  --indent-body-inner-html / --no-indent-body-inner-html
                                  Indent content of <body>  [default: indent-
                                  body-inner-html]
  --indent-head-inner-html / --no-indent-head-inner-html
                                  Indent content of <head>  [default: indent-
                                  head-inner-html]
  --indent-scripts [keep|separate|normal]
                                  [default: normal]
  --wrap-attributes [auto|force|force-aligned|force-expand-multiline|aligned-multiple|preserve|preserve-aligned]
                                  Wrap html tag attributes to new lines
                                  [default: preserve-aligned]
  --wrap-attributes-min-attrs INTEGER
                                  Minimum number of html tag attributes for
                                  force wrap attribute options  [default: 2]
  --wrap-attributes-indent-size INTEGER
                                  Indent wrapped tags to after N characters
                                  [default: --indent-size]
  --max-preserve-newlines INTEGER
                                  Number of line-breaks to be preserved in one
                                  chunk  [default: 1]
  --unformatted TEXT              List of tags (defaults to inline) that
                                  should not be reformatted
  --content-unformatted TEXT      List of tags (defaults to pre, textarea)
                                  whose content should not be reformatted
  --extra-liners TEXT             List of tags (defaults to [head,body,html])
                                  that should have an extra newline
  --unformatted-content-delimiter TEXT
                                  Keep text content together between this
                                  string

JS beautifier options:
  --brace-style [collapse|expand|end-expand|none|preserve-inline]
                                  Brace style  [default: collapse, preserve-
                                  inline]
  --space-in-paren                Add padding spaces within paren, ie. f( a, b
                                  )
  --space-in-empty-paren          Add a single space inside empty paren, ie.
                                  f( )
  --jslint-happy                  Enable jslint-stricter mode
  --space-after-anon-function     Add a space before an anonymous function's
                                  parens, ie. function ()
  --space-after-named-function    Add a space before a named function's
                                  parens, ie. function example ()
  --unindent-chained-methods      Don't indent chained method calls
  --break-chained-methods         Break chained method calls across subsequent
                                  lines
  --keep-array-indentation        Preserve array indentation
  --unescape-strings              Decode printable characters encoded in xNN
                                  notation
  --e4x                           Pass E4X xml literals through untouched
  --comma-first                   Put commas at the beginning of new line
                                  instead of end
  --operator-position [before-newline|after-newline|preserve-newline]
                                  Set operator position  [default: before-
                                  newline]

CSS beautifier options:
  --selector-separator-newline / --no-selector-separator-newline
                                  Print each selector on a separate line
                                  [default: selector-separator-newline]
  --newline-between-rules / --no-newline-between-rules
                                  Print empty line between rules  [default:
                                  newline-between-rules]
  --space-around-combinator       Print spaces around combinator
```
