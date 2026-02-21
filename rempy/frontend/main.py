# Run this app with `python app.py` and
# visit http://backend:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
from io import BytesIO
import base64
import requests
import plotly.graph_objects as go
import datetime
import json

app = Dash()


app.layout = html.Div(
    html.Div(
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
    html.H4('Attention: if there is, at the same time, an image + mask selected AND a benchmark from the database, the image and mask will be at the end of the page.',             
            style={"marginTop":"6%"}, ),
    html.Div([
        html.Div(
            style={"display": "none", "display": "block"}, 
            children=[
                html.Div([
                    dcc.Store(id="benchmarks-store"),
                    dcc.Dropdown(id="benchmarks-dropdown", placeholder="Select a benchmark from the database",),
                    html.Div(id="benchmark-details")
                ]),
            ])
    ]),
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
        html.Div(
            id="graph-container",
            style={"display": "none"}, 
            children=[
                dcc.Graph(id="benchmark-graph")
            ]
            ),
        ]),
    html.Div([
        html.Div(
            id="graph-all-value-container",
            style={"display": "none"}, 
            children=[
                dcc.Graph(id="all-normal-value-graph"),
                dcc.Graph(id="all-optimized-value-graph"),
            ]
            ),
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


    #change backend:8000 to path in docker = backend
    response = requests.post(
        "http://backend:8000/create_benchmark/",
        files=files,
        params={"nb_run": nb_run}, 
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
    image_url = f"http://backend:8000/benchmarks/{id}/result-normal"

    response = requests.get(image_url)
    if response.status_code != 200:
        return html.P(f"Erreur: {response.text}")

    encoded = base64.b64encode(response.content).decode("utf-8")
    mime = response.headers.get("Content-Type", "image/png")
    src = f"data:{mime};base64,{encoded}"

    return html.Div([
        html.H4("Résultat Normal", style={"textAlign": "center"}),
        html.Img(src=src, style={"width": "100%"})
    ])

@app.callback(
    Output("opti-result", "children"),
    Input("benchmark-id", "data"),
)
def load_opti_result(benchmark_id):
    if benchmark_id is None or benchmark_id == "":
        return None

    id = benchmark_id["id"]

    image_url = f"http://backend:8000/benchmarks/{id}/result-opti"

    response = requests.get(image_url)
    if response.status_code != 200:
        return html.P(f"Erreur: {response.text}")

    encoded = base64.b64encode(response.content).decode("utf-8")
    mime = response.headers.get("Content-Type", "image/png")
    src = f"data:{mime};base64,{encoded}"

    return html.Div([
        html.H4("Résultat Optimisé (Numba)", style={"textAlign": "center"}),
        html.Img(src=src, style={"width": "100%"})
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
    Output("benchmark-graph", "figure"),
    Input("benchmark-id", "data"),
)
def update_graph(benchmark_data):
    if benchmark_data is None:
        raise PreventUpdate
        
    benchmark_id = benchmark_data["id"]

    response = requests.get(
        f"http://backend:8000/benchmarks/{benchmark_id}/data"
    )
    if response.status_code != 200:
        raise PreventUpdate

    data = response.json()

    normal_time = data["mean_time_normal"]
    opti_time = data["mean_time_opti"]

    fig = go.Figure()
    fig.add_trace(
            go.Bar(name="Normal", x=["Execution Time"], y=[normal_time]),
    )

    fig.add_trace(
            go.Bar(name="Numba", x=["Execution Time"], y=[opti_time]),
    )

    fig.update_layout(
        title="Benchmark Comparison",
        barmode="group",
        yaxis_title="Time (seconds)",
    )
    return fig

@app.callback(
    Output("graph-container", "style"),
    Input("benchmark-id", "data"),
)
def toggle_graph(benchmark_data):
    if benchmark_data is None:
        return {"display": "none"}
    
    return {"display": "block"}

@app.callback(
    Output("all-normal-value-graph", "figure"),
    Input("benchmark-id", "data"),
)
def update_graph_all_value(benchmark_data):
    if benchmark_data is None:
        raise PreventUpdate
        
    benchmark_id = benchmark_data["id"]

    response = requests.get(
        f"http://backend:8000/benchmarks/{benchmark_id}/data"
    )
    if response.status_code != 200:
        raise PreventUpdate

    data = response.json()

    individual_times_normal = data["individual_times_normal"]

    fig = go.Figure()

    i=0
    for elt in json.loads(individual_times_normal):
        i+=1
        fig.add_trace(
            go.Bar(name=f"Normal result value {i}", x=["Execution Time"], y=[elt]),
        )


    fig.update_layout(
        title="Values of Normal Propagation (depending of the number of run)",
        barmode="group",
        yaxis_title="Time (seconds)",
    )
    return fig

@app.callback(
    Output("all-optimized-value-graph", "figure"),
    Input("benchmark-id", "data"),
)
def update_graph_all_optimize_value(benchmark_data):
    if benchmark_data is None:
        raise PreventUpdate
        
    benchmark_id = benchmark_data["id"]

    response = requests.get(
        f"http://backend:8000/benchmarks/{benchmark_id}/data"
    )
    if response.status_code != 200:
        raise PreventUpdate

    data = response.json()

    individual_times_opti = data["individual_times_opti"]

    fig = go.Figure()

    i=0
    for elt in json.loads(individual_times_opti):
        i+=1
        fig.add_trace(
            go.Bar(name=f"Optimized result value {i}", x=["Execution Time"], y=[elt]),
        )


    fig.update_layout(
        title="Values of Numba Propagation (depending of the number of run)",
        barmode="group",
        yaxis_title="Time (seconds)",
    )
    return fig

@app.callback(
    Output("graph-all-value-container", "style"),
    Input("benchmark-id", "data"),
)
def toggle_graph_all_value(benchmark_data):
    if benchmark_data is None:
        return {"display": "none"}

    return {"display": "block"}

@app.callback(
    Output("benchmarks-dropdown", "options"),
    Output("benchmarks-store", "data"),
    Input("benchmark-id", "data"), 
)
def load_benchmarks(benchmark_data):

    response = requests.get(
        "http://backend:8000/benchmarks/"
    )

    if response.status_code != 200:
        return [], []

    benchmarks = response.json() 

    options = [
        {
            "label": f"Benchmark {b['id']}",
            "value": b["id"],  
        }
        for b in benchmarks
    ]
    return options, benchmarks

@app.callback(
    Output("benchmark-details", "children"),
    Input("benchmarks-dropdown", "value"),
    Input("benchmarks-store", "data"),
)
def display_benchmark_details(benchmark_id, benchmarks):

    if benchmark_id is None or not benchmarks:
        return ""

    selected = next(
        (b for b in benchmarks if b["id"] == benchmark_id),
        None
    )

    if not selected:
        return "Benchmark not found"

    image_url = f"http://backend:8000{selected['image_url']}"
    response = requests.get(image_url)
    if response.status_code != 200:
        return html.P(f"Erreur: {response.text}")
    mask_url = f"http://backend:8000{selected['mask_url']}"
    response_mask = requests.get(mask_url)
    if response_mask.status_code != 200:
        return html.P(f"Erreur: {response_mask.text}")
    normal_url = f"http://backend:8000{selected['result_normal_url']}"
    response_normal = requests.get(normal_url)
    if response_normal.status_code != 200:
        return html.P(f"Erreur: {response_normal.text}")
    numba_url = f"http://backend:8000{selected['result_opti_url']}"
    response_numba = requests.get(numba_url)
    if response_numba.status_code != 200:
        return html.P(f"Erreur: {response_numba.text}")
    
    response_data = requests.get(
        f"http://backend:8000{selected['data_url']}"
    )
    if response_data.status_code != 200:
        raise PreventUpdate

    data = response_data.json()

    normal_time = data["mean_time_normal"]
    opti_time = data["mean_time_opti"]

    fig = go.Figure()
    fig.add_trace(
            go.Bar(name="Normal", x=["Execution Time"], y=[normal_time]),
    )

    fig.add_trace(
            go.Bar(name="Numba", x=["Execution Time"], y=[opti_time]),
    )

    fig.update_layout(
        title="Benchmark Comparison",
        barmode="group",
        yaxis_title="Time (seconds)",
    )
    
    return html.Div([
        html.H4(f"Benchmark {selected['id']}"),
        
        html.P(f"Input Image :"),
        html.Img(src=encode_image(response), style={"width": "30%"}),
        html.P(f"Input Mask :"),
        html.Img(src=encode_image(response_mask), style={"width": "30%"}),
        html.P(f"Normal propagation :"),
        html.Img(src=encode_image(response_normal), style={"width": "30%"}),
        html.P(f"Numba propagation :"),
        html.Img(src=encode_image(response_numba), style={"width": "30%"}),
        dcc.Graph(figure=fig),
    ])

def encode_image(response):
    encoded = base64.b64encode(response.content).decode("utf-8")
    mime = response.headers.get("Content-Type", "image/png")
    src = f"data:{mime};base64,{encoded}"
    return src

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8050, debug=True)