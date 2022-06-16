############################################################################## 
# IMPORTING AND CONFIGURATION
##############################################################################

from sentinelhub import SHConfig
config = SHConfig()

config.instance_id = '1fc73689-68c6-4f09-aba0-fa6d7c80aee9'
config.sh_client_id = 'feafa876-6d36-46e9-8f06-6125aaf70157'
config.sh_client_secret = '3+.y(0GObjs}HG0zhvi<~MMG#|NP?!9AT&U&M9+c'

config.save()

import os
import datetime 
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal
import rasterio as rs
import rasterio.plot
import pyproj
from rasterio.plot import show
from rasterio.plot import show_hist

from sentinelhub import (
    MimeType,
    CRS,
    BBox,
    SentinelHubRequest,
    SentinelHubDownloadClient,
    DataCollection,
    bbox_to_dimensions,
    DownloadRequest,
    #MosaickingOrder,
)

from utils import plot_image

##############################################################################
# DEFINE BBOX
##############################################################################

caphaitien_coords = [-72.273903,19.671135,-72.159233,19.798714]
resolution = 10
caphaitien_bbox = BBox(bbox = caphaitien_coords, crs = CRS.WGS84)
caphaitien_size = bbox_to_dimensions(caphaitien_bbox, resolution = resolution)


sudest_coords = [-72.419128,18.213372,-72.287807,18.274835]
resolution = 10
sudest_bbox = BBox(bbox = sudest_coords, crs = CRS.WGS84)
sudest_size = bbox_to_dimensions(sudest_bbox, resolution = resolution)


nordouest_coords = [-72.083359,19.594725,-71.882858,19.745378]
resolution = 10
nordouest_bbox = BBox(bbox = nordouest_coords, crs = CRS.WGS84)
nordouest_size = bbox_to_dimensions(nordouest_bbox, resolution = resolution)

##############################################################################
# EVALSCRIPTS
##############################################################################

# Part of this code is from https://apps.sentinel-hub.com/eo-browser

# An evalscipt is a piece of Javascript code which defines how the satellite data
# shall be processed by Sentinel Hub and what values the service shall return.
# 
# Source: https://docs.sentinel-hub.com/api/latest/evalscript/:



evalscript = """
    //VERSION=3

    function setup() {
        return {
            input: ['VV'],
            output: {bands: 1}
        };
    }

    function evaluatePixel(sample) {
        return [sample.VV];
    }
"""



evalscript_VH_dec = """
    //VERSION=3
    
    function setup() {
        return {
            input: ["VH", "dataMask"],
            output: [
                { id: "default", bands: 4 },
                { id: "eobrowserStats", bands: 1 },
                { id: "dataMask", bands: 1 },
            ],
        };
    }

    function evaluatePixel(samples) {
        const value = Math.max(0, Math.log(samples.VH) * 0.21714724095 + 1);

        return {
            default: [value, value, value, samples.dataMask],
            eobrowserStats: [(10 * Math.log(samples.VH)) / Math.LN10],
            dataMask: [samples.dataMask],
        };
    }

    // ---
    /*
    // displays VH in decibels from -20 to 0
    // the following is simplified below
    // var log = 10 * Math.log(VH) / Math.LN10;
    // var val = Math.max(0, (log + 20) / 20);

    return [Math.max(0, Math.log(VH) * 0.21714724095 + 1)];
    */
"""

evalscript_VV_dec = """
    //VERSION=3
    
    function setup() {
        return {
            input: ["VV", "dataMask"],
            output: [
                { id: "default", bands: 4 },
                { id: "eobrowserStats", bands: 1 },
                { id: "dataMask", bands: 1 },
            ],
        };
    }

    function evaluatePixel(samples) {
        const value = Math.max(0, Math.log(samples.VV) * 0.21714724095 + 1);

        return {
            default: [value, value, value, samples.dataMask],
            eobrowserStats: [(10 * Math.log(samples.VV)) / Math.LN10],
            dataMask: [samples.dataMask],
        };
    }

    // ---
    /*
    // displays VV in decibels from -20 to 0
    // the following is simplified below
    // var log = 10 * Math.log(VV) / Math.LN10;
    // var val = Math.max(0, (log + 20) / 20);

    return [Math.max(0, Math.log(VV) * 0.21714724095 + 1)];
    */
"""

evalscript_VV_lin = """
    //VERSION=3
    
    function setup() {
        return {
            input: ["VV", "dataMask"],
            output: [
                { id: "default", bands: 4 },
                { id: "eobrowserStats", bands: 1 },
                { id: "dataMask", bands: 1 },
            ],
        };
    }

    function evaluatePixel(samples) {
        return {
            default: [2 * samples.VV, 2 * samples.VV, 2 * samples.VV, samples.dataMask],
            eobrowserStats: [samples.VV],
            dataMask: [samples.dataMask],
        };
    }
"""

##############################################################################
# REQUEST ONE IMAGE
##############################################################################

# part of this code is from:
# https://sentinelhub-py.readthedocs.io/en/latest/examples/process_request.html#Example-1:-True-color-(PNG)-on-a-specific-date

request_130 = SentinelHubRequest(
    data_folder = 'test_dir',
    evalscript=evalscript,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL1,
            time_interval=("2022-02-01", "2022-02-02"),
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=caphaitien_bbox,
    size=caphaitien_size,
    config=config,
)

imgs_130 = request_130.get_data #(save_data = True)
image_130 = imgs_130[0]
print(f"Image type: {image_130.dtype}")
# plot function
# factor 1/255 to scale between 0-1
# factor 3.5 to increase brightness
plot_image(image_130, factor=3.5 / 255, clip_range=(0, 1))
plot_image(image_130)
plt.imshow(image_130)
show_hist(image_130)


##############################################################################
# RASTERIO
##############################################################################

haitien21 = 'test_dir\\ab8017738496a6e504e42a5a5a8cd3ca\\response.tiff'
haitien130 = 'test_dir\\66e6af5071361625a142d926df8aa87c\\response.tiff'

with rs.open(filepath) as src:
    print(src.profile)

with rs.open(haitien130) as src:
    new = src.read()
    new = new.astype('f4')
    new[new<5] = np.nan

show(new)

with rs.open(haitien130) as src:
    src = src.astype('f4')
    src[src<5] = np.nan
    show(src)
    

tiff = rs.open(haitien21)
tiff2 = tiff.read()
tiff2 = tiff2.astype('f4')
tiff2[tiff2 < 5] = np.nan
show(tiff2)

tiff3 = rs.open(haitien130)
tiff4 = tiff3.read()
tiff4 = tiff4.astype('f4')
tiff4[tiff4 < 5] = np.nan
show(tiff2)

tiff.plot()

tiff2 = gdal.Open(filepath)


# VISUALISE 
fig, axs = plt.subplots(1, 2)
fig.suptitle('Horizontally stacked subplots')
axs[0].set_title('test')
axs[1].set_title('test')
axs[0].imshow(np.clip(tiff2.squeeze() * 2.5 / 255, 0, 1))
axs[1].imshow(np.clip(tiff4.squeeze() * 2.5 / 255, 0, 1))

##############################################################################
# REQUEST TIME SERIES
##############################################################################

##############################################################################
# CAPHAITIEN
##############################################################################

# part of this code is from:
# https://sentinelhub-py.readthedocs.io/en/latest/examples/process_request.html#Example-8-:-Multiple-timestamps-data

# possible way of getting slots, but can result in duplicate images if one image falls within multiple slots
start = datetime.datetime(2022, 1, 16)
end = datetime.datetime(2022, 2, 15)
n_chunks = 12
tdelta = (end - start) / n_chunks
edges = [(start + i * tdelta).date().isoformat() for i in range(n_chunks)]
slots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]

print("Monthly time windows:\n")
for slot in slots:
    print(slot)

# feb 1, 2022
slots = [('2022-01-18'), 
         ('2022-01-20'), 
         ('2022-01-25'),
         ('2022-01-27'),
         ('2022-01-30'),
         ('2022-02-01'),
         ('2022-02-06'),
         ('2022-02-08'),
         ('2022-02-11'),
         ('2022-02-13')]

# april 4, 2021
slots = [('2021-03-26'), 
         ('2021-03-31'),
         ('2021-04-02'), 
         ('2021-04-05'),
         ('2021-04-07'),  
         ('2021-04-12'),
         ('2021-04-14')]

def get_caphaitien_request(time_interval):
    return SentinelHubRequest(
        # data_folder = 'caphaitien',
        evalscript=evalscript_VV_dec,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL1,
                time_interval=time_interval,
                #mosaicking_order=MosaickingOrder.LEAST_CC,
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=caphaitien_bbox,
        size=caphaitien_size,
        config=config,
    )

# create a list of requests
list_of_requests = [get_caphaitien_request(slot) for slot in slots]
list_of_requests = [request.download_list[0] for request in list_of_requests]

# download data with multiple threads
data = SentinelHubDownloadClient(config=config).download(list_of_requests, max_threads=5)

# some stuff for pretty plots
ncols = 3
nrows = 3
aspect_ratio = caphaitien_size[0] / caphaitien_size[1]
subplot_kw = {"xticks": [], "yticks": [], "frame_on": False}

fig, axs = plt.subplots(ncols=ncols, nrows=nrows, figsize=(5 * ncols * aspect_ratio, 5 * nrows), subplot_kw=subplot_kw)

for idx, image in enumerate(data):
    ax = axs[idx // ncols][idx % ncols]
    ax.imshow(np.clip(image * 2.5 / 255, 0, 1))
    ax.set_title(f"{slots[idx][0]}  -  {slots[idx][1]}", fontsize=10)

plt.tight_layout()

for idx, image in enumerate(data):
    ax = axs[idx // ncols][idx % ncols]
    ax.imshow(np.clip(image * 2.5 / 255, 0, 1))
    ax.set_title(f"{slots[idx]}", fontsize=10)
 
plt.suptitle('Flood event in Cap Haïtien', fontweight = 'bold', fontsize = 13, y = 0.98)

data.save_data()

##############################################################################
# SUDEST
##############################################################################


start = datetime.datetime(2021, 8, 6)
end = datetime.datetime(2021, 8, 26)
n_chunks = 20
tdelta = (end - start) / n_chunks
edges = [(start + i * tdelta).date().isoformat() for i in range(n_chunks)]
slots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]

slots = [('2021-08-09', '2021-08-10'),
         ('2021-08-10', '2021-08-11'),
         ('2021-08-16', '2021-08-17'),
         ('2021-08-17', '2021-08-18'),
         ('2021-08-22', '2021-08-23'),
         ('2021-08-23', '2021-08-24')]

def get_sudest_request(time_interval):
    return SentinelHubRequest(
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL1,
                time_interval=time_interval,
                #mosaicking_order=MosaickingOrder.LEAST_CC,
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=sudest_bbox,
        size=sudest_size,
        config=config,
    )

# create a list of requests
list_of_requests = [get_sudest_request(slot) for slot in slots]
list_of_requests = [request.download_list[0] for request in list_of_requests]

# download data with multiple threads
data = SentinelHubDownloadClient(config=config).download(list_of_requests, max_threads=5)

# some stuff for pretty plots
ncols = 4
nrows = 3
aspect_ratio = sudest_size[0] / sudest_size[1]
subplot_kw = {"xticks": [], "yticks": [], "frame_on": False}

fig, axs = plt.subplots(ncols=ncols, nrows=nrows, figsize=(5 * ncols * aspect_ratio, 5 * nrows), subplot_kw=subplot_kw)

for idx, image in enumerate(data):
    ax = axs[idx // ncols][idx % ncols]
    ax.imshow(np.clip(image * 2.5 / 255, 0, 1))
    ax.set_title(f"{slots[idx][0]}  -  {slots[idx][1]}", fontsize=10)

plt.tight_layout()

for idx, image in enumerate(data):
    ax = axs[idx // ncols][idx % ncols]
    ax.imshow(np.clip(image * 2.5 / 255, 0, 1))
    ax.set_title(f"{slots[idx]}", fontsize=10)
 
plt.suptitle('Flood event in Sud-Est Department', fontweight = 'bold', fontsize = 13, y = 0.98)


##############################################################################
# NORD OUEST 
##############################################################################

start = datetime.datetime(2021, 3, 30)
end = datetime.datetime(2021, 4, 16)
n_chunks = 20
tdelta = (end - start) / n_chunks
edges = [(start + i * tdelta).date().isoformat() for i in range(n_chunks)]
slots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]

slots = [('2021-08-09', '2021-08-10'),
         ('2021-08-10', '2021-08-11'),
         ('2021-08-16', '2021-08-17'),
         ('2021-08-17', '2021-08-18'),
         ('2021-08-22', '2021-08-23'),
         ('2021-08-23', '2021-08-24')]

def get_nordouest_request(time_interval):
    return SentinelHubRequest(
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL1,
                time_interval=time_interval,
                #mosaicking_order=MosaickingOrder.LEAST_CC,
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=nordouest_bbox,
        size=nordouest_size,
        config=config,
    )

# create a list of requests
list_of_requests = [get_nordouest_request(slot) for slot in slots]
list_of_requests = [request.download_list[0] for request in list_of_requests]

# download data with multiple threads
data = SentinelHubDownloadClient(config=config).download(list_of_requests, max_threads=5)

# some stuff for pretty plots
ncols = 4
nrows = 3
aspect_ratio = nordouest_size[0] / nordouest_size[1]
subplot_kw = {"xticks": [], "yticks": [], "frame_on": False}

fig, axs = plt.subplots(ncols=ncols, nrows=nrows, figsize=(5 * ncols * aspect_ratio, 5 * nrows), subplot_kw=subplot_kw)

for idx, image in enumerate(data):
    ax = axs[idx // ncols][idx % ncols]
    ax.imshow(np.clip(image * 2.5 / 255, 0, 1))
    ax.set_title(f"{slots[idx][0]}  -  {slots[idx][1]}", fontsize=10)

plt.tight_layout()

for idx, image in enumerate(data):
    ax = axs[idx // ncols][idx % ncols]
    ax.imshow(np.clip(image * 2.5 / 255, 0, 1))
    ax.set_title(f"{slots[idx]}", fontsize=10)
 
plt.suptitle('Flood event in Sud-Est Department', fontweight = 'bold', fontsize = 13, y = 0.98)





