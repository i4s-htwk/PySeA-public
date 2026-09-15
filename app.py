from dash import html, dcc, Dash
import os

from frontend.components.menubar import menubar, container_menu
from frontend.components.edit import variables_excel
import frontend.components.menubar.callbacks
from frontend.components.teststructure import images, configuration, teststructure, variants, layout

hidden_container = {"container_answer_list"}
hidden_buttons = {"b_load_test", "b_new_table", "b_show_tables", "b_tables", "b_new_response", "b_new_excel_response", "b_answers", "b_general", "b_load_images", "b_new_excel_file", "b_acc_from_excel_file", "dropdown_acc_responses", "b_feedback", "b_selections", "initialize_feedback", "add_incorrect_feedback", "b_new_selection", "b_add_selection", "b_new_variable", "dd_table_type", "cb_acc_from_excel", "dd_navigation_mode", "cb_keep_responses", "cb_use_point_deduction", "b_new_variants_dependent_image", "b_use_excel_variables", "b_new_excel_variable", "b_excel_variables"}
hidden_inputs = {"path_images", "path_export", "path_excel_file", "i_test_title", "i_title", "path_load_test", "i_acc_answers", "feedback_correct", "i_selection_correct", "i_point_deduction_per_attempt", "i_min_score_percentage", "i_feedback_correct_variants", "i_feedback_incorrect_variants", "i_feedback_correct_config", "i_feedback_incorrect_config", "i_pass_score_percentage", "i_points_per_gap_tasks", "i_points_per_selection_tasks", "i_points_task"}
hidden_i_textareas = {"i_text"}
hidden_dropdowns = {"excel_variable_page", "excel_variable_doc","cb_adjust_visibility","dd_visible_wrong_count"}

stores_is_saved = {"tables_is_saved", "configuration_is_saved", "answers_is_saved", "feedback_is_saved", "selections_is_saved", "variants_is_saved", "images_is_saved", "general_is_saved", "variables_excel_is_saved"}

app = Dash(__name__, suppress_callback_exceptions=True)
app.layout = html.Div(
    style={"fontSize": "12px","fontFamily": "Arial"},
    children = [
    dcc.Store(id="store_teststructure", data={}),
    dcc.Store(id="store_images", data={"path_images":"","images":[]}),
    *[dcc.Store(id=name, data=False) for name in stores_is_saved],

    dcc.Store(id="store_current_obj"),
    dcc.Store(id="view_edit"),
    dcc.Store(id="view_edit_item"),

    dcc.Store(id="store_item_body"),
    dcc.Store(id="store_responses"),
    dcc.Store(id="store_tables"),
    dcc.Store(id="store_feedback"),
    dcc.Store(id="store_selections"),
    dcc.Store(id="store_configurations"),
    dcc.Store(id="store_variants"),
    dcc.Store(id="store_matchings"),
    dcc.Store(id="store_graphical_assignment"),

    menubar,
    container_menu,

    html.Div(id="hidden-elements",children=[
        *[html.Div(id=name) for name in hidden_container],
        *[html.Button(id=name, style={"display":"none"}) for name in hidden_buttons],
        *[dcc.Input(id=name, style={"display":"none"}) for name in hidden_inputs],
        *[dcc.Textarea(id=name, style={"display":"none"}) for name in hidden_i_textareas],
        *[dcc.Dropdown(id=name, style={"display":"none"}) for name in hidden_dropdowns],
    ])
])


# Stylesheet für Schriftgrößen der Buttons
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>PySeA</title>
        {%favicon%}
        {%css%}
        <style>
            button {
                font-size: 12px;
                font-family: Arial;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    try:
        app.run(debug=True, dev_tools_hot_reload=False)
    finally:
        os.makedirs("frontend/assets", exist_ok=True)
        for f in os.listdir("frontend/assets"):
            pfad = os.path.join("frontend/assets", f)
            if os.path.isfile(pfad):
                os.remove(pfad)


#console.log(document.getElementsByTagName("*").length);


