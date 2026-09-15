from dash import html, callback, Output, Input


container_task_editor = html.Div(
    id="container_task_editor",
    children=[
        html.Div(id="div_general"),
        html.Div(id="div_answers"),
        html.Div(id="div_tables"),
        html.Div(id="div_selection"),
        html.Div(id="div_graphical_assignment"),
        html.Div(id="div_feedback"),
        html.Div(id="div_variables")
    ]
)

container_edit_item = html.Div(
    id="container_edit_item",
    children=[
        html.Div(id="div_menu_edit_item"),
        container_task_editor
    ]
)


def render_edit_task():
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.Button(
                        "Allgemein",
                        id="b_general",
                        style={
                            "width": "115px",
                            "marginRight": "20px",
                            "backgroundColor": "white",
                            "border": "1px solid lightgray",
                            "borderRadius": "7px"
                        }
                    ),

                    html.Button(
                        "Antworten",
                        id="b_answers",
                        style={
                            "width": "115px",
                            "backgroundColor": "white",
                            "border": "1px solid lightgray",
                            "borderRadius": "7px"
                        }
                    ),

                    html.Button(
                        "Tabellen",
                        id="b_tables",
                        style={
                            "width": "115px",
                            "backgroundColor": "white",
                            "border": "1px solid lightgray",
                            "borderRadius": "7px"
                        }
                    ),

                    html.Button(
                        "Auswahl",
                        id="b_selections",
                        style={
                            "width": "115px",
                            "backgroundColor": "white",
                            "border": "1px solid lightgray",
                            "borderRadius": "7px"
                        }
                    ),

                    html.Button(
                        "Grafische Zuordnung",
                        id="b_graphical_assignment",
                        style={
                            "width": "155px",
                            "backgroundColor": "white",
                            "border": "1px solid lightgray",
                            "borderRadius": "7px"
                        }
                    )
                ],
                style={
                    "display": "flex",
                    "gap": "10px"
                }
            ),

            html.Button(
                "Feedback",
                id="b_feedback",
                style={
                    "width": "115px",
                    "marginRight": "20px",
                    "backgroundColor": "white",
                    "border": "1px solid lightgray",
                    "borderRadius": "7px"
                }
            )
        ],
        style={
            "position": "fixed",
            "backgroundColor": "#f0f0f0",
            "top": "50px",
            "left": "250px",
            "boxShadow": (
                "0 2px 4px rgba(0, 0, 0, 0.1)"
            ),
            "width": "calc(100% - 250px)",
            "height": "50px",
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "paddingLeft": "10px",
            "paddingRight": "20px"
        }
    )


def render_edit_section():
    return html.Div(
        children=[
            html.Div(
                [
                    html.Button(
                        "Allgemein",
                        id="b_general",
                        style={
                            "width": "115px",
                            "marginRight": "20px",
                            "backgroundColor": "white",
                            "border": "1px solid lightgray",
                            "borderRadius": "7px"
                        }
                    ),

                    html.Button(
                        "Variablen",
                        id="b_excel_variables",
                        style={
                            "width": "115px",
                            "backgroundColor": "white",
                            "border": "1px solid lightgray",
                            "borderRadius": "7px"
                        }
                    ),

                    html.Button(
                        "Tabellen",
                        id="b_tables",
                        style={
                            "width": "115px",
                            "backgroundColor": "white",
                            "border": "1px solid lightgray",
                            "borderRadius": "7px"
                        }
                    )
                ],
                style={
                    "display": "flex",
                    "gap": "10px"
                }
            )
        ],
        style={
            "position": "fixed",
            "backgroundColor": "#f0f0f0",
            "top": "50px",
            "left": "250px",
            "boxShadow": (
                "0 2px 4px rgba(0, 0, 0, 0.1)"
            ),
            "width": "calc(100% - 250px)",
            "height": "50px",
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "paddingLeft": "10px",
            "paddingRight": "20px"
        }
    )


@callback(
    Output("div_answers", "style"),
    Output("div_feedback", "style"),
    Output("div_tables", "style"),
    Output("div_general", "style"),
    Output("div_selection", "style"),
    Output("div_graphical_assignment", "style"),
    Output("div_variables", "style"),

    Input("view_edit_item", "data"),

    prevent_initial_call=True
)
def layout_manager(state):
    return (
        (
            {"display": "block"}
            if state == "answers"
            else {"display": "none"}
        ),
        (
            {"display": "block"}
            if state == "feedback"
            else {"display": "none"}
        ),
        (
            {"display": "block"}
            if state == "tables"
            else {"display": "none"}
        ),
        (
            {"display": "block"}
            if state == "general"
            else {"display": "none"}
        ),
        (
            {"display": "block"}
            if state == "selection"
            else {"display": "none"}
        ),
        (
            {"display": "block"}
            if state == "graphical_assignment"
            else {"display": "none"}
        ),
        (
            {"display": "block"}
            if state == "variables"
            else {"display": "none"}
        )
    )