import rasterio as rio
import os
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
from rasterio.mask import mask
from shapely.geometry import box

# Set the folder location
folder_location = './data/SentinelTimeSeriesStacked_Incl_DEM_GHS'
output_location = './data/DifferenceMaps'

# Use a file to get the 
metadata_file = './data/SentinelTimeSeriesStacked_Incl_DEM_GHS/2021-04-02_Stack_vv_vh_vvvh_ghs_dem.tiff'

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

# Open the first layers: vv
vv_1 = stack_1.read()[0]
vv_2 = stack_2.read()[0]
vv_3 = stack_3.read()[0]
vv_4 = stack_4.read()[0]

# Open the second layers: vh
vh_1 = stack_1.read()[1]
vh_2 = stack_2.read()[1]
vh_3 = stack_3.read()[1]
vh_4 = stack_4.read()[1]

# Open the third layers: vv/vh
vv_vh_1 = stack_1.read()[2]
vv_vh_2 = stack_2.read()[2]
vv_vh_3 = stack_3.read()[2]
vv_vh_4 = stack_4.read()[2]

# Calculate the difference between two bands
diff_1_2_vv = vv_2 - vv_1
diff_2_3_vv = vv_3 - vv_2
diff_3_4_vv = vv_4 - vv_3

diff_1_2_vh = vh_2 - vh_1
diff_2_3_vh = vh_3 - vh_2
diff_3_4_vh = vh_4 - vh_3

diff_ratio_1_2 = vv_vh_1 - vv_vh_2
diff_ratio_2_3 = vv_vh_2 - vv_vh_3
diff_ratio_3_4 = vv_vh_3 - vv_vh_4

# Sum the differences from both layers: vv + vh
sum_diff_1_2 = diff_1_2_vv + diff_1_2_vh
sum_diff_2_3 = diff_2_3_vv + diff_2_3_vh
sum_diff_3_4 = diff_3_4_vv + diff_3_4_vh


# Get only 1 and 0 values to distuingish flooded and non-flooded cities better
def diff_city (raster):
    for i in range(0, len(raster)):
        for j in range(0, len(raster[0])):
            if raster[i][j] > 30000:
                raster[i][j] = 1
            else:
                raster[i][j] = 0
    return(raster)

city_1_2_vv = diff_city(diff_1_2_vv)
plt.imshow(city_1_2_vv)
plt.title('Difference vv ' + list_dates[0] + '_' + list_dates[1])
plt.show()

city_2_3_vv = diff_city(diff_2_3_vv)
plt.imshow(city_2_3_vv)
plt.title('Difference vv ' + list_dates[1] + '_' + list_dates[2])
plt.show()

city_3_4_vv = diff_city(diff_3_4_vv)
plt.imshow(city_3_4_vv)
plt.title('Difference vv ' + list_dates[2] + '_' + list_dates[3])
plt.show()






city_1_2_vh = diff_city(diff_1_2_vh)
plt.imshow(city_1_2_vh)
plt.title('Difference vh ' + list_dates[0] + '_' + list_dates[1])
plt.show()

city_2_3_vh = diff_city(diff_2_3_vh)
plt.imshow(city_2_3_vh)
plt.title('Difference vh ' + list_dates[1] + '_' + list_dates[2])
plt.show()

city_3_4_vh = diff_city(diff_3_4_vh)
plt.imshow(city_3_4_vh)
plt.title('Difference vh ' + list_dates[2] + '_' + list_dates[3])
plt.show()








# Plot the results
plt.imshow(diff_1_2_vv)
plt.imshow(diff_2_3_vv)
plt.imshow(diff_3_4_vv)

plt.imshow(diff_1_2_vh)
plt.imshow(diff_2_3_vh)
plt.imshow(diff_3_4_vh)

plt.imshow(diff_ratio_1_2)
plt.imshow(diff_ratio_2_3)
plt.imshow(diff_ratio_3_4)

plt.imshow(sum_diff_1_2)
plt.imshow(sum_diff_2_3)
plt.imshow(sum_diff_3_4)




def diff_map (raster_1, raster_2, folder_location, output_location, metadata_file, list_dates):
    # Create output folder
    if not os.path.exists(output_location):
        os.mkdir(output_location)
    
    
    # Create a list of the files
    list_files = os.listdir(folder_location)
    
    # Get the dates of all the input files
    for i in range(0,len(list_files)):
        list_dates = list_files
        list_dates[i] = list_files[i][0:10]
    
        # Substract raster_1 from raster_2
        diff_raster = raster_2 - raster_1
    
    # Get only 1 and 0 values to distuingish flooded and non-flooded cities better
    for i in range(0, len(diff_raster)):
        for j in range(0, len(diff_raster[0])):
            if diff_raster[i][j] > 30000:
                diff_raster[i][j] = 1
            else:
                diff_raster[i][j] = 0
                
    # Plot the difference raster
    plt.imshow(diff_raster)
    plt.title('Difference_' + list_dates[0] + '_' + list_dates[1])
    plt.show()
     
    # Create outputname
    dates = list_dates[0] +'_' + list_dates[1]
    output_name = '%s_diff_raster.tiff' % dates
    diff_raster_filepath=os.path.join(output_location,output_name)
    
    # Open the metadata
    with rio.open(metadata_file,"r") as vv:
        meta=vv.meta
        vv_data=vv.read(1)
              
    #Update meta to fit three layers
    meta.update(count=3)
    meta.update(dtype=rio.float32)
        
    with rio.open(diff_raster_filepath, "w",**meta) as dst:
       dst.write_band(1,vv_data.astype(rio.float32))

    
    return(print('\n' + output_name + ' has been saved in ' + output_location))
    

diff_map(vv_1, vv_2, folder_location, output_location, metadata_file, list_dates)
    





