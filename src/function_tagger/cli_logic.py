import shutil
from pathlib import Path

from function_tagger.tagger import parse_file


def cmd_arg_file(paths: list[Path]) -> None:
    term = shutil.get_terminal_size()
    for f in paths:
        print(str(f).center(term.columns, "-"))
        tagged = parse_file(f)
        for t in tagged:
            print(str(t))
