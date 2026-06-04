import ast
import logging
import re
from pathlib import Path

from function_tagger.extra_types import (
    PlaceHolderType,
    TagScanResult,
)
from function_tagger.tag_class import (
    AstFunctionType,
    Tag,
    TaggedFunction,
    UntaggedFunction,
)

logger = logging.getLogger(__name__)


def get_function_tags_from_docstring(
    docstring: str,
    delimiter: str = ":",
    inner_delimter: str = "|",
) -> list[Tag]:
    """
    Parse a function docstring and return a list of tag objects
    """
    tags: list[str] = re.findall(r"(?:\[)(.*?)(?:\])", docstring)
    inner_pattern = re.compile(rf"(.*)(?:{re.escape(delimiter)})(.*)")
    tag_list: list[Tag] = []
    for t in tags:
        if inner_tag := re.findall(inner_pattern, t):
            # noramlized: str = inner_tag[0][1].replace(" ", "")
            normalized = str(inner_tag[0][1]).strip()
            tag_list.append(
                Tag(
                    name=inner_tag[0][0],
                    value=normalized.split(inner_delimter),
                )
            )
        else:
            tag_list.append(Tag(name=t))
    return tag_list


def generate_tag_from_function_def(
    func_def: AstFunctionType,
    class_base: str | None,
    file_path: Path,
) -> TaggedFunction | None:
    doc_string = ast.get_docstring(func_def)
    if not doc_string:
        return None
    tags = get_function_tags_from_docstring(doc_string)
    if not tags:
        return None
    return TaggedFunction(
        func_def.name,
        class_base,
        tags,
        func_def,
        file_path,
    )


def walk_class_def(
    class_def: ast.ClassDef,
    file_path: Path,
) -> list[TaggedFunction]:
    """
    Walk through a class for a functions and attach
    the class name to the base attribute of the TaggedFunction
    [Needs Review]
    """
    tagged_functions: list[TaggedFunction] = []
    for m in ast.walk(class_def):
        if isinstance(m, AstFunctionType):
            tagged = generate_tag_from_function_def(
                m, class_def.name, file_path
            )
            if tagged:
                tagged_functions.append(tagged)
    return tagged_functions


def parse_file(file_path: Path) -> TagScanResult:
    """
    [Needs Review]
    """
    if file_path.is_dir():
        raise ValueError(f"{file_path.name} cannot be directory")
    f = open(file_path, "r")
    module = ast.parse(f.read())
    f.close()
    tagged_functions: list[TaggedFunction] = []
    untagged_functions: list[UntaggedFunction] = []
    for m in module.body:
        if isinstance(m, ast.ClassDef):
            tagged_functions.extend(walk_class_def(m, file_path))
        elif isinstance(m, AstFunctionType):
            tagged_func = generate_tag_from_function_def(
                m,
                None,
                file_path,
            )
            if tagged_func:
                tagged_functions.append(tagged_func)
            else:
                untagged_functions.append(
                    UntaggedFunction(m.name, None, file_path, m)
                )
    return tagged_functions, untagged_functions


def parse_dir(
    dir_path: Path,
) -> PlaceHolderType:
    """
    [Needs Review]
    """
    dir_path = dir_path.resolve()
    if not dir_path.is_dir():
        raise ValueError(f"{dir_path.name} must be directory")
    tagged_functions_to_path: dict[Path, list[TaggedFunction]] = {}
    untagged_functions_to_path: dict[Path, list[UntaggedFunction]] = {}
    for f in dir_path.rglob("*.py"):
        if f.is_file():
            tagged, untagged = parse_file(f)
            if tagged:
                tagged_functions_to_path[f] = tagged
            if untagged:
                untagged_functions_to_path[f] = untagged
    return tagged_functions_to_path, untagged_functions_to_path
