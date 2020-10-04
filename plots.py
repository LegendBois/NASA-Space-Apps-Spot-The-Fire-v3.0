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

def get_text(data):
    text =  data['timestamp'].astype(str) 
    text += "<br>Confidence: " + data['confidence'].astype(str) 
    text += "<br>Brightness I-4: "+ data['bright_ti4'].astype(str) 
    text += "<br>Brightness I-5: "+ data['bright_ti5'].astype(str) 
    text += "<br>FRP: "+ data['frp'].astype(str)

    return text

def firms_map(data):

    fig = go.Figure(go.Scattermapbox(
    lat=data["latitude"], 
    lon=data["longitude"], 
    hoverinfo="text",
    customdata=data.index,
    hovertext=get_text(data),
    mode="markers",
    marker=go.scattermapbox.Marker(
            size=data['frp'],
            sizemode="area",
            color=data['frp_scaled'],
            colorscale="inferno",
            opacity=data['conf'],

    )))

    fig.update_layout(
        mapbox=dict(
            center=go.layout.mapbox.Center(
                lat=38,
                lon=-90
            ),
            zoom=3
        ),
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
    fig.update_layout(clickmode='event+select', height=800)
    return fig

def firms_heatmap(data):
    trace = data
    heat_fig = px.density_mapbox(trace,
                                 lat="latitude",
                                 lon="longitude",
                                 radius=data["frp_scaled"],
                                 zoom=3,
                                 mapbox_style="open-street-map",
                                )
    return(heat_fig)