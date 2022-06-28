# =============================================================================
# IMPORTS
# =============================================================================

import copy
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow
import rasterio as rio
from rasterio.plot import show_hist
from sklearn.cluster import KMeans

# =============================================================================
# STEP 1: APPLY THRESHOLDING
# =============================================================================

def thresholding(array):
    """ Function that includes thresholding method for one array """
    array_1D = array.reshape(array.shape[0] * array.shape[1], 1) # reshape to 1D array
    kmeans = KMeans(n_clusters = 2).fit(array_1D) # apply kmeans clustering
    cluster_center = kmeans.cluster_centers_
    
    # compute midpoint between the two clusters aka the threshold
    threshold = (cluster_center[0] + cluster_center[1]) / 2 
    threshold = threshold[0] 
    
    # crate binary flood map 
    # all pixels below the threshold (1) are flooded, all pixels above (0) are non-flooded
    output = copy.copy(array)
    output[np.where(output < threshold)] = 0.0001
    output[np.where(output > threshold)] = 0
    
    return output

def apply_thresholding(dest_name):
    """ Function that applies tresholding method to the folder with unzipped and filtered tif files"""
    dates = [] # list of dates for visualisation
    images = [] # list of images without thresholding
    output = [] # list of images with thresholding
    for i in os.listdir(dest_name):
        dates.append(i[0:10])
        data = os.path.join(dest_name, i) # open and read tif files
        data2 = rio.open(data)
        data2 = data2.read(1) # get only first band (vv)
        images.append(data2)
        output.append(thresholding(data2)) # call thresholding function on all files

    return output, images, dates
        
# =============================================================================
# STEP 2: VISUALISE 
# =============================================================================

def show_stats(image):
    """ Function that computes statistics and shows histogram for one image """
    stats = []
    stats.append({'min': np.nanmin(image), 
                  'mean': np.nanmean(image), 
                  'median': np.nanmedian(image),
                  'max': np.nanmax(image)})
    hist = show_hist(image, bins = 50, lw = 0.0, stacked = False, alpha = 0.3, histtype = 'stepfilled', title = "Histogram")
    return stats, hist 
    
def visualise(images, nrows, ncols, dates, title='Title'):
    """ Function that visualises images to which thresholding is applied """
    plt.figure()
    plt.suptitle(title, fontsize = 18, x = 0.51, y = 0.98)
    for n, image in enumerate(images):
        ax = plt.subplot(nrows, ncols, n + 1)
        ax.imshow(image)
        ax.set_title(dates[n])
        ax.set_xticks([])
        ax.set_yticks([])
