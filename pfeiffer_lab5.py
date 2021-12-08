import rasterio
import pandas as pd
import geopandas as gpd
import numpy as np
import scipy
import os 
import glob
from rasterio.plot import show
from sklearn.utils.extmath import density 


from lab5functions import reclassAspect, reclassByHisto, slopeAspect



dem = r'bigElk_dem.tif'


#Part 1.1
with rasterio.open(dem) as raster:
    data = raster.read(1)
    slope, aspect = slopeAspect(data, 30)

reAsp = reclassAspect(aspect)
reSlope = reclassByHisto(slope, 10)

#Part 1.2,1.3,1.4,1.5

#establish aoi healthy and burned forest
with rasterio.open('fire_perimeter.tif') as aoi:
    forest = aoi.read(1)
    healthy = np.where(forest == 2, 1, np.nan)
    burn = np.where(forest == 1, 1, np.nan)
   
#calcualte ndvi and rr
rrlist = []
b3 = sorted(glob.glob('L5_big_elk/*B3.tif'))
b4 = sorted(glob.glob('L5_big_elk/*B4.tif'))
ndvi_values = []
for ras4, ras3 in zip(b4,b3):
    with rasterio.open(ras4) as v4:
        b4_value = v4.read(1)
    with rasterio.open(ras3) as v3:
        b3_value = v3.read(1)
    numerator = b4_value - b3_value
    denom = b4_value + b3_value
    ndvi = numerator/denom 
    # print(ndvi) 
    health_ndvi = healthy * ndvi
    # print (health_ndvi)
    mean_year_health = np.nanmean(health_ndvi)
    # print(mean_year_health)
    burn_ndvi = burn * ndvi
    #print (burn_ndvi)
    recovery = burn_ndvi/mean_year_health
    rrlist.append(recovery)

#reformat rrlist and yearlist to correct format for polyfit
stack_rr = np.vstack(rrlist)    
final_rr = stack_rr.flatten() 
final_rr[np.isnan(final_rr)] = 0


year_list = []
for year in range (2002, 2012):
        empty_array = np.zeros_like(rrlist[0])
        year_array = np.where (empty_array == 0, year, year)
        year_list.append(year_array)
master_year = np.vstack(year_list)

for recovery in rrlist:
    recovery[np.isnan(recovery)]=0

master_year = master_year.flatten()

slope = np.polyfit(master_year, final_rr, 1)

#Final print statements for Part 1
print(f'The mean coefficient of recovery across all years for the burned area is ', round(slope[0],3))

yr=2002   
for recovery in rrlist:
    print(f'Recovery Ratio for the year {yr}:', round(recovery.mean(),3))
    yr += 1
                 
         
            
       
# Part 2.1 z stats
def zstat_table (value_array, zone, csv_name):
    uniqzone = np.unique(zone)
    dict = {'zones':[], 'mean':[], 'max':[], 'min':[], 'sd':[], 'count':[]}
    x = 1
    for zone in list(uniqzone):
        dict['zones'].append(x)
        boras = np.where(zone == x,1,np.nan)
        dict['mean'].append(np.nanmean(boras * value_array))
        dict['max'].append(np.nanmax(boras * value_array))
        dict['min'].append(np.nanmin(boras * value_array))
        dict['sd'].append(np.nanstd(boras * value_array))
        dict['count'].append(np.nansum(boras))
        x += 1
    df = pd.DataFrame(dict)
    df.to_csv(csv_name)

#Part2.2 csv of zstas
final_asp = zstat_table(recovery, reAsp, 'aspect.csv' )
final_slope = zstat_table(recovery, reSlope, 'slope.csv' )

#Part 2.3 geotif creation from recovery ratio
with rasterio.open('fire_perimeter.tif') as dataset:
    with rasterio.open (f'RR_Coefficent.tif','w',
        driver = 'Gtiff',
        height = recovery.shape[0],
        width = recovery.shape[1],
        count = 1,
        dtype = 'int8',
        crs = dataset.crs,
        transfrom = dataset.transform,
        nodata = 0
    )as out_raster:
        out_raster.write(recovery,1)

#Part 2.4 Final Print

print ("The less steep slopes and more soutern facing aspects of the burn area recovered faster in terms of vegetaion regrowth")


