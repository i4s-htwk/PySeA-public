from types import SimpleNamespace

import pytest
from dash.exceptions import PreventUpdate

import frontend.components.edit.selection as module

from .conftest import find_by_id


def test_render_selection_requires_callback_trigger(monkeypatch):
    monkeypatch.setattr(module, "ctx", SimpleNamespace(triggered_id=None))
    with pytest.raises(PreventUpdate):
        module.render_selection(1, {}, {}, "TASK_1")


def test_render_selection_missing_item_contains_add_button(monkeypatch):
    selections = SimpleNamespace(items={}, type="single Choice")
    monkeypatch.setattr(module, "ctx", SimpleNamespace(triggered_id="b_selections"))
    monkeypatch.setattr(module.StoreSelections, "from_dict", lambda _: selections)
    layout, state = module.render_selection(1, {}, {"images": []}, "TASK_1")
    assert state == "selection"
    assert find_by_id(layout, "b_add_selection")
    assert find_by_id(layout, "dd_selection_type")


def test_rerender_selection_requires_saved(monkeypatch):
    monkeypatch.setattr(module, "ctx", SimpleNamespace(triggered_id="selections_is_saved"))
    with pytest.raises(PreventUpdate):
        module.rerender_answers(False, {}, {}, "TASK_1")
