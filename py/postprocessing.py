#Post processing:
#Create frequency map of flood events (simple end product)

import rasterio as rio
import numpy as np
from rasterio.plot import reshape_as_image
from matplotlib import pyplot as plt
import matplotlib
import os
import subprocess
import numpy as np
from rasterio.features import sieve, shapes


# =============================================================================

def createFrequencyMap(masked_predictions_folder, output_folder):
    if not os.path.exists(output_folder): os.makedirs(output_folder)
   
    for filename in os.listdir(masked_predictions_folder):
        path = os.path.join(masked_predictions_folder, filename)
        with rio.open(path) as src:
            
            flood_predictions= src.read()
            meta = src.meta
            
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
            
            #1=flooded land (land is fields, agriculture, etc.):
            frequencymapLand[flood_predictions==1] += 1
            frequencymapLand[flood_predictions==100] = 100
            
            #1=flooded urban areas or land:
            frequencymapComb[flood_predictions==1] += 1
            frequencymapComb[flood_predictions==2] += 1
            frequencymapComb[flood_predictions==100] = 100
# =============================================================================
    #Save the frequency maps as tiff files:
    meta.update(count=1,
                dtype=rio.int8,
                compress='lzw')
    with rio.open(os.path.join(output_folder, "FloodFrequencyLand.tiff"), "w", **meta) as dst:
        dst.write(frequencymapLand)
    with rio.open(os.path.join(output_folder, "FloodFrequencyUrban.tiff"), "w", **meta) as dst:
        dst.write(frequencymapUrban)
    with rio.open(os.path.join(output_folder, "FloodFrequencyCombined.tiff"), "w", **meta) as dst:
        dst.write(frequencymapComb)       
# =============================================================================
    #very simple visualization:
    frequencymapComb_plot = reshape_as_image(frequencymapComb)
    frequencymapUrban_plot = reshape_as_image(frequencymapUrban)
    frequencymapLand_plot = reshape_as_image(frequencymapLand)
    maps={"Combined flood frequency map": frequencymapComb_plot, 
          "Urban flood frequency map": frequencymapUrban_plot, 
          "Flooded land frequency map": frequencymapLand_plot}
    
    #Display each frequency map:
    for title, freq_map in maps.items():
        
        permanent_water=100 
    
        masked_array = np.ma.masked_where(freq_map == permanent_water, freq_map)
    
        #Define a colormap for the plotted image
        cmap = matplotlib.cm.get_cmap('hsv').copy()
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["green","yellow","gold", "orange","darkorange", "red", "darkred"])
        
        #Define a colormap for permanent water (aqua = light blue)
        cmap.set_bad(color='aqua')
        
        plt.figure()
        c = plt.imshow(masked_array, cmap=cmap)
        plt.colorbar(c)
        plt.suptitle(title)
        plt.show()

    return


#credit: https://stackoverflow.com/questions/37719304/python-imshow-set-certain-value-to-defined-color
