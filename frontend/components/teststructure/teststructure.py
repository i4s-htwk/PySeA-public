from dash import Output, Input, State, callback, callback_context, ALL, ctx
from dash.exceptions import PreventUpdate

from backend.Section import Section
from backend.TestStructure import TestStructure
from backend.Task import Task
from backend.stores import StoreItemBody, StoreResponses, StoreTables, StoreFeedback, StoreSelections

from .layout import get_stack_content
from frontend.components.edit import render_edit_section, render_edit_task


@callback(
    Output("store_teststructure", "data"),
    Output("store_item_body", "data"),
    Output("store_responses", "data"),
    Output("store_tables", "data"),
    Output("store_feedback", "data"),
    Output("store_selections", "data"),
    Output("store_current_obj", "data"),

    Input("neue-sektion", "n_clicks"),
    Input("neue-aufgabe", "n_clicks"),
    Input("loeschen","n_clicks"),

    State("store_teststructure", "data"),
    State("store_item_body", "data"),
    State("store_responses", "data"),
    State("store_tables", "data"),
    State("store_feedback", "data"),
    State("store_selections", "data"),
    State("store_current_obj", "data"),
    prevent_initial_call=True)

def update_store(n_sektion, n_aufgabe,n_loeschen, test_structure, store_item_body, store_responses, store_tables, store_feedback, store_selections, current_obj):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    teststruktur = TestStructure.from_dict(test_structure or {})
    #current_obj = teststruktur.get_object(current_obj)

    item_body = StoreItemBody(items=store_item_body or {})
    responses = StoreResponses.from_dict(store_responses or {})
    tables = StoreTables.from_dict(store_tables or {})
    feedback = StoreFeedback.from_dict(store_feedback or {})
    selections = StoreSelections.from_dict(store_selections or {})
    trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger == "neue-sektion" and n_sektion and (len(teststruktur.list)==0 or len(teststruktur.list[-1].list_tasks)>=1):
        neue_id = "section"+str(len(teststruktur.list) + 1)
        sektion = Section("Sektion " + str(len(teststruktur.list) + 1), len(teststruktur.list) + 1, neue_id)
        teststruktur.append_section(sektion)
        item_body.add_item(sektion.id)
        tables.add_item(sektion.id)
        current_obj = sektion.id

    elif trigger == "neue-aufgabe" and n_aufgabe and len(teststruktur.list)>=1:
        aufgabe = teststruktur.list[-1].add_task()
        item_body.add_item(aufgabe.id)
        responses.add_item(aufgabe.id)
        tables.add_item(aufgabe.id)
        current_obj = aufgabe.id

    elif trigger == "loeschen" and n_loeschen:
        id_map={}
        current_obj_ts = teststruktur.get_object(current_obj)
        if "section" in current_obj:
            id_map = teststruktur.delete_section(current_obj_ts)
            current_obj = None
        elif "task" in current_obj and len(teststruktur.list[current_obj_ts.section_nr - 1].list_tasks)>1:
            id_map = teststruktur.list[current_obj_ts.section_nr - 1].delete_task(current_obj_ts)
            current_obj = None
        item_body.delete_item(id_map)
        responses.delete_item(id_map)
        tables.delete_item(id_map)
        feedback.delete_item(id_map)
        selections.delete_item(id_map)

    return teststruktur.to_dict(), item_body.items, responses.to_dict(), tables.to_dict(), feedback.to_dict(), selections.to_dict(), current_obj

@callback(
    Output("div_teststructure", "children"),
    Input("store_teststructure", "data"),
    Input("store_current_obj", "data"))
def render_sidebar(teststructure, current_obj):
    if not teststructure:
        raise PreventUpdate
    teststruktur = TestStructure.from_dict(teststructure)
    return get_stack_content(teststruktur.list, current_obj)

@callback(
    Output("div_menu_edit_item", "children"),
    Output("store_current_obj", "data", allow_duplicate=True),
    Output("view_edit", "data", allow_duplicate=True),

    Input({'type': 'b-sektion-bearbeiten', 'index': ALL}, 'n_clicks'),
    Input({'type': 'b-aufgabe-bearbeiten', 'index': ALL}, 'n_clicks'),
    State("store_teststructure", "data"),
    State("store_item_body", "data"),
    prevent_initial_call=True
)
def bearbeiten(n_clicks_sektionen, n_clicks_aufgaben, data, item_body):
    if not any(n_clicks_sektionen) and not any(n_clicks_aufgaben):
        raise PreventUpdate

    triggered_id = ctx.triggered_id
    if not triggered_id:
        raise PreventUpdate

    teststruktur = TestStructure.from_dict(data)
    index = triggered_id.get("index", "unbekannt")
    current_obj = teststruktur.get_object(index)

    result = None
    if triggered_id.get("type") == "b-sektion-bearbeiten":
        result = render_edit_section()
    elif triggered_id.get("type") == "b-aufgabe-bearbeiten":
        result = render_edit_task()
    return result, current_obj.id, "edit_item"