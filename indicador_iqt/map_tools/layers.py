import folium
import fiona
import geopandas as gpd
import pandas as pd
from ..utils.colors import color_iqt

def load_layers_lines(path_lines: str) -> gpd.GeoDataFrame:
    """
    Carrega camadas de linhas de um arquivo KML, excluindo a camada 'Linhas prontas'.
    
    Parameters
    ----------
    path_lines : str
        Caminho para o arquivo KML contendo as camadas de linhas.
        
    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame contendo todas as camadas de linhas concatenadas,
        exceto a camada 'Linhas prontas'.
        
    Notes
    -----
    Utiliza o driver LIBKML para leitura do arquivo e concatena todas as
    camadas válidas em um único GeoDataFrame.
    """
    gdf_list = []
    for layer in fiona.listlayers(path_lines):
        if layer == 'Linhas prontas':
            continue
        gdf = gpd.read_file(path_lines, driver='LIBKML', layer=layer)
        gdf_list.append(gdf)
    gdf_lines = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))
    return gdf_lines

def filter_lines(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Filtra o GeoDataFrame para manter apenas geometrias do tipo LineString.
    
    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame contendo diferentes tipos de geometrias.
        
    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame filtrado contendo apenas geometrias do tipo LineString.
    """
    return gdf[gdf.geometry.type == "LineString"]

def calculate_distances(gdf_lines: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calcula o comprimento de cada LineString no GeoDataFrame.
    
    Parameters
    ----------
    gdf_lines : gpd.GeoDataFrame
        GeoDataFrame contendo geometrias do tipo LineString.
        
    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame original com uma nova coluna 'distances' contendo
        o comprimento de cada linha.
        
    Notes
    -----
    O cálculo é feito utilizando o sistema de coordenadas atual do GeoDataFrame.
    Para resultados em metros, certifique-se que o CRS está em uma projeção adequada.
    """
    gdf_lines['distances'] = gdf_lines.apply(lambda row: row.geometry.length, axis=1)
    return gdf_lines

def calculate_distances_2(gdf_lines: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calcula distâncias em metros e quilômetros usando projeção Web Mercator (EPSG:3857).
    
    Parameters
    ----------
    gdf_lines : gpd.GeoDataFrame
        GeoDataFrame contendo geometrias do tipo LineString.
        
    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame com novas colunas:
        - 'distancia_metros': comprimento da linha em metros
        - 'distancia_km': comprimento da linha em quilômetros
        O GeoDataFrame é retornado na projeção WGS84 (EPSG:4326).
        
    Notes
    -----
    A função realiza os seguintes passos:
    1. Reprojecta para Web Mercator (EPSG:3857)
    2. Calcula as distâncias
    3. Retorna o GeoDataFrame na projeção WGS84
    """
    gdf_lines = gdf_lines.to_crs(epsg=3857)
    gdf_lines['distancia_metros'] = gdf_lines.length
    gdf_lines['distancia_km'] = gdf_lines['distancia_metros'] / 1000
    return gdf_lines.to_crs(4326)

def add_line_to_map(line: gpd.GeoSeries, map_routes: folium.Map, group: folium.FeatureGroup) -> None:
    """
    Adiciona uma linha ao mapa Folium com grupo específico.
    
    Parameters
    ----------
    line : gpd.GeoSeries
        Série do GeoPandas contendo a geometria da linha e seus atributos.
        Deve conter as seguintes colunas:
        - 'geometry': geometria do tipo LineString
        - 'Name': nome da linha para o tooltip
        - 'iqt': índice de qualidade para determinar a cor
        
    map_routes : folium.Map
        Objeto do mapa Folium onde a linha será adicionada.
        
    group : folium.FeatureGroup
        Grupo de features do Folium onde a linha será agrupada.
        
    Notes
    -----
    A cor da linha é determinada pela função color_iqt com base no valor do IQT.
    """
    geometry = line['geometry']
    tooltip_line = line['Name']
    color = color_iqt(line['iqt'])
    folium.PolyLine(
        locations=[(lat, lon) for lon, lat in zip(geometry.xy[0], geometry.xy[1])],
        color=color,
        weight=2.5,
        opacity=1,
        tooltip=tooltip_line
    ).add_to(group).add_to(map_routes)

def add_line_to_map_no_group(line: gpd.GeoSeries, map_routes: folium.Map) -> None:
    """
    Adiciona uma linha diretamente ao mapa Folium sem agrupamento.
    
    Parameters
    ----------
    line : gpd.GeoSeries
        Série do GeoPandas contendo a geometria da linha e seus atributos.
        Deve conter as seguintes colunas:
        - 'geometry': geometria do tipo LineString
        - 'Name': nome da linha para o tooltip
        - 'iqt': índice de qualidade para determinar a cor
        
    map_routes : folium.Map
        Objeto do mapa Folium onde a linha será adicionada.
        
    Notes
    -----
    Similar a add_line_to_map, mas adiciona a linha diretamente ao mapa
    sem usar grupos. A linha terá uma espessura maior (weight=3).
    """
    geometry = line['geometry']
    tooltip_line = line['Name']
    color = color_iqt(line['iqt'])
    folium.PolyLine(
        locations=[(lat, lon) for lon, lat in zip(geometry.xy[0], geometry.xy[1])],
        color=color,
        weight=3,
        opacity=1,
        tooltip=tooltip_line
    ).add_to(map_routes)