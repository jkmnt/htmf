# Motivation

Why one would ever want to code HTML in Python f-strings ? The common wisdom is to use the template languages (_jinja_, _mako_, etc.) and separate the concerns.

Templates languages were invented with the idea of separation of concerns. Or, more likely, with the idea of "let's add some dynamic to this otherwise static document". They are great for the static sites, user-generated markup, teams with dedicated designers. Programmers manage the logic and models. Designers are authoring the HTML. Template languages give designers a basic programming features for rendering models: loops, conditionals, filters, macros. No way should designers mess with the code and models. Template isolate these worlds.

The situation is different for developers, fully controlling the templates and implementing both the code and markup.
The templates languages stand in the way. They lack the expressiveness of programming language. They are bound to the models only by the fragile magic strings (identifiers). It's too easy to produce invalid markup by misplacing some conditional blocks, like the C-code with `#ifdef` overuse. IDE support is not that good. Composing from macro components
at the template language level is hard. Scopes of variables are mess.

A lot of times templates are sitting in the dark corner of the repository that nobody wants to touch. With a sign on the door saying Beware of the Leopard.

## Rethinking

Think about it for the moment. We are dumping our beautifully
type-annotated models with full IDE support into the template engine, and they leave the Python land. We receive them in the
Template language land and reconstruct them by the fragile untyped string identifiers. Engine executes the template compiled to function, which processes the conditionals, stringifies the models attributes, applies filters and interpolates the result into the huge string.
The string leaves the Template language land to be received back in the Python land.

What if we could stay in the Python land until the very end ? And it would be so nice to let the Python itself compile the template code. And maybe this code could be safe from eval and template injections.
Then this code should be very fast, since it's native. And maybe we could get rid of magic identifiers too and let the IDE help us with missing attributes, refactoring, and stuff. And throw in a good measure of typesafety to prevent us
from accidentally templating the wrong models. And then let us use the full power of Python and libraries in templating. If only it could be possible ...

Sure, the f-strings are far from perfect, but they are native, fast, and safe. With the help of the few utilities, we could build
our minimal templating solution. It won't be foolproof, but good enough for a lot of cases.

## Expressiveness of language

[React](https://react.dev)'s JSX success shows that reusing the JS as the template logic engine is the great idea. Almost nothing new to learn, full language power at the fingertips.

[lit-html](https://lit.dev) and numerous other JS tagged literal libraries use the native JS templates for producing HTML. htmf tries to bring the same to Python.

Various declarative config formats with templates (_Ansible_!) become unmanageable after just a few introduced conditionals. On the other way, language-based configs scales much better.

## Separation of concerns/locality

Some modern examples:

React blurs the distinction between code and markup in JSX.

[Vue.js](https://vuejs.org) components are the mixture of code, templates and styles, all nicely sitting in one file. Moreother, there is an option to produce HTML with tagged literals too.

[tailwindcss](https://tailwindcss.com) brings styles back into the markup, brokes with the traditional HTML/CSS separation. Developers are happy.

CSS-in-JS libraries place the CSS declarations in JS code... Actually, lets forget it. It was a horrible idea.

No more switching between files and syncing identifiers back and forth.

htmf allows colocating markup with form, route, or model.
In some cases, it may be just the right solution.

## Composability

htmf promotes splitting the markup into the number of small components and then composing them using the built-in Python language features.

As soon as the template becomes noisy, it's time to refactor it into the separate component. Tailwind suggests the [same solution](https://tailwindcss.com/docs/reusing-styles#extracting-components-and-partials) for its unwieldy long class strings.

The interesting thing here is that above the some base level there is no more raw HTML to be seen, just the components:
<!--
fields = [Input("a", ...), Textbox("b", ...)]
return Layout(
    body=Form(fields, ...),
    header=Header(),
    footer=Footer()
)
 -->
<div class="htmf-code"><div><span style="color: #001080;">fields</span><span style="color: #000000;"> = [Input(</span><span style="color: #a31515;">"a"</span><span style="color: #000000;">, ...), Textbox(</span><span style="color: #a31515;">"b"</span><span style="color: #000000;">, ...)]</span></div><div><span style="color: #af00db;">return</span><span style="color: #000000;"> Layout(</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #001080;">body</span><span style="color: #000000;">=Form(</span><span style="color: #001080;">fields</span><span style="color: #000000;">, ...),</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #001080;">header</span><span style="color: #000000;">=Header(),</span></div><div><span style="color: #000000;">&nbsp; &nbsp; </span><span style="color: #001080;">footer</span><span style="color: #000000;">=Footer()</span></div><div><span style="color: #000000;">)</span></div></div>

---
Give the HTML in f-strings a try on some side project, with the linting and syntax highlighting it actually feels ok.