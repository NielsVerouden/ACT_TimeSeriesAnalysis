#############################################################################################
########################################## IMPORT ###########################################
#############################################################################################

import re
import copy
import os
import sys
from datetime import datetime
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
####################################### THRESHOLDING ########################################
#############################################################################################

# for switching between inline and window plotting
%matplotlib qt
%matplotlib inline

input_name = 'input_zip'
dest_name = 'input_los'

def load_data2(input_name, dest_name):
    """ Function for unzipping downloaded files """
    # input_name =  folder containing multiple zip folders
    # dest_name =  destination folder of files from zip folders
    if not os.path.exists(dest_name): os.makedirs(dest_name)
    extension = ".zip"
    #image_names = []
    global dates
    dates=[] #initialize list of dates
    #Unzip files from input_name to a new folder
    for item in os.listdir(input_name): # loop through items in dir
        if item.endswith(extension): # check for ".zip" extension
            file_name =  os.path.join(input_name, item)  # get full path of files
            zip_ref = ZipFile(file_name) # create zipfile object
            zipinfos=zip_ref.infolist()
            for zipinfo in zipinfos:
                #change filename to something shorter
                date = zipinfo.filename[0:10]
                if date not in dates: dates.append(date) #append date to the list of unique dates
                info = zipinfo.filename[-79:]
                zipinfo.filename = date + '_' + info
                #image_names.append(zipinfo.filename)
                #extract image to destination folder
                zip_ref.extract(zipinfo, dest_name)
            zip_ref.close() # close file
            #os.remove(file_name) # delete zipped file    
    return

load_data2(input_name, dest_name)

def thresholding(array):
    """ Function for thresholding method for one array """
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

def apply_thresholding(dest_name):
    """ Function for applying tresholding method to the folder with unzipped tif files"""
    global list
    list = [tif for tif in os.listdir(dest_name) if '_VV_' in tif ]
    output = []
    for i in list:
        data = os.path.join(dest_name, i)
        data2 = rio.open(data)
        data2 = data2.read(1)
        data2 = lee_filter(data2, 5) 
        outputt = thresholding(data2) 
        output.append(outputt)
    return output
        
list_th = apply_thresholding(dest_name)

# some stats
def stats(image):
    stats = []
    stats.append({'min': image.min(), 
                  'mean': image.mean(), 
                  'median': np.median(image),
                  'max': image.max()})
    return stats 
stats(list_th[0])

show_hist(list_th[0], bins = 50, lw = 0.0, stacked = False, alpha = 0.3, histtype = 'stepfilled', title = "Histogram")

# visualise

dates = ['2021-03-31', '2021-04-02', '2021-04-05', '2021-04-07', '2021-04-12']

fig, axs = plt.subplots(2, 3)
for idx, image in enumerate(list_th):
    ax = axs[idx // 3][idx % 3]
    ax.imshow(image)
    ax.set_title(dates[idx])
    #ax[0].set_title('test')
    
plt.tight_layout()
plt.suptitle('Thresholding method for VV', fontweight = 'bold', fontsize = 13, y = 0.98)




"""
# visualise 
fig, axs = plt.subplots(2, 3)
for i in range(len(list_th)):
    imshow(list_th[i])

fig.suptitle('Horizontally stacked subplots')
axs[0].set_title('test')
axs[1].set_title('test')
axs[0].imshow(np.clip(tiff2 * 2.5 / 255, 0, 1))
axs[1].imshow(np.clip(tiff4.squeeze() * 2.5 / 255, 0, 1))

# create list with dates 
for i in list:
    dates=[]
    #date = i[0:10]
    dates.append(i[0:10])

for i in list:
    dates = []
    match_str = re.search(r'\d{4}-\d{2}-\d{2}', i)
    res = datetime.strptime(match_str.group(), '%Y-%m-%d').date()
    res = [date for date in res.strftime('%Y-%m-%d')]
    dates.append[res]
"""



    





















#########################################################################################################
######################################## JUST TRYING STUFF ##############################################
#########################################################################################################



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






 water = rio.open('occurrence_80W_30Nv1_3_2020.tif')
 water = water.read()
 water = reshape_as_image(water)














# speckle filter
test = [f for f in os.listdir('vv')]
apply_lee_filter(test, input_folder = vv_folder)

# speckle filter
load_data(input_folder, images_folder, stacked_images_folder)
test = [f for f in os.listdir('SentinelTimeSeriesStacked')]
apply_lee_filter(test, input_folder = stacked_images_folder)







file_list = ['file1.tif', 'file2.tif', 'file3.tif']

# Read metadata of first file
with rasterio.open(file_list[0]) as src0:
    meta = src0.meta

# Update meta to reflect the number of layers
meta.update(count = len(file_list))

# Read each layer and write it to stack
with rasterio.open('stack.tif', 'w', **meta) as dst:
    for id, layer in enumerate(file_list, start=1):
        with rasterio.open(layer) as src1:
            dst.write_band(id, src1.read(1))




