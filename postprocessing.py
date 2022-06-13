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
            img = src.read()
            kwargs = src.meta
            kwargs.update(
                    dtype=rio.float32,
                    count=1,
                    compress='lzw')
            if 'frequencymap' not in locals(): 
                frequencymap = np.zeros_like(img)
            img[img > 0] = 1
            frequencymap = np.add(frequencymap,img)
            
    #very simple visualization:
    frequencymap_plot = reshape_as_image(frequencymap)

    c = plt.imshow(frequencymap_plot, cmap='jet')
    plt.colorbar(c)
    plt.show()
    return(frequencymap)


