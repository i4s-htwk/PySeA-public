from dash import Output, Input, State, callback, dcc, html, MATCH, ALL, ctx
from dash.exceptions import PreventUpdate

from backend.stores import StoreSelections

@callback(
    Output("div_selection", "children"),
    Output("view_edit_item", "data", allow_duplicate=True),

    Input("b_selections", "n_clicks"),

    State("store_selections", "data"),
    State("store_images", "data"),
    State("store_current_obj", "data"),
    prevent_initial_call=True
)
def render_selection(n_clicks, store_selection, store_images, current_obj):
    if not (ctx.triggered_id and n_clicks):
        raise PreventUpdate
    images = store_images["images"] if "images" in store_images else {}
    selection = StoreSelections.from_dict(store_selection or {})

    if current_obj in selection.items:
        selection_obj = selection.get_selection(current_obj)
        correct_answers = selection_obj.correct
        wrong_answers = selection_obj.incorrect
        b_new_correct_answer = html.Button("neue richtige Antwort", id={"id":"b_new_selection", "type":"correct"}, n_clicks=0,style={"marginLeft": "130px", "margin-bottom": "20px"})if selection_obj.type == "multipleChoice" else None

        div = html.Div([
            html.Div([
                html.Div("Richtige Antworten:"),
                html.Div([
                    html.Div([
                        dcc.Input(id={"type": "i_selection_correct", "index": i}, type="text", value=ans,
                                  style={"margin-left": "25px", "width": "300px"}),
                        (html.Img(src=f"/assets/{img_obj['href']}",
                                  style={"width": f"{img_obj['width']}px", "height": f"{img_obj['height']}px",
                                         "marginLeft": "20px"})
                         if (img_obj := next((img for img in images if img["id"] == ans or img["href"] == ans),
                                             None)) else html.Div("-"))
                    ], style={"display": "flex", "alignItems": "center", "marginBottom": "10px"})
                    for i, ans in enumerate(correct_answers)
                ], id="div_correct_answers"),
            ], style={"display": "flex", "alignItems": "flex-start"}),
            b_new_correct_answer,
            html.Div([
                html.Div("Falsche Antworten:"),
                html.Div([
                    html.Div([
                        dcc.Input(id={"type": "i_selection_wrong", "index": i}, type="text", value=ans, style={"margin-left": "25px", "width": "300px"}),
                        (html.Img(src=f"/assets/{img_obj['href']}", style={"width": f"{img_obj['width']}px", "height": f"{img_obj['height']}px", "marginLeft": "20px"})
                            if (img_obj := next((img for img in images if img["id"] == ans or img["href"] == ans), None)) else html.Div("-"))
                    ], style={"display": "flex", "alignItems": "center", "marginBottom": "10px"})
                    for i, ans in enumerate(wrong_answers)
                ], id="div_wrong_answers")
            ], style={"display": "flex", "alignItems": "flex-start"}),
            html.Div([
                dcc.Checklist(
                    id="cb_adjust_visibility",
                    options=[{"label": "Anzahl falscher Antworten begrenzen", "value": "on"}],
                    value=["on"] if selection_obj.adjust_visibility else [],
                    style={"marginLeft": "130px", "marginTop": "10px"}
                ),

                dcc.Dropdown(
                    id="dd_visible_wrong_count",
                    options=[
                        {"label": f"{i} anzeigen", "value": i}
                        for i in range(1, max(1, len(selection_obj.incorrect)) + 1)
                    ],
                    value=min(
                        selection_obj.visible_wrong_count,
                        max(1, len(selection_obj.incorrect))
                    ),
                    disabled=not selection_obj.adjust_visibility,
                    style={"width": "200px", "marginLeft": "15px"}
                )
            ], style={"display":"flex","flex-direction":"row", "alignItmes":"center"}),
            html.Button("Neue falsche Antwort", id={"id": "b_new_selection", "type": "incorrect"}, n_clicks=0, style={"marginLeft": "130px","margin-bottom": "20px"}),
            html.Button("x", id="b_delete_selection", n_clicks=0, style={"margin-top": "10px", "marginLeft":"15px"}),
            dcc.Dropdown(id="dd_selection_type", style={"display": "none"}),
            html.Button(id="b_add_selection", style={"display":"none"})
        ], style={"marginLeft": "280px", "marginTop": "80px"})
    else:
        div = html.Div([html.Div([dcc.Dropdown(id = "dd_selection_type", options=["single Choice", "multiple Choice"], value=selection.type, placeholder="Aufgabentyp", style={"width": "150px", "height": "10px", "fontSize": "12px"}),
                        html.Button("Auswahl hinzufügen", id="b_add_selection", style={"width": "250px", "marginTop":"8px", "marginLeft":"10px"})], style={"display":"flex","flex-direction":"row","marginLeft": "280px","marginTop" :"80px"}),
                        html.Button(id="b_delete_selection", style={"display":"none"}),
                        dcc.Input(id="i_selection_correct", style={"display":"none"}),
                        dcc.Checklist(id="cb_adjust_visibility", style={"display":"none"}),
                        dcc.Dropdown(id="dd_visible_wrong_count",style={"display":"none"})])

    return div, "selection"

@callback(
    Output("selections_is_saved", "data", allow_duplicate=True),
    Output("div_selection", "children", allow_duplicate=True),

    Input("selections_is_saved", "data"),
    State("store_selections", "data"),
    State("store_images", "data"),
    State("store_current_obj", "data"),
    prevent_initial_call=True
)
def rerender_answers(is_saved, store_selections, store_images, current_obj):
    if not ctx.triggered_id or not is_saved:
        raise PreventUpdate
    layout, *_ = render_selection(1, store_selections, store_images, current_obj)
    return False, layout

@callback(
    Output("store_selections", "data", allow_duplicate=True),
    Output("selections_is_saved", "data", allow_duplicate=True),

    Input("dd_selection_type", "value"),
    Input({"type": "i_selection_correct", "index": ALL}, "value"),
    Input({"type": "i_selection_wrong", "index": ALL}, "value"),
    Input("b_add_selection", "n_clicks"),
    Input({"id":"b_new_selection", "type":ALL}, "n_clicks"),
    Input("b_delete_selection", "n_clicks"),

    Input("cb_adjust_visibility", "value"),
    Input("dd_visible_wrong_count", "value"),

    State("store_selections", "data"),
    State("store_current_obj", "data"),
    prevent_initial_call=True
)
def save_answers(selection_type, i_correct_answer, i_incorrect_answers, add_selection, new_selection, delete_selection, adjust_visibility, visible_wrong_count, store_selections, current_obj):
    if not ctx.triggered_id:
        raise PreventUpdate

    selections = StoreSelections.from_dict(store_selections or {"items": {}, "type": "single Choice"})
    if ctx.triggered_id == "b_add_selection" and add_selection:
        if selection_type == "single Choice":
            selections.add_item(current_obj, "singleChoice")
        else:   selections.add_item(current_obj, "multipleChoice")

    selection_obj = selections.get_selection(current_obj)

    if isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get("type") == "i_selection_wrong":
        wrong_answers = selection_obj.incorrect
        index = ctx.triggered_id.get("index")
        wrong_answers[index] = i_incorrect_answers[index]
        selections.update_item(current_obj, new_incorrect= wrong_answers)
    elif isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get("type") == "i_selection_correct":
        correct_answers = selection_obj.correct
        index = ctx.triggered_id.get("index")
        correct_answers[index] = i_correct_answer[index]
        selections.update_item(current_obj, new_correct=correct_answers)
    elif isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get("id") == "b_new_selection":
        answer_type = ctx.triggered_id.get("type")
        selections.add_selection(current_obj, answer_type, None)
    elif ctx.triggered_id == "b_delete_selection" and delete_selection:
        del selections.items[current_obj]
    elif ctx.triggered_id == "dd_selection_type" and selection_type:
        selections.type = selection_type
    elif ctx.triggered_id == "cb_adjust_visibility":
        selection_obj.adjust_visibility = bool(adjust_visibility)
        selections.items[current_obj] = selection_obj

    elif ctx.triggered_id == "dd_visible_wrong_count" and visible_wrong_count:
        selection_obj.visible_wrong_count = visible_wrong_count
        selections.items[current_obj] = selection_obj

    return selections.to_dict(), True

