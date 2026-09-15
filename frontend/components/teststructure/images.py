import os
import shutil
from PIL import Image as Img
from dash import Output, Input, State, callback, callback_context, html, ALL, dcc, ctx
from dash.exceptions import PreventUpdate

from backend.stores import StoreImages
from backend.utils import Image

@callback(
    Output("div_images", "children", allow_duplicate=True),
    Output("view_edit", "data", allow_duplicate=True),

    Input("load_images", "n_clicks"),
    State("store_images", "data"),
    prevent_initial_call=True
)
def bearbeiten_bilder (n_clicks, data):
    if not n_clicks:
        raise PreventUpdate

    output_bilder = html.Div(children=["Es wurden keine Bilder gefunden."])
    os.makedirs("assets", exist_ok=True)
    if any(f.lower().endswith(".png") for f in os.listdir("assets")):
        output_bilder = html.Div(children=[
            html.Div([
            html.H3(f["id"], style={"marginTop": "0px"}),
            html.Div(   [
                html.H4(f["href"], style={"marginTop": "4px"}),
                html.Div(["Breite", dcc.Input(id={"type": "breite", "index": i}, type="text", value = f["width"], placeholder="Breite", style={"marginLeft":"20px", "width": "200px"})]),
                html.Div(["Höhe", dcc.Input(id={"type": "hoehe", "index": i}, type="text", value= f["height"], placeholder="Hoehe", style={"marginTop": "20px","marginLeft":"20px", "width": "200px"})])],
            style={"display": "flex", "flexDirection": "column", "minWidth": "300px", "marginLeft":"20px"}),
            html.Img(src=f"/assets/{f['href']}", style={"width": f["width"]+"px", "height":f["height"]+"px", "marginLeft": "20px"})], style={"display":"flex", "alignItems": "flex-start", "marginBottom": "20px"})
            for i, f in enumerate(data["images"])
            if f["href"].lower().endswith(".png")
        ], style={"marginLeft": "20px", "marginTop": "20px"})

    return html.Div([
        html.Div([
            html.H3("Pfad zu den Bildern", style={"marginRight": "10px", "minWidth": "180px"}),
            dcc.Input(id="path_images", type="text", value=data["path_images"],style={"width": "300px"}),
            html.Button("Bilder einladen", id="b_load_images", style={"width": "115px", "marginLeft":"20px"})
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "20px"}),
        output_bilder
    ], style={"marginLeft": "260px", "paddingLeft": "20px"}), "images"

@callback(
Output("images_is_saved", "data", allow_duplicate=True),
    Output("div_images", "children", allow_duplicate=True),

    Input("images_is_saved", "data"),
    State("store_images", "data"),
    prevent_initial_call=True)
def rerender_configuration(is_saved, store_images):
    if not ctx.triggered_id or not is_saved:
        raise PreventUpdate
    layout, *_ = bearbeiten_bilder(1, store_images)
    return False, layout

@callback(
    Output("store_images", "data"),
    Output("images_is_saved", "data"),

    Input({"type": "breite", "index": ALL}, "value"),
    Input({"type": "hoehe", "index": ALL}, "value"),
    Input("b_load_images", "n_clicks"),
    Input("store_images", "data"),
    State("path_images", "value"),
    prevent_initial_call=True
)
def speichere_bilder(breite, hoehe, n_clicks, data, bildpfad):
    ctx = callback_context
    if not data:
        raise PreventUpdate
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered_id
    store_images = StoreImages.from_dict(data or {})

    if triggered_id == "b_load_images" and n_clicks:
        store_images.load_images(bildpfad)

    elif triggered_id == "store_images":
        os.makedirs("assets", exist_ok=True)
        for f in os.listdir("assets"):
            pfad = os.path.join("assets", f)
            if os.path.isfile(pfad):
                os.remove(pfad)

        if os.path.isdir(store_images.path_images):
            for b in store_images.images:
                src = os.path.join(store_images.path_images, b.href)
                dst = os.path.join("assets", b.href)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)

    elif isinstance(triggered_id, dict):
        index = int(triggered_id.get("index"))
        typ = triggered_id.get("type")

        f = next((bild for bild in data["images"] if bild["id"] == "BILD_" + str(index + 1)), None)
        f = Image.from_dict(f)
        if typ == "breite":
            f.set_width(breite[index])
        else:
            f.set_height(hoehe[index])
        store_images.images[index] = f

    return store_images.to_dict(), True