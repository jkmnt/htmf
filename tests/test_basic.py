# import pytest

from hitml import text, Safe, markup, classname, attr, csv_attr, script, json_attr
from hitml.hitml import escape


class BadArg:
    pass


def test_escape():
    assert escape("<div></div>") == "&lt;div&gt;&lt;/div&gt;"
    assert escape(Safe("<div></div>")) == "<div></div>"
    assert escape(None) == ""
    assert isinstance(escape("<div></div>"), Safe)
    assert isinstance(Safe("<div></div>"), Safe)


def test_text():
    # smoke
    assert text("text") == "text"
    assert text(1) == "1"
    assert text(0) == "0"
    assert text(True) == ""
    assert text(False) == ""
    assert text(None) == ""

    # basic escaping
    assert text(Safe("foo")) == "foo"
    assert text("<>") == "&lt;&gt;"
    assert text(Safe("<>")) == "<>"
    assert text("&nbsp;") == "&amp;nbsp;"
    assert text(Safe("&nbsp;")) == "&nbsp;"

    # iteration
    assert (
        text(
            0,
            1,
            2,
            3,
            " foo ",
            True,
            False,
            [0, 1, 2, 3, " foo ", None, True, False],
            "more",
            ["a", "b", "c", Safe("d")],
        )
        == "0123 foo 0123 foo moreabcd"
    )
    assert text([], [], []) == ""
    assert text([]) == ""

    # set (order is not guaranteed)
    assert text({1, 2}) in ("12", "21")
    assert text({1, None, False, True, "foo"}) in ("1foo", "foo1")

    # dict keys (ok too, the dicts are iterable)
    assert text({1: "3", 2: "4", None: False}) == "12"

    # generators
    assert text((i for i in range(10)), (b for b in (True, False, None)), (c for c in "abcd")) == "0123456789abcd"

    # Wrong args types
    assert text("ok", BadArg(), [BadArg, BadArg(), "ok"], "ok") == "okokok"

    # return type
    assert isinstance(text("<div></div>", 1, 2, 3), Safe)


def test_markup():
    assert markup("<div>") == "<div>"
    assert markup(True) == ""
    assert markup(False) == ""
    # trim
    assert markup("    <div> </div>   ") == "<div> </div>"
    assert markup("    \n\n<div> </div> \n  ") == "<div> </div>"

    assert markup(Safe("<div></div>")) == "<div></div>"

    assert isinstance(markup("<div></div>"), Safe)


def test_classname():
    assert classname("visible") == "visible"
    assert classname(["visible", "invisible"]) == "visible invisible"
    assert classname(["visible", "invisible", True, False]) == "visible invisible"

    assert classname("visible", "invisible", True, False, "flex") == "visible invisible flex"
    assert classname(["visible", "invisible", "flex"], True, False) == "visible invisible flex"
    assert classname("visible", "invisible", True, [False, "flex"]) == "visible invisible flex"

    # trims
    assert classname("  flex  ", " grid", " \n float ", None) == "flex grid float"

    # bads
    assert classname(1, 2, 3, "ok", BadArg, [BadArg(), BadArg], "ok") == "ok ok"

    # generators
    assert (
        classname((f"mb-{i}" for i in range(4)), "flex", (f"mt-{i}" for i in range(4)))
        == "mb-0 mb-1 mb-2 mb-3 flex mt-0 mt-1 mt-2 mt-3"
    )

    # escaping
    assert classname("<here>") == "&lt;here&gt;"
    # ensure no double escaping
    assert classname(Safe("&lt;here&gt;")) == "&lt;here&gt;"
    assert classname(Safe("   &lt;here&gt;     ")) == "&lt;here&gt;"
    # trust the caller - ensure no changes if marked as safe
    assert classname(Safe("<here>")) == "<here>"

    assert isinstance(classname("flex"), Safe)


def test_attr():
    assert (
        attr({"display": "hidden", "tabindex": -1, "type": "submit", "hx-boost": True})
        == 'display="hidden" hx-boost tabindex="-1" type="submit"'
    )

    assert attr({"hx-vals": "{}"}) == 'hx-vals="{}"'
    assert (
        attr({"hx-vals": '{"1":"3", "4":"5"}'})
        == 'hx-vals="{&quot;1&quot;:&quot;3&quot;, &quot;4&quot;:&quot;5&quot;}"'
    )

    assert attr({"hx-vals": Safe('{"1":"3", "4":"5"}')}) == 'hx-vals="{"1":"3", "4":"5"}"'

    assert attr({"data-user": True}) == "data-user"
    assert attr({"data-user": True}, id=False) == "data-user"

    # merge
    assert attr({"data-user": True, "id": True}, id=False) == "data-user"
    assert attr({"data-user": True, "id": False, "visible": "12"}, id=True, visible=True) == "data-user id visible"

    assert isinstance(attr(foo="bar"), Safe)


def test_csv_attr():
    assert csv_attr("load", "from:body delay:1ms", "every 20s") == "load,from:body delay:1ms,every 20s"
    assert csv_attr("<load>", "from:body delay:1ms", "every 20s") == "&lt;load&gt;,from:body delay:1ms,every 20s"
    assert csv_attr(Safe("<load>")) == "<load>"
    assert isinstance(csv_attr("load"), Safe)


def test_json_attr():
    assert json_attr({"a": "b", "c": "d"}) == "{&quot;a&quot;:&quot;b&quot;,&quot;c&quot;:&quot;d&quot;}"
    assert isinstance(json_attr({"a": "b", "c": "d"}), Safe)


def test_script():
    assert script("console.log('<script></script)')") == r"console.log('<script><\/script)')"
