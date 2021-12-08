import rasterio
import pandas as pd
import geopandas as gpd
import numpy as np
import os 
import matplotlib.pyplot as plt
import glob
from rasterio.plot import show, show_hist
from scipy.spatial import cKDTree



files = glob.glob(r"C:\geog5092\lab4\data\*.tif")

#Clean out unnecessary files and check files list (print stament)
rfiles = sorted(files)
rfiles.pop(1)
rfiles.pop(2)
print(rfiles)


#Empty list for new rasters (temp_array)
factors = []

def mean_window(rasterfiles):
    """"
    The function takes in a list of rasters,
    Creaates an empty numpy array with same shape,
    Runs a focal analysis using a window that 
    calculates the mean of the pixels within the window,
    and inserts mean value into empty numpy array
    """
    for raster in rasterfiles: 
        with rasterio.open(raster) as array:
            data = array.read(1)
            temp_array = np.zeros_like(data)
            for row in range(0, data.shape[0]):
                for col in range(0, data.shape[1]):
                    win = data[row: row + 11, col: col + 9] 
                    temp_array[row, col]= win.sum()/99
            factors.append(temp_array)


            
#Utilize function 
mean_window(rfiles)


#Criteria for each raster
area = np.where(factors[0] < 0.05,1,0)
slope = np.where(factors[1] < 15,1,0)
urban = np.where(factors[2] == 0,1,0)
water = np.where(factors[3] < 0.02,1,0)
wind = np.where(factors[4] > 8.5,1,0)


#Sum 5 rasters into one array, and reclassify
sum_group = (area+slope+urban+water+wind)
final_array = np.where(sum_group == 5,1,0)

#Number of suitable sites
final_array.sum()


#Geotif creation
with rasterio.open(r"C:\geog5092\lab4\data\protected_areas.tif") as dataset:
    with rasterio.open (f'suit_areas.tif','w',
                driver = 'GTiff',
                height = final_array.shape[0],
                width = final_array.shape[1],
                count = 1,
                dtype = 'int8',
                crs = dataset.crs,
                transform = dataset.transform,
                nodata = 0) as out_raster:
        fivearray = final_array.astype('int8')
        out_raster.write(final_array, indexes = 1)


#Get bounds of tif and append centroids to a suit_coords
with rasterio.open('suit_areas.tif') as blob:
    cell_size = blob.transform[0]
    bounds = blob.bounds
    x_coords = np.arange(bounds[0] + cell_size/2, bounds[2], cell_size)
    y_coords = np.arange(bounds[1] + cell_size/2, bounds[3], cell_size)
    x, y = np.meshgrid(x_coords, y_coords)
    x.flatten().shape, y.flatten().shape
    suit_coords = np.c_[x.flatten(),y.flatten()]
    
# Use Ravel to compare falttened array of 0 and 1s with the xy coords of suit_coords  
    Rave = x.ravel()
    Bool = fivearray.reshape(Rave.shape)

# Multiply boolean by cells and append any cells with a value of 1 to Bool_coords    
    Bool_coords =[]
    for i, e in zip(suit_coords, Bool):
        x = np.multiply(i[0],e)
        y = np.multiply(i[1],e)
        if x != 0 and y != 0: 
            Bool_coords.append([x,y])

#Create coord from stations.txt
trans_stats = pd.read_csv(r"C:\geog5092\lab4\data\transmission_stations.txt")
x_coord = trans_stats['X']
y_coord = trans_stats['Y']
stations = np.column_stack([x_coord, y_coord])

#Creat numpy arrays from stations and bool)coords
Bool_array = np.array(Bool_coords)
Stat_array = np.array(stations)

dist,indexes = cKDTree(Stat_array).query(Bool_array)

Stat_array.shape

#Max and Min distances
print('Max:', dist.max()/1000,'Min:', dist.min()/1000)
