# adopted from black

from dataclasses import dataclass
from pathlib import Path

from click import style

from .output import err, out


class NothingChanged(UserWarning):
    """Raised when reformatted code is the same as source."""


@dataclass
class Report:
    check: bool = False
    quiet: bool = False
    verbose: bool = False
    change_count: int = 0
    same_count: int = 0
    failure_count: int = 0

    def done(self, src: Path, *, changed: bool) -> None:
        if changed:
            reformatted = "would reformat" if self.check else "reformatted"
            if self.verbose or not self.quiet:
                out(f"{reformatted} {src}")
            self.change_count += 1
        else:
            if self.verbose:
                msg = f"{src} already well formatted, good job."
                out(msg, bold=False)
            self.same_count += 1

    def failed(self, src: Path, message: str) -> None:
        err(f"error: cannot format {src}: {message}")
        self.failure_count += 1

    def path_ignored(self, path: Path, message: str) -> None:
        if self.verbose:
            out(f"{path} ignored: {message}", bold=False)

    @property
    def return_code(self) -> int:
        if self.failure_count:
            return 123
        if self.change_count and self.check:
            return 1
        return 0

    def __str__(self) -> str:
        if self.check:
            reformatted = "would be reformatted"
            unchanged = "would be left unchanged"
            failed = "would fail to reformat"
        else:
            reformatted = "reformatted"
            unchanged = "left unchanged"
            failed = "failed to reformat"
        report = []
        if self.change_count:
            s = "s" if self.change_count > 1 else ""
            report.append(
                style(f"{self.change_count} file{s} ", bold=True, fg="blue") + style(f"{reformatted}", bold=True)
            )

        if self.same_count:
            s = "s" if self.same_count > 1 else ""
            report.append(style(f"{self.same_count} file{s} ", fg="blue") + unchanged)
        if self.failure_count:
            s = "s" if self.failure_count > 1 else ""
            report.append(style(f"{self.failure_count} file{s} {failed}", fg="red"))
        return ", ".join(report) + "."
