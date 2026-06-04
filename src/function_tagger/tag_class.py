import ast
import copy
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

AstFunctionType = ast.FunctionDef | ast.AsyncFunctionDef


@dataclass
class Tag:
    name: str
    value: str | list[str] | None = None

    def __str__(self) -> str:
        if isinstance(self.value, list):
            return f"{self.name}: {' '.join(self.value)}"
        if self.value:
            return f"{self.name}: {self.value}"
        return self.name


@dataclass
class UntaggedFunction:
    name: str
    base: str | None
    location: Path
    node: AstFunctionType

    @property
    def qualname(self):
        if self.base:
            return f"{self.base}.{self.name}"
        return self.name

    @property
    def hash(self) -> str:
        """
        Returns the function hash
        (Docstring and comments are not included in hash calculation)
        """
        node = copy.deepcopy(self.node)
        node.body.pop(0)
        func_hash = (
            hashlib.sha256(
                ast.unparse(node).encode(),
                usedforsecurity=False,
            )
        ).hexdigest()
        del node
        return func_hash

    def to_json(self) -> dict[str, Any]:
        return {
            "qualname": self.qualname,
            "location": str(self.location),
            "hash": self.hash,
        }

    def __str__(self) -> str:
        return ""


class TaggedFunction:
    def __init__(
        self,
        name: str,
        base: str | None,
        tags: list[Tag],
        node: AstFunctionType,
        location: Path,
    ):
        self.name = name
        self.tags = tags
        self.node = node
        self.base = base
        self.location = location

    def to_json(self) -> dict[str, Any]:
        return {
            "qualname": self.qualname,
            "location": str(self.location),
            "tags": [{t.name: t.value} for t in self.tags],
            "hash": self.hash,
        }

    def filter_tags(self, tags: set[str] | None) -> bool:
        if not tags:
            return True
        return bool({t.name for t in self.tags} & tags)

    @property
    def qualname(self) -> str:
        """
        Return `Class_name.func_name` if function belongs to class,
        This only returns the base class of the function,
        and ignores multiple levels of inheritence
        Example:
        ```
        class Foo:
            def add()->int: ...
        class Bar(Foo):
            def add()->int: ...
        ```
        Qualname for `add()` under Bar returns `Bar.add`
        and doesn't return `Foo.Bar.add`
        """
        if self.base:
            return f"{self.base}.{self.name}"
        else:
            return self.name

    @property
    def hash(self) -> str:
        """
        Returns the function hash
        (Docstring and comments are not included in hash calculation)
        """
        node = copy.deepcopy(self.node)
        node.body.pop(0)
        func_hash = (
            hashlib.sha256(
                ast.unparse(node).encode(),
                usedforsecurity=False,
            )
        ).hexdigest()
        del node
        return func_hash

    def __str__(self) -> str:
        tags = [str(t) for t in self.tags]
        return f"({Path(self.location.parent.name) / self.location.name}){self.qualname}: {tags}"  # noqa E501

    def __repr__(self) -> str:
        class_vars = [f"{k}={v}" for k, v in self.__dict__.items()]
        return f"{self.__class__.__name__}({', '.join(class_vars)})"
