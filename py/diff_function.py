import rasterio as rio
import os
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
from rasterio.mask import mask
from shapely.geometry import box


# List the files in the directory
list_files = os.listdir('./data/SentinelTimeSeriesStacked_Incl_DEM_GHS')

# Chek number of files in the directory
len(list_files)

# Create a function to get all the dates of the rasters
def get_dates(list_files):
    for i in range(0,len(list_files)):
        list_dates = list_files
        list_dates[i] = list_files[i][0:10]
    return(list_dates)

# Get the dates of all the rasters
list_dates = get_dates(list_files)

stack_1 = rio.open('./data/SentinelTimeSeriesStacked_Incl_DEM_GHS/2021-04-02_Stack_vv_vh_vvvh_ghs_dem.tiff')
stack_2 = rio.open('./data/SentinelTimeSeriesStacked_Incl_DEM_GHS/2021-04-05_Stack_vv_vh_vvvh_ghs_dem.tiff')
stack_3 = rio.open('./data/SentinelTimeSeriesStacked_Incl_DEM_GHS/2021-04-07_Stack_vv_vh_vvvh_ghs_dem.tiff')
stack_4 = rio.open('./data/SentinelTimeSeriesStacked_Incl_DEM_GHS/2021-04-12_Stack_vv_vh_vvvh_ghs_dem.tiff')


vv_1 = stack_1.read()[0]
vv_2 = stack_2.read()[0]
vv_3 = stack_3.read()[0]
vv_4 = stack_4.read()[0]

diff_1_2 = vv_2 - vv_1
diff_2_3 = vv_3 - vv_2
diff_3_4 = vv_4 - vv_3

diff_raster_1_2 = diff_1_2
diff_raster_2_3 = diff_2_3
diff_raster_3_4 = diff_3_4

plt.imshow(diff_raster_1_2)
plt.imshow(diff_raster_2_3)
plt.imshow(diff_raster_3_4)

def diff_city (raster):
    for i in range(0, len(raster)):
        for j in range(0, len(raster[0])):
            if raster[i][j] > 1000:
                raster[i][j] = 1
            else:
                raster[i][j] = 0
    return(raster)

city_1_2 = diff_city(diff_raster_1_2)
plt.imshow(city_1_2)

city_2_3 = diff_city(diff_raster_2_3)
plt.imshow(city_2_3)

city_3_4 = diff_city(diff_raster_3_4)
plt.imshow(city_3_4)



city_polys = gpd.read_file("./data/city_polygons/city_polygons.shp")

bounds = city_polys.bounds    
geom = box(*bounds)


minx, miny = -72.190091, 19.731434
maxx, maxy = -72.186256, 19.735062

bounds = box(minx, miny, maxx, maxy)




test, out_transform = mask(city_1_2, bounds, crop=True)













def remove_small_diff (diff_raster): 
    for i in range(0,len(diff_raster)):
        for j in range(0, len(diff_raster)):
            if diff_raster[i][j] < 2000 and diff_raster[i][j] > -2000:
                diff_raster[i][j] = 0
            else:
                diff_raster[i][j] = diff_raster[i][j]
    return(diff_raster)

big_diff = remove_small_diff(diff_1_2)
plt.imshow(big_diff)



























# Open data
stack_1 = rio.open('./data/SentinelTimeSeriesStacked_Incl_DEM_GHS/%s_Stack_vv_vh_vvvh_ghs_dem.tiff' % list_dates[0]

vvname = '%s*_VV_*.tiff' % date

'%s_Stack_vv_vh_vvvh_ghs_dem.tiff' % list_dates[0]
