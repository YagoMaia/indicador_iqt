import os
import fiona
import geopandas as gpd
import pandas as pd
import folium
from .data_loader_layers import load_routes, load_neighborhoods
from .layers import add_map_layers, add_line_to_map, add_line_to_map_sem_grupo
from .styles import get_legend_html

def create_map():
    
    pass

def initialize_map(path_city, path_routes) -> folium.Map:
    # gdf_routes = load_routes(path_routes)
    gdf_city = load_neighborhoods(path_city)
    
    # Define centro do mapa
    map_center = [gdf_city.geometry.centroid.y.mean(), gdf_city.geometry.centroid.x.mean()]
    map_routes = folium.Map(location=map_center, zoom_start=12, tiles='CartoDB Voyager')
    
    folium.GeoJson(
        gdf_city,
        style_function=lambda feature: {
            'fillColor': 'white',
            'color': 'black',    
            'weight': 0.7,
            'fillOpacity': 0.5,
        },
        name = 'Bairros'
    ).add_to(map_routes)
    
    return map_routes

def classification_routes(map_routes, gdf_routes : gpd.GeoDataFrame):
    for line in gdf_routes.iter_rows():
        add_line_to_map_sem_grupo(line, map_routes)
    return map_routes