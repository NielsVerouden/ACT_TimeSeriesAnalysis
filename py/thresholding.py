#############################################################################################
########################################## IMPORT ###########################################
#############################################################################################

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio.plot import show 
from rasterio.plot import show_hist
from rasterio.plot import reshape_as_image
from osgeo import gdal
from sklearn.cluster import KMeans

from utils2 import plot_image
from utils2 import plot_image2

from speckle_filter import lee_filter
from speckle_filter import apply_lee_filter
from load_data_from_zip_folders import load_data

# should exist
input_folder = 'input_folder'
human_settlement_folder = "human_settlement_folder"

# are made
images_folder = 'SentinelTimeSeries'
stacked_images_folder = 'SentinelTimeSeriesStacked'
vv_folder = 'vv'

#############################################################################################
############################################ GDAL ###########################################
#############################################################################################

# just exploring difference between gdal and rasterio

data = gdal.Open('2022-02-01-00 00_2022-02-01-23 59_Sentinel-1_AWS-IW-VVVH_VV_-_decibel_gamma0_-_radiometric_terrain_corrected(1).tiff')
band1 = data.GetRasterBand(1)
b1 = band1.ReadAsArray()

band1.GetStatistics(True, True)
band1.GetMetadata()
band1.GetMaximum()
band1.Getminimum()

#############################################################################################
########################################## RASTERIO ###########################################
#############################################################################################

# for switching between inline and window plotting
%matplotlib qt
%matplotlib inline

# single band
vv = rio.open('2022-02-01-00 00_2022-02-01-23 59_Sentinel-1_AWS-IW-VVVH_VV_-_decibel_gamma0_-_radiometric_terrain_corrected(1).tiff')
vv = vv.read(1)
vv = vv.astype('f4')

# some stats
def stats(image):
    stats = []
    stats.append({'min': image.min(), 
                  'mean': image.mean(), 
                  'median': np.median(image),
                  'max': image.max()})
    return stats 

stats(vv)

# speckle filter
vv_lee = lee_filter(vv, 5)

# reshape for visualising 
#vv_img = reshape_as_image(vv)
#plt.imshow(vv_img / vv_img.max())
show_hist(vv, bins = 50, lw = 0.0, stacked = False, alpha = 0.3, histtype = 'stepfilled', title = "Histogram")

# create 1D array by selecting only 1 band and multiplying rows with columns
#vv_1D = vv[0]
vv_1D = vv.reshape(vv.shape[0]*vv.shape[1], 1)

# kmeans clustering to find the midpoint of both peaks from the histogram
kmeans_vv = KMeans(n_clusters=2).fit(vv_1D)
cluster_center_vv = kmeans_vv.cluster_centers_
threshold_vv = (cluster_center_vv[0] + cluster_center_vv[1]) / 2 
threshold_vv = threshold_vv[0]

# all pixels below the threshold (1) are flooded, all pixels above (0) are non-flooded
vv[np.where(vv < threshold_vv)] = 1 
vv[np.where(vv > threshold_vv)] = 0


def apply_threshold(array):
    """ Function for threshold method """
    array_1D = array.reshape(array.shape[0] * array.shape[1], 1) # reshape to 1D array
    kmeans = KMeans(n_clusters = 2).fit(array_1D) # apply kmeans clustering
    cluster_center = kmeans.cluster_centers_
    
    # compute midpoint between the two cluster aka the threshold
    threshold = (cluster_center[0] + cluter_center[1]) / 2 
    threshold = threshold[0] 
    
    # crate binary flood map 
    # all pixels below the threshold (1) are flooded, all pixels above (0) are non-flooded
    array[np.where(array < threshold)] = 1
    array[np.where(array > threshold)] = 0














# create 1D array by selecting only 1 band and multiplying rows with columns
#vv_1D = vv[0]
vv_lee_1D = vv.reshape(vv_lee.shape[0]*vv_lee.shape[1], 1)

# kmeans clustering to find the midpoint of both peaks from the histogram
kmeans_vv_lee = KMeans(n_clusters=2).fit(vv_lee_1D)
cluster_center_vv_lee = kmeans_vv_lee.cluster_centers_
threshold_vv_lee = (cluster_center_vv_lee[0] + cluster_center_vv_lee[1]) / 2
threshold_vv_lee = threshold_vv_lee[0]

# all pixels below the threshold (1) are flooded, all pixels above (0) are non-flooded
vv_lee[np.where(vv_lee < threshold_vv_lee)] = 1 
vv_lee[np.where(vv_lee > threshold_vv_lee)] = 0

































# mask all values above threshold
vv_img[vv_img > threshold_vv] = np.nan
plt.imshow(vv_img)
plt.imshow(np.clip(vv * 2.5 / 255, 0, 1))
plot_image(vv, factor=3.5 / 255, clip_range=(0, 1))




# speckle filter
load_data(input_folder, images_folder, stacked_images_folder)
test = [f for f in os.listdir('SentinelTimeSeriesStacked')]
apply_lee_filter(test, input_folder = stacked_images_folder)

# stack
stack = rio.open('SentinelTimeSeriesStacked/2022-02-01_vv_vh_vvvhratio_Stack.tiff')
stack = stack.read()
stack = stack.astype('f4')
stack_img = reshape_as_image(stack)

new = tif2[0]
new = new.reshape(new.shape[0]*new.shape[1], 1)



kmeans = KMeans(n_clusters=2).fit(new)
cluster_center = kmeans.cluster_centers_
threshold = (cluster_center[0] + cluster_center[1]) / 2



show_hist(tif2, bins=50, lw=0.0, stacked=False, 
          alpha=0.3, histtype='stepfilled', title="Histogram")




%matplotlib inline
plt.imshow(tif3)



tif3[tif3 > th] = np.nan
plt.imshow(tif3 / 65535)

# Calculate statistics for each band
stats = []
for band in vv: 
    stats.append({
        'min': band.min(),
        'mean': band.mean(),
        'median': np.median(band),
        'max': band.max()})
print(stats)    


 




















vv = rio.open('2022-02-01-00 00_2022-02-01-23 59_Sentinel-1_AWS-IW-VVVH_VV_-_decibel_gamma0_-_radiometric_terrain_corrected(1).tiff')
vv = vv.read()
vv = vv.astype('f4')

# speckle filter
test = [f for f in os.listdir('vv')]
apply_lee_filter(test, input_folder = vv_folder)

# reshape for visualising 
vv_img = reshape_as_image(vv)
plt.imshow(vv_img / 65535)
show_hist(vv, bins = 50, lw = 0.0, stacked = False, alpha = 0.3, histtype = 'stepfilled', title = "Histogram")


vv_sf = rio.open('vv/2022-02-01-00 00_2022-02-01-23 59_Sentinel-1_AWS-IW-VVVH_VV_-_decibel_gamma0_-_radiometric_terrain_corrected(1).tiff')
vv_sf = vv_sf.read()
vv_sf = vv_sf.astype('f4')
vv_sf_img = reshape_as_image(vv_sf)
show_hist(vv_sf, bins = 50, lw = 0.0, stacked = False, alpha = 0.3, histtype = 'stepfilled', title = "Histogram")



plt.imshow(vv_sf_img / vv_sf.max())



















