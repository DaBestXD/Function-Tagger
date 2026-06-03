import argparse
from pathlib import Path

from function_tagger.cli_logic import cmd_arg_file


def cmd_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--files", nargs="+", type=Path)
    parser.add_argument("--dirs", nargs="+", type=Path)
    parser.add_argument("--init")
    return parser.parse_args()


def main() -> None:
    cmd_args = cmd_parser()
    if cmd_args.files:
        cmd_arg_file(cmd_args.files)


if __name__ == "__main__":
    main()
