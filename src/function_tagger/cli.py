import argparse
import logging
from pathlib import Path

from function_tagger.cli_init import init_cache
from function_tagger.cli_logic import cmd_arg_dir, cmd_arg_file
from function_tagger.extra_types import OutputType

logger = logging.getLogger(__name__)


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(levelname)s]: %(message)s",
    )


def cmd_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="function-tagger")
    parser.add_argument("-v", "--verbose", action="store_true")

    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan")
    scan_inputs = scan.add_mutually_exclusive_group(required=True)
    scan_inputs.add_argument("-f", "--files", nargs="+", type=Path)
    scan_inputs.add_argument("-d", "--directory", type=Path)
    scan.add_argument(
        "--format",
        type=str,
        nargs="?",
        help="""
Valid format types:
- Text
- Json
- File
""",
    )
    scan.add_argument("--tags", nargs="+", type=str)

    init = subparsers.add_parser("init")
    init.add_argument(
        "--project_dir",
        type=Path,
    )
    init.add_argument(
        "--cache-location",
        type=Path,
    )

    return parser.parse_args()


def check_format_arg(format_type: str | None) -> int | OutputType | None:
    if format_type is None:
        return None
    format_type = format_type.lower().strip()
    if format_type in ["text", "json", "file"]:
        # raise error that format_type must be one of the following
        # Return type is OutputType but type checker trolling
        return format_type  # pyright: ignore
    return -1


def main() -> None:
    """
    [Needs Review: Debug mode is set to True change later]
    """
    cmd_args = cmd_parser()
    configure_logging(True)
    if cmd_args.command == "init":
        raise SystemExit(
            init_cache(
                cache_path=cmd_args.cache_location,
                project_dir=cmd_args.project_dir,
            )
        )
    if cmd_args.command == "scan":
        tags = set(cmd_args.tags) if cmd_args.tags else None
        format = check_format_arg(cmd_args.format)
        if isinstance(format, int):
            print("broken")
            # how to insert error here?
            #
            raise SystemExit()
        if cmd_args.files:
            raise SystemExit(cmd_arg_file(cmd_args.files, tags, format))
        if cmd_args.directory:
            raise SystemExit(cmd_arg_dir(cmd_args.directory, tags, format))


if __name__ == "__main__":
    main()
