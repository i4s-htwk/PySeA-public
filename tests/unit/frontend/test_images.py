from types import SimpleNamespace

import pytest
from dash.exceptions import PreventUpdate

import frontend.components.teststructure.images as module

from .conftest import find_by_id


def test_edit_images_requires_click():
    with pytest.raises(PreventUpdate):
        module.bearbeiten_bilder(0, {})


def test_rerender_images_requires_saved(monkeypatch):
    monkeypatch.setattr(module, "ctx", SimpleNamespace(triggered_id="images_is_saved"))
    with pytest.raises(PreventUpdate):
        module.rerender_configuration(False, {})
