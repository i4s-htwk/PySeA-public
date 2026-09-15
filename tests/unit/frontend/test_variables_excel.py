from types import SimpleNamespace

import pytest
from dash.exceptions import PreventUpdate

import frontend.components.edit.variables_excel as module

from .conftest import find_by_id


def test_render_excel_variables_requires_click():
    with pytest.raises(PreventUpdate):
        module.render_excel_variables(0, {}, "SECTION_1", {})


def test_render_excel_variables_without_configuration_shows_initialize(monkeypatch):
    current = SimpleNamespace(excel_variables=None)
    structure = SimpleNamespace(get_object=lambda _object_id: current)
    configuration = SimpleNamespace(path_excel_files=[])

    monkeypatch.setattr(module.TestStructure, "from_dict", lambda _: structure)
    monkeypatch.setattr(module.StoreConfigurations, "from_dict", lambda _: configuration)

    result, state = module.render_excel_variables(1, {}, "SECTION_1", {})
    assert state == "variables"
    assert find_by_id(result, "b_initialize_excel_variables")


def test_page_loader_rejects_missing_file(tmp_path):
    with pytest.raises(PreventUpdate):
        module.lade_seitenoptionen(str(tmp_path / "missing.xlsx"), False)


def test_rerender_requires_saved_flag(monkeypatch):
    monkeypatch.setattr(module, "ctx", SimpleNamespace(triggered_id="variables_excel_is_saved"))
    with pytest.raises(PreventUpdate):
        module.rerender_excel_variables(False, {}, "SECTION_1", {})
