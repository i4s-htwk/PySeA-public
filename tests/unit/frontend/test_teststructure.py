from types import SimpleNamespace

import pytest
from dash.exceptions import PreventUpdate

import frontend.components.teststructure.teststructure as module

from .conftest import find_by_id


def test_render_sidebar_requires_data():
    with pytest.raises(PreventUpdate):
        module.render_sidebar(None, None)


def test_bearbeiten_requires_clicks():
    with pytest.raises(PreventUpdate):
        module.bearbeiten([], [], {}, {})


def test_bearbeiten_section_returns_section_menu(monkeypatch):
    section = SimpleNamespace(id="SECTION_1")
    structure = SimpleNamespace(get_object=lambda _: section)
    monkeypatch.setattr(module.TestStructure, "from_dict", lambda _: structure)
    monkeypatch.setattr(module, "ctx", SimpleNamespace(triggered_id={"type": "b-sektion-bearbeiten", "index": "SECTION_1"}))
    layout, current, view = module.bearbeiten([1], [], {}, {})
    assert find_by_id(layout, "b_excel_variables")
    assert (current, view) == ("SECTION_1", "edit_item")


def test_bearbeiten_task_returns_task_menu(monkeypatch):
    task = SimpleNamespace(id="TASK_1")
    structure = SimpleNamespace(get_object=lambda _: task)
    monkeypatch.setattr(module.TestStructure, "from_dict", lambda _: structure)
    monkeypatch.setattr(module, "ctx", SimpleNamespace(triggered_id={"type": "b-aufgabe-bearbeiten", "index": "TASK_1"}))
    layout, current, view = module.bearbeiten([], [1], {}, {})
    assert find_by_id(layout, "b_answers")
    assert (current, view) == ("TASK_1", "edit_item")
