from rasterio.plot import show
import rasterio as rio
from rasterio.plot import show_hist
import matplotlib.pyplot as plt
import numpy as np
from rasterio.plot import reshape_as_image
import glob

def show_histograms(filenames):
    filenames_sorted = sorted(filenames)
    for id in range(0,len(filenames_sorted)):
        title = str(filenames_sorted[id][-21:-11])
        with rio.open(filenames_sorted[id],'r') as src:

            fig, axhist = plt.subplots(1, 1, figsize=(20, 20))
            show_hist(src, ax=axhist, bins=100, lw=0.0, stacked=False, 
                      alpha=0.3, histtype='stepfilled', density=True)
    
            axhist.set_title(title, size=60)
            axhist.legend(list(src.descriptions), prop={'size': 40})
            #axhist.set_ylim([0,0.01])
            plt.show()
            #optional: add code to save histograms in a folder

def show_backscatter(filenames):
    filenames_sorted = sorted(filenames)
    for id in range(0,len(filenames_sorted)):
        title = str(filenames_sorted[id][-21:-11]) #select date as title
        with rio.open(filenames_sorted[id],'r') as src:
            show(src,title=title, transform=src.transform)
         
"""           
for id in range(0,len(stacked_rasters_names)):
    title = str(stacked_rasters_names[id][-21:-11]) #select date as title
    with rio.open(stacked_rasters_names[id],'r') as src:
        show(src,title=title, transform=src.transform)
"""

######Visualize:
def visualizePrediction(predictions):
    for date, prediction in predictions.items():
        #search for files in the directory with stacked images
        pattern = 'radar_time_series_stacked/*%s*.tiff' % date
        for file in glob.glob(pattern):
            image_path = file
            
        with rio.open(image_path) as src:
            # may need to reduce this image size if your kernel crashes, takes a lot of memory
            img = src.read()
        
        # Take our full image and reshape into long 2d array (nrow * ncol, nband) for classification
        reshaped_img = reshape_as_image(img)
        
        def color_stretch(image, index):
            colors = image[:, :, index].astype(np.float64)
            for b in range(colors.shape[2]):
                colors[:, :, b] = rio.plot.adjust_band(colors[:, :, b])
            return colors
            
        # find the highest pixel value in the prediction image
        n = int(np.max(prediction))
        
        # next setup a colormap for our map
        colors = dict((
            (0, (139,69,19, 255)),      # Brown - dry area
            (1, (48, 156, 214, 255)),    # Blue - flooded
            (2, (96, 19, 134, 255)),    # Purple - flooded urban
        ))
        
        # Put 0 - 255 as float 0 - 1
        for k in colors:
            v = colors[k]
            _v = [_v / 255.0 for _v in v]
            colors[k] = _v
            
        index_colors = [colors[key] if key in colors else 
                        (255, 255, 255, 0) for key in range(0, n+1)]
        
        cmap = plt.matplotlib.colors.ListedColormap(index_colors, 'Classification', n+1)
        fig, axs = plt.subplots(2,1,figsize=(10,7))
        
        img_stretched = color_stretch(reshaped_img, [0,1,2])
        axs[0].imshow(img_stretched)
        
        axs[1].imshow(prediction, cmap=cmap, interpolation='none')
        fig.suptitle(date)
        fig.show()
    #credit: http://patrickgray.me/open-geo-tutorial/chapter_5_classification.html
    

"""
date = list(prediction.keys())[0]
pattern = 'radar_time_series_stacked/*%s*.tiff' % date
print(pattern)
for file in glob.glob(pattern):
    print(file)
    """