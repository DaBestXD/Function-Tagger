import json
import logging
from pathlib import Path
from typing import Any, Mapping, Sequence, TypedDict

from function_tagger.tag_class import TaggedFunction, UntaggedFunction
from function_tagger.tagger import parse_dir

logger = logging.getLogger(__name__)


class JsonSchema(TypedDict):
    version: int  # swap this to the packing.version maybe?
    tagged_functions: list[dict[str, Any]]
    untagged_functions: list[dict[str, Any]]


def count_functions(
    mapping: Mapping[Path, Sequence[UntaggedFunction | TaggedFunction]],
) -> int:
    return sum(len(functions) for functions in mapping.values())


def init_cache(
    cache_path: Path | None,
    project_dir: Path | None,
    folder_name: str = ".function-tagger",
) -> None:
    """
    [Needs Review]
    Generate a .function-tagger folder with function-tagger-cache file,
    and human readable files? maybe json?
    """
    if not project_dir:
        raise ValueError("project_dir cannot be none")
    cache_path = (
        cache_path if cache_path else Path("./").resolve() / folder_name
    )
    function_cache = cache_path / ".function-cache.json"
    try:
        cache_path.mkdir(parents=True, exist_ok=False)
        function_cache.touch(exist_ok=False)
        logger.debug("Creating %s", cache_path)
        logger.debug("Creating %s", function_cache)
    except FileExistsError as e:
        logger.debug("%s already created, skipping...", e.filename)
        return None
    tagged, untagged = parse_dir(project_dir)
    struct: JsonSchema = {
        "version": 1,  # change this later
        "tagged_functions": [
            {str(p): [s.to_json() for s in v]} for p, v in tagged.items()
        ],
        "untagged_functions": [
            {str(p): [s.to_json() for s in v]} for p, v in untagged.items()
        ],
    }
    logger.debug("Found %s tagged functions", count_functions(tagged))
    logger.debug("Found %s untagged functions", count_functions(untagged))
    with open(function_cache, "w") as f:
        f.write(json.dumps(struct, indent=2))
