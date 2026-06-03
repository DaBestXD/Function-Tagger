import ast
import copy
import hashlib
from dataclasses import dataclass
from pathlib import Path

AstFunctionType = ast.FunctionDef | ast.AsyncFunctionDef


@dataclass
class Tag:
    name: str
    value: str | list[str] | None = None

    def __str__(self) -> str:
        if isinstance(self.value, list):
            return f"{self.name}: {' '.join(self.value)}"
        return f"{self.name}: {self.value}"


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

    @property
    def qualname(self) -> str:
        """
        Return Class_name.func_name if function belongs to class
        """
        if self.base:
            return f"{self.base}.{self.name}"
        else:
            return self.name

    @property
    def hash(self) -> str:
        """
        Returns the function hash
        (Docstring/comments is not included in hash calculation)
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
        return f"({self.location.name}){self.qualname}: {tags}"

    def __repr__(self) -> str:
        class_vars = [f"{k}={v}" for k, v in self.__dict__.items()]
        return f"{self.__class__.__name__}({', '.join(class_vars)})"
