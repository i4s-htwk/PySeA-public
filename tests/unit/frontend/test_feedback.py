from types import SimpleNamespace

import pytest
from dash import dcc
from dash.exceptions import PreventUpdate

import frontend.components.edit.feedback as module

from .conftest import find_by_id, find_by_type


def test_render_feedback_requires_click():
    with pytest.raises(PreventUpdate):
        module.render_feedback(0, {}, "TASK_1")


def test_render_feedback_for_missing_item_shows_initialize_button(monkeypatch):
    store = SimpleNamespace(items={})
    monkeypatch.setattr(module.StoreFeedback, "from_dict", lambda _: store)
    layout, state = module.render_feedback(1, {}, "TASK_1")
    assert state == "feedback"
    assert find_by_id(layout, "initialize_feedback")


def test_render_feedback_for_existing_item_uses_correct_text(monkeypatch):
    correct = SimpleNamespace(value="richtig", id="CORRECT")
    incorrect = [SimpleNamespace(value="falsch", id="INCORRECT_1", condition=None)]
    store = SimpleNamespace(items={"TASK_1": object()}, get_feedback_correct=lambda _: correct, get_feedback_incorrect=lambda _: incorrect,)
    monkeypatch.setattr(module.StoreFeedback, "from_dict", lambda _: store)

    layout, _ = module.render_feedback(1, {}, "TASK_1")

    assert find_by_id(layout, "feedback_correct")[0].value == "richtig"
    incorrect_inputs = [c for c in find_by_type(layout, dcc.Textarea) if isinstance(c.id, dict)]
    assert incorrect_inputs[0].value == "falsch"


def test_rerender_feedback_requires_saved_flag(monkeypatch):
    monkeypatch.setattr(module, "ctx", SimpleNamespace(triggered_id="feedback_is_saved"))
    with pytest.raises(PreventUpdate):
        module.rerender_feedback(False, {}, "TASK_1")
