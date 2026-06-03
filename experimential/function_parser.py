import ast
import hashlib
import importlib.util
import inspect
import re
import textwrap
from collections.abc import Callable
from pathlib import Path
from typing import Any

from function_tagger.tag_class import Tag, TaggedFunction


def strip_comments_from_function(func: Callable[..., Any]) -> str:
    """
    [Test-tag] [NeedsReview by: Codex]
    Returns function source without comments or docstring
    """
    if not func.__doc__:
        raise ValueError(f"doc string for {func.__qualname__} is none")
    raw_source = textwrap.dedent(inspect.getsource(func))
    function_body = ast.parse(
        raw_source,
        type_comments=True,
    ).body[0]
    # NOTE remove isinstance checks later, they are redundant checks to
    # make type checker shut up, the only important check is if the function
    # has __doc__ and raise an error then. If a function has a docstring the
    # first statement must be a Expr that is a Constant.
    # No need to look before jumping!
    if not isinstance(function_body, (ast.FunctionDef, ast.AsyncFunctionDef)):
        raise ValueError
    first_stmt = function_body.body[0]
    if not isinstance(first_stmt, ast.Expr):
        raise RuntimeError
    if isinstance(first_stmt.value, ast.Constant):
        function_body.body.pop(0)
    return ast.unparse(function_body)


def generate_function_hash(func: Callable) -> dict[str, str]:
    return {
        func.__qualname__: hash_function(strip_comments_from_function(func))
    }


def generate_tagged_function_object_from_function(
    func: Callable,
    *,
    error_on_missing_docstring: bool = True,
) -> TaggedFunction | None:
    docstring = func.__doc__
    if not docstring and error_on_missing_docstring:
        raise ValueError(f"{func.__qualname__}: docstring was none")
    elif not docstring:
        return None
    tags = get_function_tags_from_docstring(docstring)
    if not tags:
        return None
    func_path = inspect.getsourcefile(func)
    raw_source = inspect.getsource(func)
    if not func_path:
        raise ValueError(f"Unable to find path for {func.__qualname__}")
    func_path = Path(func_path)
    return TaggedFunction(
        func.__qualname__,
        func.__qualname__,
        tags,
        ast.parse(raw_source).body,
        func_path,
    )


def hash_function(func_src_stripped: str) -> str:
    """
    Generate a function hash using sha256
    """
    bytes_func_source = func_src_stripped.encode()
    return hashlib.sha256(
        bytes_func_source,
        usedforsecurity=False,
    ).hexdigest()


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
            noramlized: str = inner_tag[0][1].replace(" ", "")
            tag_list.append(
                Tag(
                    name=inner_tag[0][0],
                    value=noramlized.split(inner_delimter),
                )
            )
        else:
            tag_list.append(Tag(name=t))
    return tag_list


def get_all_objects_from_path(path: Path) -> list[Callable[..., Any]]:
    """[NeedsReview] Returns a list of function objects"""
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    if not spec or not spec.loader:
        raise RuntimeError(f"{spec} cannot be none")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return [
        func
        for _, func in inspect.getmembers(module)
        if inspect.isfunction(func)
    ]


def main() -> None:
    test = Path(__file__).resolve().parent
    for f in Path(test).parent.rglob("*"):
        if f.is_file() and f.name.endswith(".py"):
            objs = get_all_objects_from_path(f)
            tagged_functions: list[TaggedFunction] = []
            for n in objs:
                tagged = generate_tagged_function_object_from_function(
                    n,
                    error_on_missing_docstring=False,
                )
                if tagged:
                    tagged_functions.append(tagged)
            if len(tagged_functions) > 0:
                print(
                    f"{f.name}: returned {len(tagged_functions)} tagged functions"  # noqa E501
                )
                print(*[str(t) for t in tagged_functions])
            else:
                print(f"{f.name}: returned no tagged functions")


if __name__ == "__main__":
    main()
