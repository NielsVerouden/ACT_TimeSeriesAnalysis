#############################################################################################
########################################## IMPORT ###########################################
#############################################################################################

import copy
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow
import rasterio as rio
from rasterio.plot import show, show_hist, reshape_as_image
from osgeo import gdal
from sklearn.cluster import KMeans

from utils2 import plot_image, plot_image2

from speckle_filter import lee_filter, apply_lee_filter
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

vh = rio.open('2022-02-01-00 00_2022-02-01-23 59_Sentinel-1_AWS-IW-VVVH_VH_-_decibel_gamma0_-_radiometric_terrain_corrected.tiff')
vh = vh.read(1)
vh = vh.astype('f4')

# some stats
def stats(image):
    stats = []
    stats.append({'min': image.min(), 
                  'mean': image.mean(), 
                  'median': np.median(image),
                  'max': image.max()})
    return stats 
stats(vh)

# speckle filter
vv_lee = lee_filter(vv, 5)
vh_lee = lee_filter(vh, 5)

# reshape for visualising 
#vv_img = reshape_as_image(vv)
#plt.imshow(vv_img / vv_img.max())
show_hist(vh, bins = 50, lw = 0.0, stacked = False, alpha = 0.3, histtype = 'stepfilled', title = "Histogram")




# create 1D array by selecting only 1 band and multiplying rows with columns
#vv_1D = vv[0]
vv_1D = vh.reshape(vh.shape[0]*vh.shape[1], 1)

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
    
    # compute midpoint between the two clusters aka the threshold
    threshold = (cluster_center[0] + cluster_center[1]) / 2 
    threshold = threshold[0] 
    
    # crate binary flood map 
    # all pixels below the threshold (1) are flooded, all pixels above (0) are non-flooded
    output = copy.copy(array)
    #output = array
    output[np.where(output < threshold)] = 1
    output[np.where(output > threshold)] = 0
    
    return output

surface2 = apply_threshold(vv_lee)
bodies = apply_threshold(vv2_lee)
flood = surface - bodies 



    














water = rio.open('occurrence_80W_30Nv1_3_2020.tif')
water = water.read()
water = reshape_as_image(water)
























# stack
stack = rio.open('SentinelTimeSeriesStacked/2022-02-01_vv_vh_vvvhratio_Stack.tiff')
stack = stack.read()
stack = stack.astype('f4')
stack = reshape_as_image(stack)

#show_hist(stack, bins = 50, lw = 0.0, stacked = False, alpha = 0.3, histtype = 'stepfilled', title = "Histogram")

stack_1D = stack.reshape(stack.shape[0]*stack.shape[1]*stack.shape[2], 1)
kmeans = KMeans(n_clusters=3).fit(stack_1D)
cluster_center = kmeans.cluster_centers_
threshold = (cluster_center[1] + cluster_center[2]) / 2

stack[stack > threshold] = np.nan
plt.imshow(stack)
plt.imshow(stack / stack.max())






 














# speckle filter
test = [f for f in os.listdir('vv')]
apply_lee_filter(test, input_folder = vv_folder)

# speckle filter
load_data(input_folder, images_folder, stacked_images_folder)
test = [f for f in os.listdir('SentinelTimeSeriesStacked')]
apply_lee_filter(test, input_folder = stacked_images_folder)










