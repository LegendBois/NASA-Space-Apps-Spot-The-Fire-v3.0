import os
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from plots import *

DATA_DIR = "Data/FIRMS/"

FIIRMS_DF = pd.read_csv(DATA_DIR+"SUOMI_VIIRS_C2_USA_contiguous_and_Hawaii_7d.csv")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



app.layout = html.Div([
    dcc.Graph("main-map", figure=firms_map(FIIRMS_DF))
])

app.run_server(debug=True)