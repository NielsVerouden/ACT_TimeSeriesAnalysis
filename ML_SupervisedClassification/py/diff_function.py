import rasterio as rio
import os
import matplotlib.pyplot as plt
from rasterio.plot import reshape_as_image
import pandas as pd
import matplotlib


def diff_map (raster_stack, polarization, threshold):
    
    # Load raster stacks as input
    input_folder = raster_stack
    
    # Set the output folder
    output_location = './data/DifferenceMaps/rasters'
    
    # Create output folder if it has not been created yet
<<<<<<< HEAD
    if not os.path.exists(output_location): os.mkdir(output_location)
=======
    # Create the folder: './data/DifferenceMaps'
    if not os.path.exists(output_location[0:21]):
        os.mkdir(output_location[0:21])
        
    # Create the folder: './data/DifferenceMaps/rasters'
    if not os.path.exists(output_location):
        os.mkdir(output_location)
>>>>>>> 76b2c6a25d9c09196d70330f42af97233fe5143e
        
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
            
        
        
    ## Create a list of all the difference maps
    list_diff_maps = os.listdir(output_location)
    
    # Create the path for opening the file
    # "[0:21]" is needed to remove the "rasters" part of the string,
    # because the files are in "./data/DifferenceMaps"
    diff_map = os.path.join(output_location, list_diff_maps[0])
    
    # Open the difference map
    diff_map_freq = rio.open(diff_map)
    
    # Read the difference map
    diff_map_freq = diff_map_freq.read()[0]
    
    # Open the difference maps
    # BE AWARE: it starts at 1 and not at 0, because the first difference
    # map is opened above and should not be added again.
    for i in range(1, len(list_diff_maps)):
        
        # Create the path for opening the file
        # "[0:21]" is needed to remove the "rasters" part of the string,
        # because the files are in "./data/DifferenceMaps"
        add_diff_map = os.path.join(output_location, list_diff_maps[i]) 
        
        # Open the difference map
        add_diff_map = rio.open(add_diff_map)
        
        # Read the difference map
        add_diff_map = add_diff_map.read()[0]
        
        # Add the add_diff_map to the diff_map_freq to create a frequency map
        diff_map_freq += add_diff_map
        
        
        
        
    # Create output name for the difference map frequency map
    # Get the first and last date
    first_date = min(list_dates)
    last_date = max(list_dates)
    
    # Create the total timespan
    tot_dates = first_date + '_' + last_date
    
    # Create output name
    out_name = '%sdiff_freq_map.tiff' %tot_dates
        
    output_diff_map_freq = os.path.join(output_location[0:21], out_name)
        
    with rio.open(output_diff_map_freq, "w",**meta) as dst:
            dst.write_band(1,diff_map_freq.astype(rio.float32))
            
    # Open the output again
    freq_map = rio.open(output_diff_map_freq)
    
    # Read the output
    #freq_map_read = freq_map.read()
    
    # Create very simple visualization:
    #output_diff_map_freq_plot = reshape_as_image(freq_map_read)
    

        

    #Define a colormap for the plotted image
    #cmap = matplotlib.cm.get_cmap('hsv').copy()
    #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["green","yellow","gold", "orange","darkorange", "red", "darkred"])
        
        
    #plt.figure()
    #c = plt.imshow(output_diff_map_freq, cmap=cmap)
    #plt.colorbar(c)
    #plt.suptitle(out_name)
    #plt.show()
            
    return freq_map





