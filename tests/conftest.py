from collections.abc import Callable
from typing import Any


def invoke(tool: Any, *args: Any, **kwargs: Any) -> Any:
    for attr in ("fn", "handler", "__wrapped__"):
        fn = getattr(tool, attr, None)
        if callable(fn):
            return fn(*args, **kwargs)
    if callable(tool):
        return tool(*args, **kwargs)
    raise TypeError(f"cannot invoke {tool!r}")


# re-export for type checkers
Callable = Callable
