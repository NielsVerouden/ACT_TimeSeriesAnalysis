import rasterio as rio
import os
import matplotlib.pyplot as plt
import pandas as pd


def diff_map (raster_stack, polarization, threshold):
    
    # Load raster stacks as input
    input_folder = raster_stack
    
    # Set the output folder
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
    
    # Select the correct polarization
    if polarization == 'vv':
        pol = 0
    elif polarization == 'vh':
        pol = 1
    elif polarization == 'ratio':
        pol = 2
    else:
        pol = 0
        print('Only, "vv", "vh", and "ratio" are correct parameters for the polarization. Now the vv has been chosen, if another polarization is wanted please ruen the function again with the correct parameter.') 
    
    # Substract rasters from each other
    ## This will be done for all consecutive rasters due to the for loop
    for j in range(0, len(list_files)-1):
        
        raster_name_1 = os.path.join(input_folder, list_files[j]) 
        raster_name_2 = os.path.join(input_folder, list_files[j+1]) 
        
        raster_1 = rio.open(raster_name_1)
        raster_2 = rio.open(raster_name_2)
        
        diff_raster = raster_2.read()[pol] - raster_1.read()[pol]
        
        # Get the threshold with the percentage        
        # Create a dataframe
        diff_raster_df = pd.DataFrame(diff_raster)
        
        # Get the maximum and minimum value of the dataframe
        max_pixel = abs(diff_raster_df.max().max())
        
        # Create the threshold value from the percentage
        threshold_val = threshold * max_pixel
                
        # Get only 1 and 0 values to distuingish flooded and non-flooded cities better
        ## Create a function to do it
        ## Only the parts that have big difference will be shown
        ## This threshold can be changed, it is now set at 30000
        def diff_city (diff_raster):
            for i in range(0, len(diff_raster)):
                for j in range(0, len(diff_raster[0])):
                    if diff_raster[i][j] > threshold_val:
                        diff_raster[i][j] = 1
                    else:
                        diff_raster[i][j] = 0
            return(diff_raster)
        
        # Call the function
        diff_raster = diff_city(diff_raster)

        
        # Create outputname
        name = list_dates[j] +'_' + list_dates[j+1] +'_' + polarization
        output_name = '%s_diff_raster.tiff' % name
        diff_raster_filepath=os.path.join(output_location,output_name)
    
        # Open the metadata
        meta=raster_1.meta
              
        #Update metadata
        meta.update(count=1)
        meta.update(dtype=rio.float32)
        
        with rio.open(diff_raster_filepath, "w",**meta) as dst:
            dst.write_band(1,diff_raster.astype(rio.float32))
    return





