from __future__ import annotations

import ast
from pathlib import Path
from typing import Literal

from function_tagger.tag_class import TaggedFunction, UntaggedFunction

AstFunctionType = ast.FunctionDef | ast.AsyncFunctionDef
TagScanResult = tuple[list[TaggedFunction], list[UntaggedFunction]]
PlaceHolderType = tuple[
    dict[Path, list[TaggedFunction]], dict[Path, list[UntaggedFunction]]
]
OutputType = Literal["text", "json", "file"]
