import ast

from dash import ALL, Input, Output, State, callback, ctx, dcc, html
from dash.exceptions import PreventUpdate

from backend.stores import StoreFeedback, StoreResponses


def condition_to_text(condition):
    """
    Wandelt eine im Backend gespeicherte Condition in einen Text für
    das Eingabefeld um.

    Beispiele:
        None                -> ""
        2                   -> "2"
        [2, 4]              -> "[2, 4]"
        Response            -> "RESPONSE_1"
        ExcelResponse       -> "EXCEL_RESPONSE_1"
    """
    if condition is None:
        return ""

    if isinstance(condition, int):
        return str(condition)

    if isinstance(condition, list):
        return str(condition)

    if hasattr(condition, "id"):
        return condition.id

    return ""


def find_response(store_responses, current_obj, response_id):
    """
    Sucht eine Response oder ExcelResponse der aktuellen Aufgabe
    anhand ihrer ID.
    """
    response_item = store_responses.get_item(current_obj)

    if response_item is None:
        return None

    for response in response_item.responses:
        if response.id == response_id:
            return response

    if response_item.excel_responses is not None:
        for response in response_item.excel_responses.responses:
            if response.id == response_id:
                return response

    return None


def text_to_condition(
    value,
    store_responses,
    current_obj,
    previous_condition=None
):
    """
    Wandelt den Text aus dem Condition-Eingabefeld in einen vom Backend
    unterstützten Condition-Typ um.

    Unterstützte Eingaben:

        leer
            Keine explizite Condition. Die Feedbackstufe wird anhand
            ihrer Reihenfolge verwendet.

        2
            Feedback ab dem zweiten Versuch.

        [2, 4]
            Feedback vom zweiten bis einschließlich vierten Versuch.

        RESPONSE_1
            Feedback, wenn RESPONSE_1 falsch beantwortet wurde.

        {RESPONSE_1}
            Alternative Schreibweise für RESPONSE_1.

        EXCEL_RESPONSE_1
            Feedback, wenn EXCEL_RESPONSE_1 falsch beantwortet wurde.
    """
    if value is None or not str(value).strip():
        return None

    condition_text = str(value).strip()

    # Die ID darf optional wie ein Platzhalter in geschweiften
    # Klammern eingegeben werden.
    if (
        condition_text.startswith("{")
        and condition_text.endswith("}")
    ):
        condition_text = condition_text[1:-1].strip()

    response = find_response(
        store_responses,
        current_obj,
        condition_text
    )

    if response is not None:
        return response

    try:
        parsed_value = ast.literal_eval(condition_text)
    except (ValueError, SyntaxError):
        # Eine noch nicht vollständig eingegebene oder ungültige Condition
        # überschreibt die bisher gespeicherte Condition nicht.
        return previous_condition

    # bool ist in Python eine Unterklasse von int, soll hier aber nicht
    # als Versuchsnummer akzeptiert werden.
    if isinstance(parsed_value, bool):
        return previous_condition

    if isinstance(parsed_value, int):
        if parsed_value < 1:
            return previous_condition

        return parsed_value

    if (
        isinstance(parsed_value, list)
        and len(parsed_value) == 2
        and all(
            isinstance(item, int) and not isinstance(item, bool)
            for item in parsed_value
        )
    ):
        lower_bound, upper_bound = parsed_value

        if lower_bound < 1 or upper_bound < lower_bound:
            return previous_condition

        return [lower_bound, upper_bound]

    return previous_condition


@callback(
    Output("div_feedback", "children"),
    Output("view_edit_item", "data", allow_duplicate=True),

    Input("b_feedback", "n_clicks"),

    State("store_feedback", "data"),
    State("store_current_obj", "data"),

    prevent_initial_call=True
)
def render_feedback(n_clicks, store_feedback, current_obj):
    if not n_clicks:
        raise PreventUpdate

    feedback = StoreFeedback.from_dict(store_feedback or {})

    correct_fb = ""
    incorrect_fbs = []
    incorrect_conditions = []

    style_fb = {"display": "none"}
    style_b = {"display": "block"}

    if current_obj in feedback.items:
        correct_feedback = feedback.get_feedback_correct(current_obj)

        if correct_feedback is not None:
            correct_fb = correct_feedback.value or ""

        incorrect_feedbacks = (
            feedback.get_feedback_incorrect(current_obj) or []
        )

        incorrect_fbs = [
            incorrect_feedback.value or ""
            for incorrect_feedback in incorrect_feedbacks
        ]

        incorrect_conditions = [
            condition_to_text(incorrect_feedback.condition)
            for incorrect_feedback in incorrect_feedbacks
        ]

        style_fb = {"display": "block"}
        style_b = {"display": "none"}

    result = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H4("Korrektes Feedback"),

                            html.Div(
                                [
                                    dcc.Textarea(
                                        id="feedback_correct",
                                        value=correct_fb,
                                        placeholder=(
                                            "Feedback, das bei richtiger "
                                            "Bewertung angezeigt wird"
                                        ),
                                        style={
                                            "width": "90%",
                                            "height": 100,
                                            "resize": "vertical",
                                            "fontSize": 16,
                                            "marginLeft": "10px"
                                        }
                                    )
                                ],
                                style={
                                    "display": "flex",
                                    "flexDirection": "row"
                                }
                            )
                        ],
                        style={
                            "marginTop": "20px"
                        }
                    ),

                    html.Div(
                        [
                            html.H4("Falsche Feedbacks"),

                            html.Div(
                                [
                                    *[
                                        html.Div(
                                            [
                                                dcc.Textarea(
                                                    id={
                                                        "type": "feedback_incorrect",
                                                        "index": i
                                                    },
                                                    value=feedback_value,
                                                    placeholder=(
                                                        "Feedback, das bei falscher "
                                                        "Bewertung als Stufe "
                                                        f"{i + 1} angezeigt wird"
                                                    ),
                                                    style={
                                                        "width": "90%",
                                                        "height": 100,
                                                        "resize": "vertical",
                                                        "fontSize": 16,
                                                        "marginBottom": "6px"
                                                    }
                                                ),

                                                dcc.Input(
                                                    id={
                                                        "type": "feedback_condition",
                                                        "index": i
                                                    },
                                                    value=incorrect_conditions[i],
                                                    type="text",
                                                    placeholder=(
                                                        "Condition, z. B. 2, "
                                                        "[2, 4] oder RESPONSE_1"
                                                    ),
                                                    debounce=True,
                                                    style={
                                                        "width": "90%",
                                                        "height": "32px",
                                                        "fontSize": 15,
                                                        "marginBottom": "15px",
                                                        "boxSizing": "border-box"
                                                    }
                                                )
                                            ],
                                            style={
                                                "display": "flex",
                                                "flexDirection": "column",
                                                "marginLeft": "10px"
                                            }
                                        )
                                        for i, feedback_value
                                        in enumerate(incorrect_fbs)
                                    ]
                                ],
                                style={
                                    "display": "flex",
                                    "flexDirection": "column"
                                }
                            )
                        ]
                    ),

                    html.Button(
                        "Neue Feedbackstufe",
                        id="add_incorrect_feedback",
                        style={
                            "marginLeft": "10px"
                        }
                    )
                ],
                style=style_fb
            ),

            html.Div(
                [
                    html.Button(
                        "Feedback hinzufügen",
                        id="initialize_feedback",
                        style={
                            "width": "250px",
                            "padding": "0",
                            "marginTop": "20px"
                        }
                    )
                ],
                style=style_b
            )
        ],
        style={
            "marginLeft": "260px",
            "marginTop": "60px",
            "paddingLeft": "20px"
        }
    )

    return result, "feedback"


@callback(
    Output(
        "feedback_is_saved",
        "data",
        allow_duplicate=True
    ),
    Output(
        "div_feedback",
        "children",
        allow_duplicate=True
    ),

    Input("feedback_is_saved", "data"),

    State("store_feedback", "data"),
    State("store_current_obj", "data"),

    prevent_initial_call=True
)
def rerender_feedback(
    is_saved,
    store_feedback,
    current_obj
):
    if not ctx.triggered_id or not is_saved:
        raise PreventUpdate

    layout, _ = render_feedback(
        1,
        store_feedback,
        current_obj
    )

    return False, layout


@callback(
    Output(
        "store_feedback",
        "data",
        allow_duplicate=True
    ),
    Output(
        "feedback_is_saved",
        "data",
        allow_duplicate=True
    ),

    Input("feedback_correct", "value"),

    Input(
        {
            "type": "feedback_incorrect",
            "index": ALL
        },
        "value"
    ),

    Input(
        {
            "type": "feedback_condition",
            "index": ALL
        },
        "value"
    ),

    Input("add_incorrect_feedback", "n_clicks"),
    Input("initialize_feedback", "n_clicks"),

    State("store_feedback", "data"),
    State("store_responses", "data"),
    State("store_current_obj", "data"),

    prevent_initial_call=True
)
def save_feedback(
    correct_value,
    incorrect_values,
    condition_values,
    add_incorrect,
    init_feedback,
    store_feedback,
    store_responses,
    current_obj
):
    triggered_id = ctx.triggered_id

    if (
        triggered_id not in (
            "initialize_feedback",
            "add_incorrect_feedback",
            "feedback_correct"
        )
        and not isinstance(triggered_id, dict)
    ):
        raise PreventUpdate

    feedback = StoreFeedback.from_dict(store_feedback or {})

    responses = StoreResponses.from_dict(store_responses or {})

    if (
        triggered_id == "initialize_feedback"
        and init_feedback
    ):
        if current_obj not in feedback.items:
            feedback.add_item(current_obj)

        if not feedback.get_feedback_incorrect(current_obj):
            feedback.add_feedback_incorrect(
                current_obj,
                ""
            )

    elif triggered_id == "feedback_correct":
        if current_obj not in feedback.items:
            raise PreventUpdate

        feedback.set_feedback_correct(
            current_obj,
            correct_value or ""
        )

    elif (
        isinstance(triggered_id, dict)
        and triggered_id.get("type") in (
            "feedback_incorrect",
            "feedback_condition"
        )
    ):
        if current_obj not in feedback.items:
            raise PreventUpdate

        incorrect_feedbacks = (
            feedback.get_feedback_incorrect(current_obj)
        )

        for i, incorrect_feedback in enumerate(
            incorrect_feedbacks
        ):
            if i < len(incorrect_values):
                incorrect_feedback.value = (
                    incorrect_values[i] or ""
                )

            if i < len(condition_values):
                incorrect_feedback.condition = text_to_condition(
                    value=condition_values[i],
                    store_responses=responses,
                    current_obj=current_obj,
                    previous_condition=incorrect_feedback.condition
                )

    elif (
        triggered_id == "add_incorrect_feedback"
        and add_incorrect
    ):
        feedback.add_feedback_incorrect(
            current_obj,
            ""
        )

    return feedback.to_dict(), True