import json
import logging
from pathlib import Path
from typing import Any, TypedDict

from function_tagger.extra_types import (
    OutputType,
    PlaceHolderType,
    TagScanResult,
)
from function_tagger.tag_class import TaggedFunction, UntaggedFunction
from function_tagger.tagger import parse_dir, parse_file

logger = logging.getLogger(__name__)


class FunctionDataDict(TypedDict):
    tagged_functions: list[dict[str, Any]]
    untagged_functions: list[dict[str, Any]]


def _return_tagged_untagged_mapping(
    tagged: list[TaggedFunction],
    untagged: list[UntaggedFunction],
    tags: set[str] | None,
) -> FunctionDataDict:
    return {
        "tagged_functions": [
            t.to_json() for t in tagged if t.filter_tags(tags)
        ],
        "untagged_functions": [] if tags else [u.to_json() for u in untagged],
    }


def output_dispatch(
    output_type: OutputType | None,
    tagged: list[TaggedFunction],
    untagged: list[UntaggedFunction],
    tags: set[str] | None,
) -> None:
    output_type = "json" if not output_type else output_type
    if output_type == "json":
        func_dict = _return_tagged_untagged_mapping(tagged, untagged, tags)
        print(
            json.dumps(
                func_dict,
                indent=2,
            )
        )
        return None
    if output_type == "text":
        for t in tagged:
            if not t.filter_tags(tags):
                continue
            print(f"[Tagged Function] {t.qualname}({t.location}): {t.tags}")
        if tags:
            return None
        for t in untagged:
            print(f"[Untagged Function]: {t.qualname}({t.location})")
        return None


def cmd_arg_file(
    paths: list[Path],
    tags: set[str] | None,
    output_type: OutputType | None,
) -> int:
    tagged = []
    for f in paths:
        logger.debug("File: %s", f.name)
        result: TagScanResult = parse_file(f)
        tagged, untagged = result
        output_dispatch(output_type, tagged, untagged, tags)
    return 0


def cmd_arg_dir(
    dir_path: Path,
    tags: set[str] | None,
    output_type: OutputType | None,
) -> int:
    result: PlaceHolderType = parse_dir(dir_path)
    tagged, untagged = result
    tagged_functions = [
        function for functions in tagged.values() for function in functions
    ]
    untagged_functions = [
        function for functions in untagged.values() for function in functions
    ]
    output_dispatch(output_type, tagged_functions, untagged_functions, tags)
    return 0


def init_cache(function_hash_path: Path) -> None:
    function_hash_path = function_hash_path.resolve(strict=True)
    logger.debug("%s", function_hash_path)
