#Post processing:
#Create frequency map of flood events (simple end product)

import rasterio as rio
import numpy as np
from rasterio.plot import reshape_as_image
from matplotlib import pyplot as plt

def createFrequencyMap(filenames):
    
    #Simple frequency map that does not distinguish flooded cities from flooded land areas:
    for filename in filenames:
        with rio.open(filename) as src:
            combined_flooding = src.read()
            flooded_urban = src.read()
            flooded_land = src.read()
            
            #Create binary rasters where 0 is non-flooded, 1 is flooded
            #1=flooded urban areas:
            flooded_urban[flooded_urban!=2] = 0
            flooded_urban[flooded_urban==2]=1
            
            #1=flooded land (land is fields, agriculture, etc.):
            flooded_land[flooded_land!=1] = 0
            
            #1=flooded urban areas or land:
            combined_flooding[combined_flooding > 0] = 1
            
            kwargs = src.meta
            kwargs.update(
                    dtype=rio.float32,
                    count=1,
                    compress='lzw')
            
            if 'frequencymapComb' not in locals(): 
                frequencymapComb = np.zeros_like(combined_flooding)
            if 'frequencymapUrban' not in locals(): 
                frequencymapUrban = np.zeros_like(combined_flooding)
            if 'frequencymapLand' not in locals(): 
                frequencymapLand = np.zeros_like(combined_flooding)
                
            frequencymapComb = np.add(frequencymapComb,combined_flooding)
            frequencymapUrban = np.add(frequencymapUrban,flooded_urban)
            frequencymapLand = np.add(frequencymapLand,flooded_land)
            
    #very simple visualization:
    frequencymapComb_plot = reshape_as_image(frequencymapComb)
    frequencymapUrban_plot = reshape_as_image(frequencymapUrban)
    frequencymapLand_plot = reshape_as_image(frequencymapLand)
    maps={"Combined flood frequency map": frequencymapComb_plot, 
          "Urban flood frequency map": frequencymapUrban_plot, 
          "Flooded land frequency map": frequencymapLand_plot}
    
    #Display each frequency map:
    for title, freq_map in maps.items():
        plt.figure()
        c = plt.imshow(freq_map, cmap='jet')
        plt.colorbar(c)
        plt.suptitle(title)
        plt.show()
        
    return(maps)


