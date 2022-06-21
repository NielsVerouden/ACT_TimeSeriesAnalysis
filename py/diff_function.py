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
            if raster[i][j] > 20000:
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

plt.imshow(diff_1_2_vv)





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



# Create if function for the i to prevent that it is more than the length


def diff_map (folder_location, metadata_file):
    # Create output folder
    if not os.path.exists(output_location):
        os.mkdir(output_location)
    
    # Create a list of the files
    list_files = os.listdir(folder_location)
    
    # Get the dates of all the input files
    for i in range(0,len(list_files)):
        list_dates = list_files
        list_dates[i] = list_files[i][0:10]
    
    # Create a list of the files, because the former is overwritten
    list_files = os.listdir(folder_location)
    
    # Substract rasters from each other
    for i in range(0, len(list_files)-1):
        
        raster_name_1 = os.path.join(folder_location, list_files[i]) 
        raster_name_2 = os.path.join(folder_location, list_files[i+1]) 
        
        raster_1 = rio.open(raster_name_1)
        raster_2 = rio.open(raster_name_2)
        
        diff_raster = raster_2.read()[0] - raster_1.read()[0]
        
        # Create only 0 and 1 values
        diff_raster[diff_raster>30000] = 1
        diff_raster[diff_raster<=30000] = 0

                
     
        # Create outputname
        dates = list_dates[i] +'_' + list_dates[i+1]
        output_name = '%s_diff_raster.tiff' % dates
        diff_raster_filepath=os.path.join(output_location,output_name)
    
        # Open the metadata
        #with rio.open(metadata_file,"r") as vv:
        meta=raster_1.meta
        #vv_data=vv.read(1)
              
        #Update meta to fit three layers
        meta.update(count=1)
        meta.update(dtype=rio.float32)
        
        with rio.open(diff_raster_filepath, "w",**meta) as dst:
            dst.write_band(1,diff_raster.astype(rio.float32))

    
    return(print('\n' + output_name + ' has been saved in ' + output_location))



diff_map(folder_location, metadata_file)



raster_1 = rio.open('./data/DifferenceMaps/2021-04-02_2021-04-05_diff_raster.tiff')
raster_2 = rio.open('./data/DifferenceMaps/2021-04-05_2021-04-07_diff_raster.tiff')
raster_3 = rio.open('./data/DifferenceMaps/2021-04-07_2021-04-12_diff_raster.tiff')
raster_4 = rio.open('./data/DifferenceMaps/2021-04-12_2021-04-14_diff_raster.tiff')
raster_5 = rio.open('./data/DifferenceMaps/2021-04-14_2021-04-17_diff_raster.tiff')

plt.imshow(raster_1)
plt.imshow(raster_2)
plt.imshow(raster_3)
plt.imshow(raster_4)
plt.imshow(raster_5)





















        # Get only 1 and 0 values to distuingish flooded and non-flooded cities better
        for j in range(0, len(diff_raster)):
            for k in range(0, len(diff_raster[0])):
                if diff_raster[j][k] > 30000:
                    diff_raster[j][k] = 1
                else:
                    diff_raster[j][k] = 0




    for filename in filenames:
        with rio.open(filename) as src:
            
            flood_predictions= src.read()

            if 'frequencymapComb' not in locals(): 
                frequencymapComb = np.zeros_like(flood_predictions)
            if 'frequencymapUrban' not in locals(): 
                frequencymapUrban = np.zeros_like(flood_predictions)
            if 'frequencymapLand' not in locals(): 
                frequencymapLand = np.zeros_like(flood_predictions)
                
            #Create binary rasters where 0 is non-flooded, 1 is flooded
            #1=flooded urban areas:
            frequencymapUrban[flood_predictions==2] += 1
            frequencymapUrban[flood_predictions==100] = 100
    





