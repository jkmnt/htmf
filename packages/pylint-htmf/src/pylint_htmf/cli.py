import sys


def run():
    from pylint.lint import Run

    args = ["--load-plugin=pylint_htmf", "--disable=all", "--enable=htmf-checker", *sys.argv[1:]]
    Run(args)
