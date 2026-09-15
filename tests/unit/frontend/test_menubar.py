from types import SimpleNamespace

import pytest
from dash.exceptions import PreventUpdate

import frontend.components.menubar.callbacks as callbacks
import frontend.components.menubar.layout as layout

from .conftest import find_by_id, ids


def test_menubar_layout_contains_primary_actions():
    assert set(ids(layout.menubar)) >= {"b_edit_test", "b_div_load_test", "b_export_test"}


def test_menu_container_contains_editor_and_load_area():
    assert find_by_id(layout.container_menu, "div_edit_test")
    assert find_by_id(layout.container_menu, "div_load_test")


def test_edit_test_returns_sidebar_and_visibility(monkeypatch):
    structure = SimpleNamespace(list=[], get_object=None)
    monkeypatch.setattr(callbacks.TestStructure, "from_dict", lambda _: structure)
    sidebar, edit_style, load_style = callbacks.edit_test(1, {})
    assert edit_style == {"display": "block"}
    assert load_style == {"display": "none"}
    assert find_by_id(sidebar, "b_variants")


def test_load_dialog_requires_click():
    with pytest.raises(PreventUpdate):
        callbacks.div_load_test(0)


def test_load_dialog_contains_path_and_button():
    dialog, load_style, edit_style = callbacks.div_load_test(1)
    assert find_by_id(dialog, "path_load_test")
    assert find_by_id(dialog, "b_load_test")
    assert load_style == {"display": "block"}
    assert edit_style == {"display": "none"}


def test_load_test_requires_click():
    with pytest.raises(PreventUpdate):
        callbacks.load_test(0, "file.json")

def test_create_test_uses_configured_export_path(monkeypatch):
    store = SimpleNamespace(create_test=lambda path: setattr(store, "created_path", path))
    monkeypatch.setattr(callbacks.TestStore, "from_dict", lambda _: store)

    callbacks.test_erstellen(
        n_clicks=1,
        store_test_structure={},
        store_item_body={},
        store_images={},
        store_responses={},
        store_tables={},
        store_selections={},
        store_matchings={},
        store_graphical_assignment={},
        store_feedback={},
        store_configurations={
            "path_export": "/tmp/out"
        },
        store_variants={},)
    assert store.created_path == "/tmp/out"