"""Parse source files without writing __pycache__."""
from __future__ import annotations
import ast
from pathlib import Path
import sys
for value in sys.argv[1:]:
    ast.parse(Path(value).read_text(encoding="utf-8"), filename=value)
print(f"AST_PARSE_OK files={len(sys.argv) - 1}")
