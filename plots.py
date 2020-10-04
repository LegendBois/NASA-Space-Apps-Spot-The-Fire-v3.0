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

confidence_map = {
    "low":0.2,
    "nominal":0.4,
    "high":0.99
}

def get_text(data):
    text =  data['timestamp'].astype(str) 
    text += "<br>Confidence: " + data['confidence'].astype(str) 
    text += "<br>Brightness I-4: "+ data['bright_ti4'].astype(str) 
    text += "<br>Brightness I-5: "+ data['bright_ti5'].astype(str) 
    text += "<br>FRP: "+ data['frp'].astype(str)
    
    return text

def firms_map(data):

    frp = data['frp']
    frp_scaled = np.log(data['frp'])
    frp_scaled += -2*frp_scaled.min()
    data['timestamp'] = pd.to_datetime(data['acq_date'].astype(str) + data['acq_time'].astype(str), format="%Y-%m-%d%H%M")
    fig = go.Figure(go.Scattermapbox(
    lat=data["latitude"], 
    lon=data["longitude"], 
    hoverinfo="text",
    hovertext=get_text(data),
    mode="markers",
    marker=go.scattermapbox.Marker(
            size=data['frp'],
            sizemode="area",
            color=frp_scaled,
            colorscale="inferno",
            opacity=data['confidence'].map(confidence_map),

    )))

    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": "United States Geological Survey",
                "source": [
                    "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                ]
            }
        ])
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()