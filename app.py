import os
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from plots import *
from loss import *

DATA_DIR = "../Data/FIRMS/"

FIIRMS_DF = pd.read_csv(DATA_DIR+"SUOMI_VIIRS_C2_USA_contiguous_and_Hawaii_7d.csv")
FIIRMS_DF['conf'] = FIIRMS_DF['confidence'].map({
    "low":0.2,
    "nominal":0.5,
    "high":0.9
})
data=FIIRMS_DF
frp = data['frp']
frp_scaled = np.log(data['frp'])
frp_scaled += -2*frp_scaled.min()
data['frp_scaled'] = frp_scaled
data['timestamp'] = pd.to_datetime(data['acq_date'].astype(str) + data['acq_time'].astype(str), format="%Y-%m-%d%H%M")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Graph("main_map", figure=firms_map(data))
            ], className="nine columns"),
        html.Div([
            html.H3("Economic effects"),
            html.Hr(),
            html.P("Select a marker to populate", id="eco_text", style={'whiteSpace': 'pre-wrap'}),
            html.Hr(),
            html.H4("Wildlife effects"),
            html.Hr(),
            html.P("Select a marker to populate", id="wildl_text", style={'whiteSpace': 'pre-wrap'}),
            html.Hr(),
            html.Hr(),
            daq.ToggleSwitch(
                id='map_toggle',
                value=False,
                color="red",
                label='Scattermap | Heatmap  ',
                labelPosition='bottom'
            )
        ], className="three columns")
    ], className="row")

])



def format_ec(ec_loss, wt_loss):
    return "<b>Total Economic assets:</b> %f"%ec_loss +"\n<b>Weighted Economic loss:</b> %f"%wt_loss

def format_wl(specs):
    if specs is not None:
        return "\n".join(specs.values)
    return "Data unavailable"

@app.callback(
    [Output('eco_text', "children"),
    Output('wildl_text', "children")],
    [Input("main_map", "selectedData")]
)
def marker_select(marker):
    if marker is None:
        return "Select a marker to populate", "Select a marker to populate"
    else:
        # print(marker)
        row = data.loc[marker['points'][0]['customdata']]
        loss = get_total_economic_loss(row['latitude'], row['longitude'], get_area_from_scan_track(row['scan'],row['track']))
        wt_loss = get_weighted_economic_loss(loss, row['conf'], 1)
        species = get_df_endangered_species(row['latitude'], row['longitude'])
        return format_ec(loss, wt_loss), format_wl(species)

@app.callback(
    Output("main_map", "figure"),
    [Input("map_toggle", "value")]
)
def change_map(heatmap):
    if heatmap:
        return firms_heatmap(data)
    else:
        return firms_map(data)
app.run_server(debug=True)