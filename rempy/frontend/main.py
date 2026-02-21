# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
from io import BytesIO
import base64
import requests
import pandas as pd
import plotly.graph_objects as go
import datetime

app = Dash()


app.layout = html.Div(
    html.Div(
        #style={'backgroundColor':'grey'},
             children=[
                 html.H1('Propagation normal VS numba', 
            style={'textAlign': 'center'}),

    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select an Image')
        ]),
        style={
            'float':'left',
            'width': '49%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': 'auto',
            'backgroundColor':'grey',
            'border-color': 'black'
        },
        multiple=True
    ),
    dcc.Upload(
        id='upload-mask',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select an Mask')
        ]),
        style={
            'float':'right',
            'width': '49%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': 'auto',
            'backgroundColor':'grey',
            'border-color': 'black'
        },
        multiple=True
    ),

    html.Div(id='output-image-upload', style={
            'float':'left',
            'width': '49%',
            'margin': 'auto',},),
    html.Div(id='output-mask-upload', style={
            'float':'right',
            'width': '49%',
            'margin': 'auto',},),
    dcc.Store(id="benchmark-id"),
    html.Div(
        id="controls-container",  
        children=[
        dcc.Button('Lancer les calculs', id='run-benchmark',
                    n_clicks=0, 
                    style={
                "cursor": "pointer",
            },
                          ),
         html.H4("Nombre de run",
                 style={
                "margin": "10px 15px",
            },),
        dcc.Input(
            id="nb-run",
            type="number",
            min=1,
            step=1,
            value=1,
            placeholder="Nombre de runs",
            style={
                "width": "100px",
                "textAlign": "center",
                "marginBottom":'20px'
            },
        ),
    ],
    style={
        "display": "none",
    },
    ),
    html.Div(id='benchmark-result', style={'textAlign':'center'}),
    html.Div(
        [
            html.Div(id="normal-result"),
            html.Div(id="opti-result"),
        ],
        style={
            "display": "flex",
            "justifyContent": "space-evenly",
            "alignItems": "flex-start",
        },
    ),
    html.Div([
        html.Div(id="benchmark-graph"),
        #html.Div(
         #   dcc.Graph(id="benchmark-graph"), style={"marginTop": "40px",}),
        html.Div(
            dcc.Graph(id='empty', figure={'data': []}), style={'display': 'none'})
        ]),
    ])
),
    

def parse_contents(contents, filename, date):
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        html.Img(src=contents),
    ])    

@app.callback(Output('output-image-upload', 'children'),
              Input('upload-image', 'contents'),
              State('upload-image', 'filename'),
              State('upload-image', 'last_modified'))
def update_output_image(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
    
@app.callback(Output('output-mask-upload', 'children'),
              Input('upload-mask', 'contents'),
              State('upload-mask', 'filename'),
              State('upload-mask', 'last_modified'))
def update_output_mask(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(
    Output("benchmark-id", "data"),
    Input("run-benchmark", "n_clicks"),
    State("upload-image", "contents"),
    State("upload-mask", "contents"),
    State("nb-run", "value")
)
def run_benchmark(n_clicks, image_contents, mask_contents, nb_run):

    if n_clicks is None:
        return None

    if image_contents is None or mask_contents is None:
        return None

    image_data = base64.b64decode(image_contents[0].split(",")[1])
    mask_data = base64.b64decode(mask_contents[0].split(",")[1])

    files = {
        "image": ("image.png", BytesIO(image_data), "image/png"),
        "mask": ("mask.png", BytesIO(mask_data), "image/png"),
    }

    #change 127.0.0.1:8000 to path in docker
    response = requests.post(
        "http://127.0.0.1:8000/create_benchmark/",
        files=files,
        data={"nb_run": nb_run},
    )

    if response.status_code != 200:
        return f"Error: {response.text}"

    return response.json()

@app.callback(
    Output("normal-result", "children"),
    Input("benchmark-id", "data"),
)
def load_normal_result(benchmark_id):
    if benchmark_id is None or benchmark_id == "":
        return None
    
    id = benchmark_id["id"]
    image_url = f"http://127.0.0.1:8000/benchmarks/{id}/result-normal"

    return html.Div([
        html.H4("Résultat Normal", style={"textAlign": "center"}),
        html.Img(src=image_url, style={"width": "100%"})
    ])

@app.callback(
    Output("opti-result", "children"),
    Input("benchmark-id", "data"),
)
def load_opti_result(benchmark_id):
    if benchmark_id is None or benchmark_id == "":
        return None

    id = benchmark_id["id"]

    image_url = f"http://127.0.0.1:8000/benchmarks/{id}/result-opti"

    return html.Div([
        html.H4("Résultat Optimisé (Numba)", style={"textAlign": "center"}),
        html.Img(src=image_url, style={"width": "100%"})
    ])

@app.callback(
    Output("controls-container", "style"),
    Input("upload-image", "contents"),
    Input("upload-mask", "contents"),
)
def toggle_controls(image_contents, mask_contents):

    if image_contents is not None and mask_contents is not None:
         return {
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "gap": "10px",
            "marginTop": "3%",
            "clear": "both", 
        }


    return {
        "display": "none"
    }


@app.callback(
    Output("benchmark-graph", "children"),
    Input("benchmark-id", "data"),
    Input("upload-image", "contents"),
    Input("upload-mask", "contents"),
)
def update_graph(benchmark_data, image_contents, mask_contents):
    #if image_contents is None and mask_contents is None:
      #  return {
     #   "display": "none"
    #}
    #if benchmark_data is None:
     #   print("No benchmark")
      #  return None

    #benchmark_id = benchmark_data["id"]

    response = requests.get(
        f"http://127.0.0.1:8000/benchmarks/1/data"
    )
    print("Benchmark")
    if response.status_code != 200:
        return {}

    data = response.json()

    normal_time = data["mean_time_normal"]
    opti_time = data["mean_time_opti"]
    print(normal_time)
    print(opti_time)

    fig = go.Figure(
        data=[
            px.bar(name="Normal", x=["Execution Time"], y=[normal_time]),
            px.bar(name="Optimized", x=["Execution Time"], y=[opti_time]),
        ]
    )

    fig.update_layout(
        title="Benchmark Comparison",
        barmode="group",
        yaxis_title="Time (seconds)",
    )
    return [fig]

"""
@app.callback(
    Output("all_benchmarks", "contents")
)
def get_all_benchmarks():
    response = requests.post(
        "http://127.0.0.1:8000/benchmarks/"
    )

    if response.status_code != 200:
        return f"Error: {response.text}"

    benchmark = response.json()
    for elt in benchmark:
        return f"Benchmark created with ID: {elt.id}"
"""

if __name__ == '__main__':
    app.run(debug=True)