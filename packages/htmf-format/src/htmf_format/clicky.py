from typing import Any, Callable
import click

# https://github.com/pallets/click/issues/373#issuecomment-515293746


class SectionedOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.section = kwargs.pop("section", None)
        super().__init__(*args, **kwargs)


class CommandWithSections(click.Command):
    def format_options(self, ctx, formatter):
        """Writes all the options into the formatter if they exist."""
        opts = {}
        for param in self.get_params(ctx):
            par: Any = param
            rv = param.get_help_record(ctx)
            if rv is not None:
                if hasattr(param, "section") and par.section:
                    opts.setdefault(str(par.section), []).append(rv)
                else:
                    opts.setdefault("Options", []).append(rv)

        for name, opts_group in opts.items():
            with formatter.section(name):
                formatter.write_dl(opts_group)


def option(*param_decls: str, **attrs: Any) -> Callable:
    return click.option(*param_decls, **attrs, cls=SectionedOption)
