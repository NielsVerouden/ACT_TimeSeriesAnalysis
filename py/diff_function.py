import rasterio as rio
import os
import matplotlib.pyplot as plt


def diff_map ():
    
    # Set the folder location
    input_folder = './data/SentinelTimeSeriesStacked_Incl_DEM_GHS'
    output_location = './data/DifferenceMaps'
    
    # Create output folder if it has not been created yet
    if not os.path.exists(output_location):
        os.mkdir(output_location)
        
    # List the files in the directory
    list_files = os.listdir(input_folder)
    
    # Create a list of the files
    list_files = os.listdir(input_folder)
    
    # Get the dates of all the input files
    ## This is needed later for naming the files
    for i in range(0,len(list_files)):
        list_dates = list_files
        list_dates[i] = list_files[i][0:10]
    
    # Create a list of the files, because the former is overwritten
    list_files = os.listdir(input_folder)
    
    # Substract rasters from each other
    ## This will be done for all consecutive rasters due to the for loop
    for j in range(0, len(list_files)-1):
        
        raster_name_1 = os.path.join(input_folder, list_files[j]) 
        raster_name_2 = os.path.join(input_folder, list_files[j+1]) 
        
        raster_1 = rio.open(raster_name_1)
        raster_2 = rio.open(raster_name_2)
        
        diff_raster = raster_2.read()[0] - raster_1.read()[0]
        
        ###################### This does not work #############################
        # Create only 0 and 1 values
        #diff_raster[diff_raster>20000] = 1
        #diff_raster[diff_raster<=20000] = 0
        
        # Get only 1 and 0 values to distuingish flooded and non-flooded cities better
        ## Create a function to do it
        ## Only the parts that have big difference will be shown
        ## This threshold can be changed, it is now set at 30000
        def diff_city (diff_raster):
            for i in range(0, len(diff_raster)):
                for j in range(0, len(diff_raster[0])):
                    if diff_raster[i][j] > 30000:
                        diff_raster[i][j] = 1
                    else:
                        diff_raster[i][j] = 0
            return(diff_raster)
        
        # Call the function
        diff_raster = diff_city(diff_raster)
        
        
        # Create outputname
        dates = list_dates[j] +'_' + list_dates[j+1]
        output_name = '%s_diff_raster.tiff' % dates
        diff_raster_filepath=os.path.join(output_location,output_name)
    
        # Open the metadata
        meta=raster_1.meta
              
        #Update metadata
        meta.update(count=1)
        meta.update(dtype=rio.float32)
        
        with rio.open(diff_raster_filepath, "w",**meta) as dst:
            dst.write_band(1,diff_raster.astype(rio.float32))
    return









"""

Kan de backscatter in een stad afnemen? Dan zou het nadat het afgenomen is, 
wanneer het dan weer toeneemt gezien worden als een overstroming

Het kunnen stacken moet nog kunnen

Misschien het combineren met het model van Niels en Raimon


"""

























"""
def open_diffmaps ():
    
    diff_map_folder = './data/DifferenceMaps'
    
    # Create a list of the files
    list_files = os.listdir(diff_map_folder)
    
    # Get the dates of all the input files
    for i in range(0,len(list_files)):
        list_dates = list_files
        list_dates[i] = list_files[i][0:10]
    
    # Create a list of the files, because the former is overwritten
    list_files = os.listdir(folder_location)
    
    



raster_1 = rio.open('./data/DifferenceMaps/2021-04-02_2021-04-05_diff_raster.tiff')
raster_2 = rio.open('./data/DifferenceMaps/2021-04-05_2021-04-07_diff_raster.tiff')
raster_3 = rio.open('./data/DifferenceMaps/2021-04-07_2021-04-12_diff_raster.tiff')
raster_4 = rio.open('./data/DifferenceMaps/2021-04-12_2021-04-14_diff_raster.tiff')
raster_5 = rio.open('./data/DifferenceMaps/2021-04-14_2021-04-17_diff_raster.tiff')

plt.imshow(raster_1.read()[0])
plt.imshow(raster_2.read()[0])
plt.imshow(raster_3.read()[0])
plt.imshow(raster_4.read()[0])
plt.imshow(raster_5.read()[0])












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
    

"""



