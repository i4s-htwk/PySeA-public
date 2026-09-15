from __future__ import annotations

from collections.abc import Iterable


def walk(component):
    """Yield a Dash component tree recursively."""
    if component is None:
        return
    yield component
    children = getattr(component, "children", None)
    if children is None:
        return
    if not isinstance(children, (list, tuple)):
        children = [children]
    for child in children:
        if hasattr(child, "children") or hasattr(child, "id"):
            yield from walk(child)


def find_by_id(component, component_id):
    return [c for c in walk(component) if getattr(c, "id", None) == component_id]


def find_by_type(component, cls):
    return [c for c in walk(component) if isinstance(c, cls)]


def ids(component):
    return [getattr(c, "id", None) for c in walk(component) if getattr(c, "id", None) is not None]
