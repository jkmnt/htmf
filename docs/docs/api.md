# Utilities

## markup

alias: `m`, `document`

`#!python def markup(s: str) -> Safe`

Wrapper for the markup. Triggers the HTML-syntax highlight and linting. Strips the whitespaces and marks the string as safe

<!--
>>> ht.m(f" <div>{ ht.m('  <span>Content</span>') }</div>  ")
'<div><span>Content</span></div>'
-->
<div class="htmf-code"><div><span style="color: #000000;">&gt;&gt;&gt; ht.m(</span><span style="color: #0000ff;">f</span><span style="color: #a31515;">"</span><span style="color: #000000;"> </span><span style="color: #800000;">&lt;div&gt;</span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> ht.m(</span><span style="color: #a31515;">'</span><span style="color: #000000;"> &nbsp;</span><span style="color: #800000;">&lt;span&gt;</span><span style="color: #000000;">Content</span><span style="color: #800000;">&lt;/span&gt;</span><span style="color: #a31515;">'</span><span style="color: #000000;">) </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span><span style="color: #800000;">&lt;/div&gt;</span><span style="color: #000000;"> &nbsp;</span><span style="color: #a31515;">"</span><span style="color: #000000;">)</span></div><div><span style="color: #a31515;">'&lt;div&gt;&lt;span&gt;Content&lt;/span&gt;&lt;/div&gt;'</span></div></div>

!!! Note
    Linter treats `document` as the root HTML document with the `#!html <!DOCTYPE html><html>...</html>` top-level tags present.

    `m` is treated as the fragment and may consist of any markup.

---
## text

alias: `t`

`#!python def text(*args: Arg | Iterable[Arg], sep="") -> Safe`

Basic building block for HTML texts and fragments.

The arguments may be `#!python  str | bool | int | float | None` or iterables of such types.
Strings are escaped unless marked as Safe.
Numbers are stringified. Everything else is discarded.


*New in v0.3.0*: Argument may also be an object implementing `__html__` method.
Method must return the HTML-safe string.



Returns the single string of concatenated arguments

<!-- >>> ht.t('123', '456', '789', ['a', 'b', 'c']):
'123456789abc'

>>> ht.t(True, False, None, [0, '1', False, '2'])
'012'

>>> ht.t('<div>')
'&lt;div&gt;'

>>> ht.t(Safe('<div>'))
'<div>' -->

<div class="htmf-code"><div><span style="color: #000000;">&gt;&gt;&gt; ht.t(</span><span style="color: #a31515;">'123'</span><span style="color: #000000;">, </span><span style="color: #a31515;">'456'</span><span style="color: #000000;">, </span><span style="color: #a31515;">'789'</span><span style="color: #000000;">, [</span><span style="color: #a31515;">'a'</span><span style="color: #000000;">, </span><span style="color: #a31515;">'b'</span><span style="color: #000000;">, </span><span style="color: #a31515;">'c'</span><span style="color: #000000;">]):</span></div><div><span style="color: #a31515;">'123456789abc'</span></div><br><div><span style="color: #000000;">&gt;&gt;&gt; ht.t(</span><span style="color: #0000ff;">True</span><span style="color: #000000;">, </span><span style="color: #0000ff;">False</span><span style="color: #000000;">, </span><span style="color: #0000ff;">None</span><span style="color: #000000;">, [</span><span style="color: #098658;">0</span><span style="color: #000000;">, </span><span style="color: #a31515;">'1'</span><span style="color: #000000;">, </span><span style="color: #0000ff;">False</span><span style="color: #000000;">, </span><span style="color: #a31515;">'2'</span><span style="color: #000000;">])</span></div><div><span style="color: #a31515;">'012'</span></div><br><div><span style="color: #000000;">&gt;&gt;&gt; ht.t(</span><span style="color: #a31515;">'&lt;div&gt;'</span><span style="color: #000000;">)</span></div><div><span style="color: #a31515;">'&amp;lt;div&amp;gt;'</span></div><br><div><span style="color: #000000;">&gt;&gt;&gt; ht.t(Safe(</span><span style="color: #a31515;">'&lt;div&gt;'</span><span style="color: #000000;">))</span></div><div><span style="color: #a31515;">'&lt;div&gt;'</span></div></div>

Using with actual markup

<!--
>>> ht.t(
        ht.m("<h1> H1 </h1>"),
        truthy_func() and [
            0 == 1 and ht.m("<h2> H2 </h2>"),
            "foo" if 1 == 1 else "bar",
        ],
    )
'<h1> H1 </h1>foo'
-->
<div class="htmf-code"><div><span style="color: #000000;">&gt;&gt;&gt; ht.t(</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; ht.m(</span><span style="color: #a31515;">"</span><span style="color: #800000;">&lt;h1&gt;</span><span style="color: #000000;"> H1 </span><span style="color: #800000;">&lt;/h1&gt;</span><span style="color: #a31515;">"</span><span style="color: #000000;">),</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; truthy_func() </span><span style="color: #af00db;">and</span><span style="color: #000000;"> [</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #098658;">0</span><span style="color: #000000;"> == </span><span style="color: #098658;">1</span><span style="color: #000000;"> </span><span style="color: #0000ff;">and</span><span style="color: #000000;"> ht.m(</span><span style="color: #a31515;">"</span><span style="color: #800000;">&lt;h2&gt;</span><span style="color: #000000;"> H2 </span><span style="color: #800000;">&lt;/h2&gt;</span><span style="color: #a31515;">"</span><span style="color: #000000;">),</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #a31515;">"foo"</span><span style="color: #000000;"> </span><span style="color: #af00db;">if</span><span style="color: #000000;"> </span><span style="color: #098658;">1</span><span style="color: #000000;"> == </span><span style="color: #098658;">1</span><span style="color: #000000;"> </span><span style="color: #af00db;">else</span><span style="color: #000000;"> </span><span style="color: #a31515;">"bar"</span><span style="color: #000000;">,</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; ],</span></div><div><span style="color: #000000;">&nbsp; &nbsp; )</span></div><div><span style="color: #a31515;">'&lt;h1&gt; H1 &lt;/h1&gt;foo'</span></div></div>

### Common patterns

- JSX-like conditionals
    <!--
        >>> ht.t(
            1 == 1 and 'a',
            2 == 3 or 'b',
            'c' if 4 == 5 else 'd'
        )
        'abd'
    -->
    <div class="htmf-code"><div><span style="color: #000000;">&gt;&gt;&gt; ht.t(</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #098658;">1</span><span style="color: #000000;"> == </span><span style="color: #098658;">1</span><span style="color: #000000;"> </span><span style="color: #af00db;">and</span><span style="color: #000000;"> </span><span style="color: #a31515;">'a'</span><span style="color: #000000;">,</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #098658;">2</span><span style="color: #000000;"> == </span><span style="color: #098658;">3</span><span style="color: #000000;"> </span><span style="color: #af00db;">or</span><span style="color: #000000;"> </span><span style="color: #a31515;">'b'</span><span style="color: #000000;">,</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #a31515;">'c'</span><span style="color: #000000;"> </span><span style="color: #af00db;">if</span><span style="color: #000000;"> </span><span style="color: #098658;">4</span><span style="color: #000000;"> == </span><span style="color: #098658;">5</span><span style="color: #000000;"> </span><span style="color: #af00db;">else</span><span style="color: #000000;"> </span><span style="color: #a31515;">'d'</span></div><div><span style="color: #000000;">&nbsp; &nbsp; )</span></div><div><span style="color: #a31515;">'abd'</span></div></div>

- Conditional groups
    <!--
    >>> ht.t(
            1 == 1 and ['a', 'b'],
            2 != 2 and ['c', 'd'],
            ['e', 'f'] if 3 == 3 else ['g', 'h'],
            4 == 4 and ['i', 5 == 5 and 'j']
        )
    'abefij'
    -->
    <div class="htmf-code"><div><span style="color: #000000;">&gt;&gt;&gt; ht.t(</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #098658;">1</span><span style="color: #000000;"> == </span><span style="color: #098658;">1</span><span style="color: #000000;"> </span><span style="color: #af00db;">and</span><span style="color: #000000;"> [</span><span style="color: #a31515;">'a'</span><span style="color: #000000;">, </span><span style="color: #a31515;">'b'</span><span style="color: #000000;">],</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #098658;">2</span><span style="color: #000000;"> != </span><span style="color: #098658;">2</span><span style="color: #000000;"> </span><span style="color: #af00db;">and</span><span style="color: #000000;"> [</span><span style="color: #a31515;">'c'</span><span style="color: #000000;">, </span><span style="color: #a31515;">'d'</span><span style="color: #000000;">],</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; [</span><span style="color: #a31515;">'e'</span><span style="color: #000000;">, </span><span style="color: #a31515;">'f'</span><span style="color: #000000;">] </span><span style="color: #af00db;">if</span><span style="color: #000000;"> </span><span style="color: #098658;">3</span><span style="color: #000000;"> == </span><span style="color: #098658;">3</span><span style="color: #000000;"> </span><span style="color: #af00db;">else</span><span style="color: #000000;"> [</span><span style="color: #a31515;">'g'</span><span style="color: #000000;">, </span><span style="color: #a31515;">'h'</span><span style="color: #000000;">],</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #098658;">4</span><span style="color: #000000;"> == </span><span style="color: #098658;">4</span><span style="color: #000000;"> </span><span style="color: #af00db;">and</span><span style="color: #000000;"> [</span><span style="color: #a31515;">'i'</span><span style="color: #000000;">, </span><span style="color: #098658;">5</span><span style="color: #000000;"> == </span><span style="color: #098658;">5</span><span style="color: #000000;"> </span><span style="color: #0000ff;">and</span><span style="color: #000000;"> </span><span style="color: #a31515;">'j'</span><span style="color: #000000;">]</span></div><div><span style="color: #000000;">&nbsp; &nbsp; )</span></div><div><span style="color: #a31515;">'abefij'</span></div></div>

- Looping
    <!--
    >>> ht.t(
            [c for c in 'abcd'],
            [c for c in 'efgh' if c == 'f']
        )
    'abcdf'
    -->
    <div class="htmf-code"><div><span style="color: #000000;">&gt;&gt;&gt; ht.t(</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; [c </span><span style="color: #af00db;">for</span><span style="color: #000000;"> c </span><span style="color: #af00db;">in</span><span style="color: #000000;"> </span><span style="color: #a31515;">'abcd'</span><span style="color: #000000;">],</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; [c </span><span style="color: #af00db;">for</span><span style="color: #000000;"> c </span><span style="color: #af00db;">in</span><span style="color: #000000;"> </span><span style="color: #a31515;">'efgh'</span><span style="color: #000000;"> </span><span style="color: #af00db;">if</span><span style="color: #000000;"> c == </span><span style="color: #a31515;">'f'</span><span style="color: #000000;">]</span></div><div><span style="color: #000000;">&nbsp; &nbsp; )</span></div><div><span style="color: #a31515;">'abcdf'</span></div></div>

- Looping with generator expression (less braces)

    <!--
    ht.t(thing for thing in things if thing.visible)
    -->
    <div class="htmf-code"><div><span style="color: #267f99;">ht</span><span style="color: #000000;">.</span><span style="color: #001080;">t</span><span style="color: #000000;">(</span><span style="color: #001080;">thing</span><span style="color: #000000;"> </span><span style="color: #af00db;">for</span><span style="color: #000000;"> </span><span style="color: #001080;">thing</span><span style="color: #000000;"> </span><span style="color: #af00db;">in</span><span style="color: #000000;"> things </span><span style="color: #af00db;">if</span><span style="color: #000000;"> </span><span style="color: #001080;">thing</span><span style="color: #000000;">.visible)</span></div></div>

---
## attr

`#!python def attr(arg: Attrs | None = None, /, **kwargs: Arg) -> Safe`

Formats arguments as the quoted HTML-attributes suitable for direct inclusion into the tags.
Accepts the dictionary of name-value pairs and/or name-value keywords.
Keywords overrides the dictionary.

- `True` values are rendered as just the name, e.g `hidden`
- `False` and `None` values are discarded
- strings are rendered as name-value pairs, e.g. `type="checkbox"`
- numbers are interpolated, e.g. `tabindex="-1"`

*New in v0.3.0*: Objects with `__html__` method are also supported in place of strings.

Returns the single string of sorted whitespace-separated pairs.
<!--
>>> ht.attr(id=12, hidden=True, tabindex=-1)
'hidden id="12" tabindex="-1"'

>>> ht.attr({'data-user': 'Joe', 'data-user-id': 3}, contenteditable=False)
'data-user="Joe" data-user-id="3"'

>>> ht.attr({'data-tag': '<div>'} )
'data-tag="&lt;div&gt;"'

>>> ht.m(f"<div { ht.attr(hidden=True, id=1) }> Text </div>")
'<div hidden id="1"> Text </div>'
 -->
<div class="htmf-code"><div><span style="color: #000000;">&gt;&gt;&gt; ht.attr(</span><span style="color: #001080;">id</span><span style="color: #000000;">=</span><span style="color: #098658;">12</span><span style="color: #000000;">, </span><span style="color: #001080;">hidden</span><span style="color: #000000;">=</span><span style="color: #0000ff;">True</span><span style="color: #000000;">, </span><span style="color: #001080;">tabindex</span><span style="color: #000000;">=-</span><span style="color: #098658;">1</span><span style="color: #000000;">)</span></div><div><span style="color: #a31515;">'hidden id="12" tabindex="-1"'</span></div><br><div><span style="color: #000000;">&gt;&gt;&gt; ht.attr({</span><span style="color: #a31515;">'data-user'</span><span style="color: #000000;">: </span><span style="color: #a31515;">'Joe'</span><span style="color: #000000;">, </span><span style="color: #a31515;">'data-user-id'</span><span style="color: #000000;">: </span><span style="color: #098658;">3</span><span style="color: #000000;">}, </span><span style="color: #001080;">contenteditable</span><span style="color: #000000;">=</span><span style="color: #0000ff;">False</span><span style="color: #000000;">)</span></div><div><span style="color: #a31515;">'data-user="Joe" data-user-id="3"'</span></div><br><div><span style="color: #000000;">&gt;&gt;&gt; ht.attr({</span><span style="color: #a31515;">'data-tag'</span><span style="color: #000000;">: </span><span style="color: #a31515;">'&lt;div&gt;'</span><span style="color: #000000;">} )</span></div><div><span style="color: #a31515;">'data-tag="&amp;lt;div&amp;gt;"'</span></div><br><div><span style="color: #000000;">&gt;&gt;&gt; ht.m(</span><span style="color: #0000ff;">f</span><span style="color: #a31515;">"</span><span style="color: #800000;">&lt;div</span><span style="color: #000000;"> </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> ht.attr(</span><span style="color: #001080;">hidden</span><span style="color: #000000;">=</span><span style="color: #0000ff;">True</span><span style="color: #000000;">, </span><span style="color: #001080;">id</span><span style="color: #000000;">=</span><span style="color: #098658;">1</span><span style="color: #000000;">) </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span><span style="color: #800000;">&gt;</span><span style="color: #000000;"> Text </span><span style="color: #800000;">&lt;/div&gt;</span><span style="color: #a31515;">"</span><span style="color: #000000;">)</span></div><div><span style="color: #a31515;">'&lt;div hidden id="1"&gt; Text &lt;/div&gt;'</span></div></div>

---
## classname

alias: `c`

`#!python def classname(*args: CnArg | Iterable[CnArg], sep=" ") -> Safe`

htmf's variation of a classic [classnames](https://www.npmjs.com/package/classnames).
The supplied arguments may be `#!python str | bool | None` or iterables of such values.
Class names are flattened and joined into the single (unquoted!) string suitable
for inclusion into the `class` attribute. The usage patterns are the same as of `t`.

*New in v0.3.0*: Objects with `__html__` method are also supported in place of strings.

<!--
>>> ht.classname(
        'text-blue-400',
        1 == 0 and 'flex',
        None,
        False,
        1 == 1 and ['mb-1', 'mr-1', 2 == 2 and 'ml-1']
    )
'text-blue-400 mb-1 mr-1 ml-1'

>>> ht.m(f'''
    <div class="{ ht.classname('px-2', 'flex' if 1 == 1 else 'grid') }">
    </div>''')
'<div class="px-2 flex"></div>'
 -->
<div class="htmf-code"><div><span style="color: #000000;">&gt;&gt;&gt; ht.classname(</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #a31515;">'text-blue-400'</span><span style="color: #000000;">,</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #098658;">1</span><span style="color: #000000;"> == </span><span style="color: #098658;">0</span><span style="color: #000000;"> </span><span style="color: #af00db;">and</span><span style="color: #000000;"> </span><span style="color: #a31515;">'flex'</span><span style="color: #000000;">,</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #0000ff;">None</span><span style="color: #000000;">,</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #0000ff;">False</span><span style="color: #000000;">,</span></div><div><span style="color: #000000;">&nbsp; &nbsp; &nbsp; &nbsp; </span><span style="color: #098658;">1</span><span style="color: #000000;"> == </span><span style="color: #098658;">1</span><span style="color: #000000;"> </span><span style="color: #af00db;">and</span><span style="color: #000000;"> [</span><span style="color: #a31515;">'mb-1'</span><span style="color: #000000;">, </span><span style="color: #a31515;">'mr-1'</span><span style="color: #000000;">, </span><span style="color: #098658;">2</span><span style="color: #000000;"> == </span><span style="color: #098658;">2</span><span style="color: #000000;"> </span><span style="color: #0000ff;">and</span><span style="color: #000000;"> </span><span style="color: #a31515;">'ml-1'</span><span style="color: #000000;">]</span></div><div><span style="color: #000000;">&nbsp; &nbsp; )</span></div><div><span style="color: #a31515;">'text-blue-400 mb-1 mr-1 ml-1'</span></div><br><div><span style="color: #000000;">&gt;&gt;&gt; ht.m(</span><span style="color: #0000ff;">f</span><span style="color: #a31515;">'''</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #800000;">&lt;div</span><span style="color: #000000;"> </span><span style="color: #ff0000;">class</span><span style="color: #000000;">=</span><span style="color: #0000ff;">"</span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> ht.classname(</span><span style="color: #a31515;">'px-2'</span><span style="color: #000000;">, </span><span style="color: #a31515;">'flex'</span><span style="color: #000000;"> </span><span style="color: #af00db;">if</span><span style="color: #000000;"> </span><span style="color: #098658;">1</span><span style="color: #000000;"> == </span><span style="color: #098658;">1</span><span style="color: #000000;"> </span><span style="color: #af00db;">else</span><span style="color: #000000;"> </span><span style="color: #a31515;">'grid'</span><span style="color: #000000;">) </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span><span style="color: #0000ff;">"</span><span style="color: #800000;">&gt;</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #800000;">&lt;/div&gt;</span><span style="color: #a31515;">'''</span><span style="color: #000000;">)</span></div><div><span style="color: #a31515;">'&lt;div class="px-2 flex"&gt;&lt;/div&gt;'</span></div></div>

---
## style

`#!python def style(s: str) -> Safe`

Wrapper for inline styles intended to be included into the `style` attribute. HTML-escapes the string. Triggers the CSS-syntax highlight.

---
## handler

`#!python def handler(s: str) -> Safe`

Wrapper for inline javascript event handlers (`onlick` etc).
HTML-escapes the string. Triggers the JS-syntax highlight.

---
## stylesheet

`#!python def stylesheet(s: str) -> Safe`

Wrapper for css stylesheet for inclusion into the `<style>` tag.
Doing almost nothing.
Triggers the CSS-syntax highlight and formatting.

---
## script

`#!python def script(s: str) -> Safe`

Wrapper for javascript for inclusion into the `<script>` tag. Escapes `</` characters. Triggers the JS-syntax highlight and formatting

---
## json_attr

`#!python def json_attr(val: Mapping[str, Any]) -> Safe`

json.dumps the value and HTML-escape it.

---
## csv_attr

`#!python def csv_attr(*args: CnArg | Iterable[CnArg]) -> Safe`

Same as the `classname` but joins string with commas instead of the whitespaces.

---
## mark_as_safe

`#!python def mark_as_safe(s: str) -> Safe`

Mark the string as safe, promoting it to the Safe class.
It's the escape hatch if one really need to include some not-to-be escaped string. This is the same as calling the `Safe()` class constructor, but recognized by linter.

---
## Safe

`#!python class Safe(str)`

Noop subclass of `str`. Used at runtime to determine if string is already escaped. Used in linting to prove the f-expressions are safe.
Not intended to be instantiated directly.

!!! warning
    String methods of `Safe` strings, e.g. `strip`, `join`, `removeprefix`, etc. returns the `str` (at least in current version of htmf). The result (even if actually escaped) is no longer marked as safe. One should be aware of it to avoid double-escaping. The `Safe` string may be unescaped by calling the `#!python Safe.unescape()` method.

---
## SafeOf

Generic annotation to help the linter recognize new subtypes of Safe.
