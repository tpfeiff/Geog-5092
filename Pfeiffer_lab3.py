import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, Polygon
import random

#The function takes two pandas data frames with two columns (id and mean) and prints out the results in a readable statement
def final_results( mean1, mean2):
    for idx, mean in mean1.iterrows():
        print( f'In the huc 8 sample, The mean for the {idx} is {mean}')
        
    for idx, mean in mean2.iterrows():
        print( f'In the huc 12 sample, The mean for the {idx} is {mean}')
        
    return

# initiating variables containg layer data and creating empty dictionaries for encoding random samples
huc8 = gpd.read_file(r'C:\GEOG\Lab3\lab3.gpkg', layer = 'wdbhuc8')
huc12 = gpd.read_file(r'C:\GEOG\Lab3\lab3.gpkg', layer = 'wdbhuc12')
soils = gpd.read_file(r'C:\GEOG\Lab3\lab3.gpkg', layer = 'ssurgo_mapunits_lab3')
huc8sample = { "huc8id": [], "geometry": []}
huc12sample = { "huc8id": [], "geometry": []}

#Part 1 for huc8 sample

random.seed(0)
for idx, feature in huc8.iterrows():
    area = feature.geometry.area/1000000
    extent = feature.geometry.bounds
    numpoints = round(0.05*area)
    z=0
    
    while z < numpoints:
        x = random.uniform(extent[0], extent[2])
        y = random.uniform(extent[1], extent[3])
        point = Point(x, y)
        
        if feature.geometry.contains(point):
            id = feature ["HUC8"]
            huc8sample["huc8id"].append(id)
            huc8sample["geometry"].append(point)
            z += 1
            
#part 1 for huc 12 sample

random.seed(0)
for idx, feature in huc12.iterrows():
    area = feature.geometry.area/1000000
    extent = feature.geometry.bounds
    numpoints = round(0.05*area)
    
    z=0    
    while z < numpoints:
        x = random.uniform(extent[0], extent[2])
        y = random.uniform(extent[1], extent[3])
        point = Point(x, y)
               
        if feature.geometry.contains(point):
            id = feature ["HUC12"][0:8]
            huc12sample["huc8id"].append(id)
            huc12sample["geometry"].append(point)
            z += 1
            
#Part 2 for both 

#huc 8 
huc8_sampdf = pd.DataFrame(huc8sample)
huc8gdf = gpd.GeoDataFrame(huc8_sampdf, crs = huc8.crs)
huc_points = gpd.overlay(huc8gdf, soils, how = 'intersection')
aws_means = huc_points.groupby(by = ["huc8id"])["aws0150"].agg(['mean'])
print(aws_means)

#huc12
huc12_sampdf = pd.DataFrame(huc12sample)
huc12gdf = gpd.GeoDataFrame(huc12_sampdf, crs = huc8.crs)
huc_points12 = gpd.overlay(huc12gdf, soils, how = 'intersection')
aws_means12 = huc_points12.groupby(by = ["huc8id"])["aws0150"].agg(['mean'])
print(aws_means12)

#using the final_results function to print findings
final_results(aws_means, aws_means12)