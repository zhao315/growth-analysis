#!/usr/bin/env python 
import os
import base64
import io 

import dash 
from dash import dcc, html, dash_table
from dash import Input, Output, State


from dash.exceptions import PreventUpdate

import dash_bootstrap_components as dbc

import pandas as pd

from utility_funcs import save_parameters_values, save_t_values, t_value_func, plot_func
from utility_funcs import generate_values, generate_values_1st, generate_values_2nd
from utility_funcs import save_infer_values, save_t_values, save_parameters_values
# initialize application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# create html session 
########################################################################################
## side bar content 
### title
sidebar_title = html.Div(
        children=[
            html.H4(children=["5 Parameters Logistic Function"])
            ],
        style={"textAlign": "center"}
        )

### upload file name 
upload_filname = html.Div(id="upload-filename")

### upload dataset
upload_dataset = html.Div(
        children=[ 
            html.P(children="Upload Dataset:", style={"textAlign": "center"}),
            dcc.Upload(
                children=[ 
                    html.Div(children=["Drag and Drop or ", html.A("Select Files")]),
                    ],
                style={
                    "width": "100%",
                    "height": "30px",
                    "borderStyle": "dashed",
                    "borderWidth": "1px",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    },
                multiple=False,
                id="upload-dataset",
                ),
            ],
        )

### threshold value 
threshold_value = html.Div(
        children=[ 
            html.P(children="Threshold Value: ", style={"textAlign": "center"}),
            dcc.Input(
                id="threshold-value",
                type="number",
                value=0.005,
                step=0.001,
                )
            ],
        style={
            "width": "100%",
            "display": "flex",
            "flex-direction": "column",
            "margin-top": "10px",
            }
        )

### plant sliderbar 
slidebar_plant_num = html.Div(
        children=[ 
            html.P(children="Plant Number: ", style={"textAlign": "center"}),
            dcc.Slider(
                id="slidebar-plant-num",
                min=0, value=0, step=1,
                marks=None,
                tooltip={"placement": "bottom", "always_visible": True},
                ),
            ],
        style={
            "color": "white",
            "margin-top": "100px",
            },
        )

### download options 
download_options = html.Div(
        children=[ 
            html.P(
                children="Download Options", 
                style={"textAlign": "center", "color": "white"}),
            dcc.Dropdown(
                options=["Inferred_Values", "T_Values", "Parameters_Values"],
                # value="T_Values",
                multi=False,
                searchable=False,
                id="download-options"
                ),
            ],
        style={
            "margin-top": "200px",
            "color": "black",
            }
        )


### download result 
download_result = html.Div(
        children=[ 
            html.Button(children=["Download CSV"], id="download-button"),
            dcc.Download(id="download-csv"),
            ],
        style={
            "margin-top": "50px",
            "margin-left": "20%",
            },
        )

### loading
loading_indicator = html.Div(
        children=[ 
            dcc.Loading(
                id="loading",
                type="circle",
                children=[html.Div([html.Div(id="loading-output", style={"display": "none"})])]
                ),
            ],
        style={
            "margin-top": "100px",
            }
        )

sidebar = html.Div(
        children=[
            sidebar_title,
            html.Hr(),
            upload_filname, 
            upload_dataset,
            html.Hr(),
            threshold_value,
            slidebar_plant_num,
            loading_indicator,
            download_options,
            download_result,
            ],
        style={
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "width": "16rem",
            "padding": "2rem 1rem",
            "background": "#500000",
            "color": "white",
            },
        )
########################################################################################
## main page cotent 
### plant number: 
plant_number = html.Div(
        children=[
            html.Div(children="Plant Number : "),
            html.Div(id="plant-number", style={"margin-left": "3%"}),
            ],
        style={
            "display": "flex",
            "fontSize": 20,
            "textAlign": "center",
            }
        )

### show result
result_table= html.Div(
        children=[
            dash_table.DataTable(
                id="t-table",
                ),
            ],
        )

### result graphs
result_graphs = html.Div(
        children=[ 
            dcc.Graph(
                id="result-graphs",
                style={
                    "width": "80vw",
                    "height": "80vh",
                    },
                ),
            ],
        )


main_page = html.Div(
        id="main-page",
        children=[
            plant_number,
            html.Hr(),
            result_table,
            html.Hr(),
            result_graphs,
            ],
        style={
            "margin-left": "18rem",
            "margin-right": "2rem",
            "padding": "2rem 1rem",
            },
        )


########################################################################################
# create layout 
app.layout = html.Div(
        children=[
            dcc.Store(id="memory-output"),
            sidebar, 
            main_page,
            ]
        )


# utilities function 
## upload function 
def parse_contents(contents, filename):
    content_type, content_string = contents.split(",")

    deconded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # assume that the user uploaded a csv file 
            df = pd.read_csv(io.StringIO(deconded.decode("utf-8")))
        elif "xls" in filename:
            # assume that the user uploaded an excel file 
            df = pd.read_excel(io.BytesIO(deconded))
    except Exception as e:
        print(e)
        return html.Div(children=["There was an error processing this file."])
    else:
        df = df.dropna()
        return df.to_dict("series")


# callback function 
## sidebar callback funtions  
### upload function
@app.callback(
        Output(component_id="memory-output", component_property="data"),
        [
            Input(component_id="upload-dataset", component_property="contents"),
            State(component_id="upload-dataset", component_property="filename"),
            ]
        )
def update_dataset(list_of_contents, list_of_names):
    if list_of_contents is not None:
        df = parse_contents(list_of_contents, list_of_names)
        return df


### slidarbar
@app.callback(
        Output(component_id="slidebar-plant-num", component_property="max"),
        [ 
            Input(component_id="memory-output",  component_property="data"),
            ]
        )
def update_slidebar(data):
    if data is None:
        raise PreventUpdate
    max_num = len(data) - 2
    return max_num


### show plant number 
@app.callback(
        Output(component_id="plant-number", component_property="children"),
        [ 
            Input(component_id="memory-output", component_property="data"), 
            Input(component_id="slidebar-plant-num", component_property="value"), 
            ]
        )
def update_plant_num(data, value):
    if data is None: 
        raise PreventUpdate
   
    keys = list(data.keys()).copy()
    keys.remove("x")

    plant_number = keys[value]
    return plant_number


### generate table and graph
@app.callback(
        Output(component_id="t-table", component_property="data"),
        Output(component_id="result-graphs", component_property="figure"),
        [ 
            Input(component_id="memory-output", component_property="data"), 
            Input(component_id="plant-number", component_property="children"), 
            Input(component_id="threshold-value", component_property="value"), 
            ]
        )
def update_graph(data, children, value):
    if data is None:
        raise PreventUpdate

    values = generate_values(data["x"], data[children])
    values_1 = generate_values_1st(data["x"], data[children])
    values_2 = generate_values_2nd(data["x"], data[children])
    # values, values_1, values_2 = infer_values(data["x"], data[children])
    
    t_values = t_value_func(values_1, values_2, value)
    t_values = pd.DataFrame(t_values)
    t_values.insert(0, "name", ["day", "growth rate"])
    t_table = t_values.to_dict("records")

    fig = plot_func(data["x"], data[children], values, values_1, values_2, value)

    return t_table, fig

@app.callback(
        Output(component_id="loading-output", component_property="children"),
        [ 
            Input(component_id="memory-output", component_property="data"),
            Input(component_id="download-options", component_property="value"),
            Input(component_id="threshold-value", component_property="value"),
            ]
        )
def update_download_options(data, value, threshold):
    if data is None: 
        raise PreventUpdate

    if os.path.exists("my_file.pkl"):
        os.remove("my_file.pkl")

    if value == "T_Values":
        df = save_t_values(data, threshold)
        df.to_pickle("my_file.pkl")
    elif value == "Parameters_Values":
        df = save_parameters_values(data)
        df.to_pickle("my_file.pkl")
    elif value == "Inferred_Values":
        df = save_infer_values(data)
        df.to_pickle("my_file.pkl")
    else:
        pass
    return value

### download data 
@app.callback(
        Output(component_id="download-csv", component_property="data"),
        [ Input(component_id="download-button", component_property="n_clicks") ],
        prevent_initial_call=True,
        )
def download_data(n_clicks):
    try:
        df = pd.read_pickle("my_file.pkl")
    except Exception as e:
        raise PreventUpdate
    else: 
        os.remove("my_file.pkl")
        return dcc.send_data_frame(df.to_csv, "my_file.csv")


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
