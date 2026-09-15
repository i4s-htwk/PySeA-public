from dash import Output, Input, State, callback, html, dcc, ALL, ctx
from dash.exceptions import PreventUpdate

from backend.stores import StoreConfigurations

@callback(
    Output("div_config", "children"),
    Output("view_edit", "data", allow_duplicate=True),

    Input("configuration", "n_clicks"),
    State("store_configurations", "data"),
    prevent_initial_call=True
)
def bearbeiten_konfig(n_clicks_konfig, store_configurations):
    if not n_clicks_konfig:
        raise PreventUpdate

    configurations = StoreConfigurations.from_dict(store_configurations or {})

    return html.Div([
        html.Div([
            html.H3("Titel des Tests", style={"marginRight": "10px", "minWidth": "180px"}),
            dcc.Input(id="i_test_title", type="text", placeholder="Testtitel", value=configurations.title, style={"width": "300px"})
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "20px"}),
        html.Div([
            html.H4("Pfad für den Export", style={"marginLeft": "10px", "marginRight": "10px", "minWidth": "180px"}),
            dcc.Input(id="path_export", type="text", placeholder="Export path_file", value=configurations.path_export,
                      style={"width": "350px"})
        ], style={"display": "flex", "alignItems": "center"}),
        html.Div([
            html.H4("Exceldateien einladen", style={"marginLeft": "10px", "marginRight": "5px", "minWidth": "180px"}),
            html.Div([html.Div([
                    dcc.Input(id={"type": "b_path_excel_file", "index": i}, type="text", placeholder="Pfad zur Exceldatei", value=path, style={"width": "350px", "marginTop": "15px"}),
                    html.Button("x", id={"type": "b_remove_excel_file", "index": i}, style={"marginLeft": "10px", "marginTop": "15px","marginRight":"20px" })
                ], style={"display": "flex", "alignItems": "center"})
                for i, path in enumerate(configurations.path_excel_files or [])
            ],
                style={"display": "flex", "flexDirection": "column", "gap": "5px"}),
            html.Button("neue Exceldatei", id="b_new_excel_file", style={"marginTop":"15px"})
        ], style={"display": "flex", "alignItems": "flex-start", "border": "0.5px solid black", "padding": "5px"}),
        render_answers_acc(configurations.answer_acc),
        render_point_deduction(configurations.point_deduction),
        render_point_distribution(configurations.point_distribution),
        render_advanced_settings(configurations.advanced_settings),
        render_feedback(configurations.feedback, configurations.pass_score_percentage)
    ], style={"marginLeft": "260px", "paddingLeft": "20px"}), "config"

def render_answers_acc(answer_acc):
    if answer_acc.selection == "exact":
        i_acc_answers = dcc.Input(id="i_acc_answers", style={"display": "none"})
        unit = ""
    elif answer_acc.selection == "relative":
        i_acc_answers = dcc.Input(id="i_acc_answers", type="text", placeholder="Abweichung in %", value=answer_acc.relative, style={"marginLeft": "10px", "Width": "70px", "height":"18px"})
        unit = "  %"
    else:
        i_acc_answers = dcc.Input(id="i_acc_answers", type="text", placeholder="Abweichung", value=answer_acc.absolute, style={"marginLeft": "10px", "Width": "70px", "height":"18px"})
        unit = ""

    return html.Div([
            html.H4("Genauigkeit der Lücken", style={"marginLeft": "10px", "marginBottom": "10px"}),
                html.Div([
                    html.Div([
                        dcc.Dropdown(
                            id="dropdown_acc_responses",
                            options=[
                                {"label": "Relativ", "value": "relative"},
                                {"label": "Absolut", "value": "absolute"},
                                {"label": "Exakt", "value": "exact"}
                            ],
                            value=answer_acc.selection,
                            clearable=False,
                            style={"width": "150px", "marginTop":"5px"}
                        ),
                    i_acc_answers , unit], style={"display": "flex", "flexDirection": "flex-start", "alignItems": "center"})
                ], style={"display": "flex", "flexDirection": "column", "marginLeft":"50px"}),
        ], style={"display": "flex", "alignItems": "flex-start", "border": "0.5px solid black", "padding": "5px", "marginTop": "15px"})

def render_point_deduction(point_deduction):
    checkbox = dcc.Checklist(
        id="cb_use_point_deduction",
        options=[{"label": "Punktabzug pro Lösungsversuch", "value": "true"}],
        value=[] if not point_deduction.is_used else ["true"], style={"marginTop":"15px", "paddingBottom":"10px"})

    if point_deduction.is_used:
            point_deduction_per_attempt = html.Div([
                "Punktabzug pro Lösungsversuch:",
                dcc.Input(id="i_point_deduction_per_attempt", value=point_deduction.point_deduction_per_attempt, style={"marginLeft":"100px", "width":"80px"})
            ], style={"paddingBottom":"10px"})
            min_score_percantage = html.Div([
                "Mindestpunktzahl bei vollständig richtiger Lösung:",
                dcc.Input(id="i_min_score_percentage", value=point_deduction.min_score_percentage,  style={"marginLeft":"14px", "marginRight":"10px", "width":"80px"}),
                "%"
            ], style={"paddingBottom":"10px"})
    else:
            point_deduction_per_attempt = dcc.Input(id="i_point_deduction_per_attempt", style={"display":"none"})
            min_score_percantage = dcc.Input(id="i_min_score_percentage", style={"display":"none"})

    return html.Div([
        html.H4("Punktabzüge", style={"marginLeft": "10px", "marginBottom": "10px"}),
        html.Div([
            checkbox,
            point_deduction_per_attempt,
            min_score_percantage],
        style={"display": "flex", "flex-direction":"column", "marginLeft":"110px"}),
    ], style = {"display": "flex", "alignItems": "flex-start", "border": "0.5px solid black", "padding": "5px", "marginTop": "15px"})

def render_point_distribution(point_distribution):
    return html.Div([
        html.H4("Punkteverteilung", style={"marginLeft": "10px", "marginBottom": "10px"}),
        html.Div([
            html.Div([
                "Punkte pro Lücke:", dcc.Input(id="i_points_per_gap", value=point_distribution["gap"], style={"marginLeft":"70px", "width":"80px"})], style={"paddingBottom":"10px"}),
            html.Div([
                "Punkte pro Auswahlaufgabe", dcc.Input(id="i_points_per_selection", value=point_distribution["selection"], style={"marginLeft":"16px", "width":"80px"})])],
            style={"display": "flex", "flex-direction": "column", "marginLeft": "87px" ,"marginTop":"15px"})],
        style={"display": "flex", "alignItems": "flex-start", "border": "0.5px solid black", "padding": "5px",
              "marginTop": "15px"})

def render_advanced_settings(advanced_settings):
    return html.Div([
        html.H4("Erweiterte Einstellungen", style={"marginLeft": "10px", "marginBottom": "10px"}),
        html.Div([
            dcc.Dropdown(
                id="dd_navigation_mode",
                options=[
                    {"label": "Nicht linear", "value": "nonlinear"},
                    {"label": "Linear", "value": "linear"},
                    {"label": "Linear mit Testwegsteuerung", "value": "test_path_control"}
                ],
                value=advanced_settings.navigation_mode,
                clearable=False,
                style={"width": "250px", "marginBottom": "5px"}
            ),
            dcc.Checklist(id="cb_keep_responses", options=[{"label": "Antworten behalten", "value": "true"}], value=[] if not advanced_settings.keep_responses else ["true"], style={"paddingBottom": "10px"})],
            style={"display": "flex", "flex-direction": "column", "marginLeft": "45px" ,"marginTop":"15px"})],
        style={"display": "flex", "alignItems": "flex-start", "border": "0.5px solid black", "padding": "5px",
              "marginTop": "15px"})

def render_feedback(feedback, pass_score_percentage):
    return html.Div([
        html.Div([html.H4("Mindestpunktzahl zum Bestehen: ", style={"marginLeft": "10px",}), dcc.Input(id="i_pass_score_percentage", value=pass_score_percentage, style={"marginLeft":"10px", "width":"80px"})],
                 style={"display":"flex", "flex-direction":"row", "alignItems":"center", "marginBottom":"10px"}),
        html.Div([
            html.H4("Feedback Bestanden", style={"marginLeft": "10px", "marginTop":"0"}),
            dcc.Textarea(id="i_feedback_correct_config", value=feedback["feedback_correct"].value, style={'width': '100%', 'height': 100, 'resize': 'vertical', 'fontSize': 16, "marginLeft":"27px"})],
        style={"display":"flex", "flex-direction":"row", "marginBottom":"20px"}),
        html.Div([
            html.H4("Feedback nicht Bestanden", style={"marginLeft": "10px", "marginTop":"0"}),
            dcc.Textarea(id="i_feedback_incorrect_config", value=feedback["feedback_incorrect"].value, style={'width': '100%', 'height': 100, 'resize': 'vertical', 'fontSize': 16})],
        style={"display":"flex", "flex-direction":"row"})
        ],
        style={"display": "flex", "flex-direction":"column", "border": "0.5px solid black", "padding": "5px", "marginTop": "15px"})

@callback(
Output("configuration_is_saved", "data", allow_duplicate=True),
    Output("div_config", "children", allow_duplicate=True),

    Input("configuration_is_saved", "data"),
    State("store_configurations", "data"),
    prevent_initial_call=True)
def rerender_configuration(is_saved, store_configurations):
    if not ctx.triggered_id or not is_saved:
        raise PreventUpdate
    layout, *_ = bearbeiten_konfig(1, store_configurations)
    return False, layout


@callback(
    Output("store_configurations", "data", allow_duplicate=True),
    Output("configuration_is_saved", "data", allow_duplicate=True),

    Input("i_test_title", "value"),
    Input({"type": "b_path_excel_file", "index": ALL}, "value"),
    Input("path_export", "value"),
    Input("b_new_excel_file", "n_clicks"),
    Input({"type": "b_remove_excel_file", "index": ALL}, "n_clicks"),
    Input("dropdown_acc_responses", "value"),
    Input("i_acc_answers", "value"),

    Input("cb_use_point_deduction", "value"),
    Input("i_point_deduction_per_attempt", "value"),
    Input("i_min_score_percentage", "value"),

    Input("i_points_per_gap", "value"),
    Input("i_points_per_selection", "value"),

    Input("dd_navigation_mode", "value"),
    Input("cb_keep_responses", "value"),

    Input("i_feedback_correct_config", "value"),
    Input("i_feedback_incorrect_config", "value"),
    Input("i_pass_score_percentage", "value"),

    State("store_configurations", "data"),
    prevent_initial_call=True
)
def speichere_testconfiguration(titel, path_excel_file, path_export, new_excel_file, remove_excel_file, d_acc_answers, i_acc_answers,
                                use_point_deduction, point_deduction_per_attempt, min_score_percentage, points_per_gap, points_per_selection,
                                naviagtion_mode, keep_responses, feedback_correct, feedback_incorrect, pass_score_percentage,
                                store_configurations):

    configurations = StoreConfigurations.from_dict(store_configurations or {})
    configurations.answer_acc.selection = d_acc_answers or "relative"

    if ctx.triggered_id == "i_test_title":
        configurations.title = titel or ""
    elif ctx.triggered_id == "path_export":
        configurations.path_export = path_export or ""
    elif isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get("type") == "b_path_excel_file":
        configurations.path_excel_files = path_excel_file or []
    elif ctx.triggered_id == "i_acc_answers":
        if configurations.answer_acc.selection == "relative":
            configurations.answer_acc.relative = i_acc_answers
        else:
            configurations.answer_acc.absolute = i_acc_answers
    elif ctx.triggered_id == "b_new_excel_file":
        configurations.path_excel_files.append("")
    elif isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get("type") == "b_remove_excel_file":
        index = ctx.triggered_id.get("index")
        configurations.path_excel_files.pop(index)
    elif ctx.triggered_id == "cb_use_point_deduction":
        configurations.point_deduction.is_used = "true" in use_point_deduction
    elif ctx.triggered_id == "i_point_deduction_per_attempt":
        configurations.point_deduction.point_deduction_per_attempt = point_deduction_per_attempt
    elif ctx.triggered_id == "i_min_score_percentage":
        configurations.point_deduction.min_score_percentage = min_score_percentage
    elif ctx.triggered_id == "i_points_per_gap":
        configurations.point_distribution["gap"] = points_per_gap
    elif ctx.triggered_id == "i_points_per_selection":
        configurations.point_distribution["selection"] = points_per_selection
    elif ctx.triggered_id == "dd_navigation_mode":
        configurations.advanced_settings.navigation_mode = naviagtion_mode
    elif ctx.triggered_id == "cb_keep_responses":
        configurations.advanced_settings.keep_responses = "true" in keep_responses
    elif ctx.triggered_id == "i_feedback_correct_config":
        configurations.set_feedback("correct", feedback_correct)
    elif ctx.triggered_id == "i_feedback_incorrect_config":
        configurations.set_feedback("incorrect", feedback_incorrect)
    elif ctx.triggered_id == "i_pass_score_percentage":
        configurations.pass_score_percentage = pass_score_percentage

    return configurations.to_dict(), True
