# Linting

The linting is implemented as [Pylint](https://www.pylint.org) plugin, making it's easy to integrate HTML checks into the workflow.

## Installation

``` { .text, .copy }
pip install pylint-htmf
```

## Simple usage

```
pylint --load-plugin=pylint_htmf --disable=all --enable=htmf-checker <path>
```

This command line runs HTML checks over the files in path, while disabling all other Pylint rules. More info on running checks is in the [Pylint documentation](https://docs.pylint.org)

## Annotating the code

There is no way to hook into Python f-strings interpolation in runtime and make f-expressions safe. So htmf uses the typehints and linting instead.

Linter tries to prove that the f-expressions are either instances of the `Safe` class or simple HTML-safe literals.

---

The expressions are recognized as safe if they are:

- literal strings containing no HTML-special characters
    <!--
    ht.m(f"<p>{ 'known to be safe' }{ '<this will fail>' }</p>")
    -->
    <div class="htmf-code"><div><span style="color: #267f99;">ht</span><span style="color: #000000;">.</span><span style="color: #001080;">m</span><span style="color: #000000;">(</span><span style="color: #0000ff;">f</span><span style="color: #a31515;">"</span><span style="color: #800000;">&lt;p&gt;</span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> </span><span style="color: #a31515;">'known to be safe'</span><span style="color: #000000;"> </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}{</span><span style="color: #000000;"> </span><span style="color: #a31515;">'&lt;this will fail&gt;'</span><span style="color: #000000;"> </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span><span style="color: #800000;">&lt;/p&gt;</span><span style="color: #a31515;">"</span><span style="color: #000000;">)</span></div></div>

- function calls returning `Safe`. htmf's own utilities return `Safe`, so `ht.m`, `ht.t`, etc are ok.
    <!--
    def MyComponent() -> Safe: ...
    ...
    ht.m(f"<div>{ MyComponent() }</div>")
    -->
    <div class="htmf-code"><div><span style="color: #0000ff;">def</span><span style="color: #000000;"> </span><span style="color: #795e26;">MyComponent</span><span style="color: #000000;">() -&gt; </span><span style="color: #267f99;">Safe</span><span style="color: #000000;">: ...</span></div><div><span style="color: #000000;">...</span></div><div><span style="color: #267f99;">ht</span><span style="color: #000000;">.</span><span style="color: #001080;">m</span><span style="color: #000000;">(</span><span style="color: #0000ff;">f</span><span style="color: #a31515;">"</span><span style="color: #800000;">&lt;div&gt;</span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> </span><span style="color: #795e26;">MyComponent</span><span style="color: #000000;">() </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span><span style="color: #800000;">&lt;/div&gt;</span><span style="color: #a31515;">"</span><span style="color: #000000;">)</span></div></div>

    !!! note
        The class methods are currently not recognized, only the simple functions

- variables (including arguments) type-annotated as `Safe`. Linter will check the f-expression, while your typechecker will help you to supply the safe arguments.
    <!--
    def Widget(header: Safe, body: Safe) -> Safe:
        return ht.m(f"<div>{ header } { body }</div>")
    -->
    <div class="htmf-code"><div><span style="color: #0000ff;">def</span><span style="color: #000000;"> </span><span style="color: #795e26;">Widget</span><span style="color: #000000;">(</span><span style="color: #001080;">header</span><span style="color: #000000;">: </span><span style="color: #267f99;">Safe</span><span style="color: #000000;">, </span><span style="color: #001080;">body</span><span style="color: #000000;">: </span><span style="color: #267f99;">Safe</span><span style="color: #000000;">) -&gt; </span><span style="color: #267f99;">Safe</span><span style="color: #000000;">:</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #af00db;">return</span><span style="color: #000000;"> </span><span style="color: #267f99;">ht</span><span style="color: #000000;">.</span><span style="color: #001080;">m</span><span style="color: #000000;">(</span><span style="color: #0000ff;">f</span><span style="color: #a31515;">"</span><span style="color: #800000;">&lt;div&gt;</span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> </span><span style="color: #001080;">header</span><span style="color: #000000;"> </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span><span style="color: #000000;"> </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> </span><span style="color: #001080;">body</span><span style="color: #000000;"> </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span><span style="color: #800000;">&lt;/div&gt;</span><span style="color: #a31515;">"</span><span style="color: #000000;">)</span></div></div>

- `if/else` ternary if both branches are `Safe`
    <!--
        ht.m(f"<div>{ 'a' if some_conditional else 'b' }</div>")
        -->
    <div class="htmf-code"><div><span style="color: #267f99;">ht</span><span style="color: #000000;">.</span><span style="color: #001080;">m</span><span style="color: #000000;">(</span><span style="color: #0000ff;">f</span><span style="color: #a31515;">"</span><span style="color: #800000;">&lt;div&gt;</span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> </span><span style="color: #a31515;">'a'</span><span style="color: #000000;"> </span><span style="color: #af00db;">if</span><span style="color: #000000;"> some_conditional </span><span style="color: #af00db;">else</span><span style="color: #000000;"> </span><span style="color: #a31515;">'b'</span><span style="color: #000000;"> </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span><span style="color: #800000;">&lt;/div&gt;</span><span style="color: #a31515;">"</span><span style="color: #000000;">)</span></div></div>

- `or` expression if left operands are `Safe` (or `None`) and right operand is `Safe`
    <!--
    ht.m(f"<div>{ safe_or_none or another_safe_or_none or '?' }</div>")
    -->
    <div class="htmf-code"><div><span style="color: #267f99;">ht</span><span style="color: #000000;">.</span><span style="color: #001080;">m</span><span style="color: #000000;">(</span><span style="color: #0000ff;">f</span><span style="color: #a31515;">"</span><span style="color: #800000;">&lt;div&gt;</span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> safe_or_none </span><span style="color: #0000ff;">or</span><span style="color: #000000;"> another_safe_or_none </span><span style="color: #0000ff;">or</span><span style="color: #000000;"> </span><span style="color: #a31515;">'?'</span><span style="color: #000000;"> </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span><span style="color: #800000;">&lt;/div&gt;</span><span style="color: #a31515;">"</span><span style="color: #000000;">)</span></div></div>

- simple `gettext` calls. It's assumed that if original strings are ok, the translated strings would be ok too. This rule was added to reduce noise in templates. Enabled by default.
    <!-- There was a bug with python-markdown treating _() of gettext as markdown emph. Solved by escaping it with \_ -->
    <!--
        ht.m(f"<div>{ _('This is assumed safe') } { _('<... but this is not>') }</div>"
    -->
    <div class="htmf-code"><div><span style="color: #267f99;">ht</span><span style="color: #000000;">.</span><span style="color: #001080;">m</span><span style="color: #000000;">(</span><span style="color: #0000ff;">f</span><span style="color: #a31515;">"</span><span style="color: #800000;">&lt;div&gt;</span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> \_(</span><span style="color: #a31515;">'This is assumed safe'</span><span style="color: #000000;">) </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span><span style="color: #000000;"> </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> _(</span><span style="color: #a31515;">'&lt;... but this is not&gt;'</span><span style="color: #000000;">) </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span><span style="color: #800000;">&lt;/div&gt;</span><span style="color: #a31515;">"</span></div></div>

- whitelisted functions known to return HTML-safe results. Empty by default.

## Verifying the markup

The second task of the linter is checking if the markup is valid HTML5. It does it by replacing all f-expressions with whitespaces and parsing result with the [html5lib](https://github.com/html5lib/html5lib-python) in strict mode.

There are a few things to be aware of:

- The html5lib makes a distinction between complete HTML document and fragment. Well-formed document should contain the `#!html <!DOCTYPE html><html>...</html>` tags. Use `ht.document` function to wrap the top-level template. Use `ht.m` for the partials/components.

- html5lib will complain for some standalone fragments invalid outside of the parent tags. Notable example is the `#!html <tr>` tags allowed only inside `#!html <table>`.
  Use the magic comment above the markup function to define the scopes:
    <!--
    # htmf-scopes=html,table
    ht.m("<tr> ... </tr>") # verifies in context of <html><table> ... </table></html>
    -->
    <div class="htmf-code"><div><span style="color: #008000;"># htmf-scopes=html,table</span></div><div><span style="color: #267f99;">ht</span><span style="color: #000000;">.</span><span style="color: #001080;">m</span><span style="color: #000000;">(</span><span style="color: #a31515;">"</span><span style="color: #800000;">&lt;tr&gt;</span><span style="color: #000000;"> ... </span><span style="color: #800000;">&lt;/tr&gt;</span><span style="color: #a31515;">"</span><span style="color: #000000;">) </span><span style="color: #008000;"># verifies in context of &lt;html&gt;&lt;table&gt; ... &lt;/table&gt;&lt;/html&gt;</span></div></div>

## Advanced typing

There are the cases when you want to additionally limit the acceptable arguments types.
For example, you may want the Table to accept only `Safe` Thead, not just any `Safe`'s markup.
You may use the Python's `NewType` and htmf's `SafeOf` annotation to achieve it:
<!--
Thead = NewType("Thead", Safe)

def TableHead() -> Thead:
    return Thead(ht.m("<thead> ... </thead>"))

def Table(head: SafeOf[Thead], items: ...):
    return ht.m(f"<table>{ head } ... </table>")
 -->
<div class="htmf-code"><div><span style="color: #001080;">Thead</span><span style="color: #000000;"> = NewType(</span><span style="color: #a31515;">"Thead"</span><span style="color: #000000;">, </span><span style="color: #267f99;">Safe</span><span style="color: #000000;">)</span></div><br><div><span style="color: #0000ff;">def</span><span style="color: #000000;"> </span><span style="color: #795e26;">TableHead</span><span style="color: #000000;">() -&gt; </span><span style="color: #001080;">Thead</span><span style="color: #000000;">:</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #af00db;">return</span><span style="color: #000000;"> </span><span style="color: #001080;">Thead</span><span style="color: #000000;">(</span><span style="color: #267f99;">ht</span><span style="color: #000000;">.</span><span style="color: #001080;">m</span><span style="color: #000000;">(</span><span style="color: #a31515;">"</span><span style="color: #800000;">&lt;thead&gt;</span><span style="color: #000000;"> ... </span><span style="color: #800000;">&lt;/thead&gt;</span><span style="color: #a31515;">"</span><span style="color: #000000;">))</span></div><br><div><span style="color: #0000ff;">def</span><span style="color: #000000;"> </span><span style="color: #795e26;">Table</span><span style="color: #000000;">(</span><span style="color: #001080;">head</span><span style="color: #000000;">: </span><span style="color: #001080;">SafeOf</span><span style="color: #000000;">[Thead], </span><span style="color: #001080;">items</span><span style="color: #000000;">: ...):</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #af00db;">return</span><span style="color: #000000;"> </span><span style="color: #267f99;">ht</span><span style="color: #000000;">.</span><span style="color: #001080;">m</span><span style="color: #000000;">(</span><span style="color: #0000ff;">f</span><span style="color: #a31515;">"</span><span style="color: #800000;">&lt;table&gt;</span><span style="color: #0000ff;font-style: italic;font-weight: bold;">{</span><span style="color: #000000;"> </span><span style="color: #001080;">head</span><span style="color: #000000;"> </span><span style="color: #0000ff;font-style: italic;font-weight: bold;">}</span><span style="color: #000000;"> ... </span><span style="color: #800000;">&lt;/table&gt;</span><span style="color: #a31515;">"</span><span style="color: #000000;">)</span></div></div>

Now the linter knows the `head` argument is ok since it's annotated as `SafeOf[something]`, while typechecker allows passing only the Thead-compatible argument.

## Options

Dump of `pylint --load-plugin=pylint_htmf --help` follows:

```
...
--htmf-markup-func <regexp>
                    Function wrapping the HTML fragment (default: htmf\.m|htmf\.markup|ht\.m|ht\.markup)
--htmf-document-func <regexp>
                    Function wrapping the HTML document (default: htmf\.document|ht\.document)
--htmf-safetype <regexp>
                    Type annotating the function return type, variable or argument as HTML-safe (default:
                    htmf\.SafeOf|ht\.SafeOf|SafeOf|htmf\.Safe|ht\.Safe|Safe)
--htmf-safe-func <regexp>
                    Whitelist of safe functions (default: None)
--htmf-allow-simple-gettext <y or n>
                    Treat simple non-interpolated gettext calls as safe (default: True)
--htmf-allow-flat-markup <y or n>
                    Allow markup of multiple elements without the parent (default: False)
```
