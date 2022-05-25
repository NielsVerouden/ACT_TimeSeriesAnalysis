############################################################################## 
# IMPORTING AND CONFIGURATION
##############################################################################

from sentinelhub import SHConfig
import os, pyproj, gdal, rasterio.plot
import rasterio as rs
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta, date
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
)

config = SHConfig()
config.instance_id = '1fc73689-68c6-4f09-aba0-fa6d7c80aee9'
config.sh_client_id = 'feafa876-6d36-46e9-8f06-6125aaf70157'
config.sh_client_secret = '3+.y(0GObjs}HG0zhvi<~MMG#|NP?!9AT&U&M9+c'
config.save()


##############################################################################
# EVALSCRIPTS
##############################################################################
# Part of this code is from https://apps.sentinel-hub.com/eo-browser
# An evalscipt is a piece of Javascript code which defines how the satellite data
# shall be processed by Sentinel Hub and what values the service shall return.
# Source: https://docs.sentinel-hub.com/api/latest/evalscript/

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

##############################################################################
# DEFINE PARAMETERS
##############################################################################

start = '2022-05-01'
end = '2022-05-20'
lon = 19.749997
lat = -72.1999992
zoom_level = 0.1


##############################################################################
# REQUEST TIME SERIES
##############################################################################

# DEFINE FUNCTIONS
def boundingBox(lon, lat, zoom_level):
    
    resolution = zoom_level * 50
    
    min_x = lon - (0.5 * zoom_level)
    min_y = lat - (0.5 * zoom_level)
    max_x = lon + (0.5 * zoom_level)
    max_y = lat + (0.5 * zoom_level)
    coordinates = [min_y,min_x,max_y,max_x]
    
    boundBox = BBox(bbox = coordinates, crs = CRS.WGS84)
    BB_size = bbox_to_dimensions(boundBox, resolution = resolution)
    
    return (boundBox, BB_size)

def get_request(time_interval):
    return SentinelHubRequest(
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL1,
                time_interval=time_interval,
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=boundBox,
        size=BB_size,
        config=config,
    )


# DEFINE BOUNDINGBOX OF COORDINATE
boundBox = boundingBox(lon, lat, zoom_level)[0]
BB_size = boundingBox(lon, lat, zoom_level)[1]


# DEFINE TOTAL NR. DAYS BETWEEN START AND END
start = date(int(start[0:4]), int(start[5:7]), int(start[8:10]))
end = date(int(end[0:4]), int(end[5:7]), int(end[8:10])) + timedelta(days=1)
nr_days = (end - start).days
tdelta = (end - start) / nr_days
edges = [(start + i * tdelta).isoformat() for i in range(nr_days)]
slots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]


# CREATE LIST OF REQUESTS
list_of_requests = [get_request(slot) for slot in slots]
lijst = [i.download_list[0] for i in list_of_requests]


# DOWNLOAD DATA FROM MULTIPLE REQUESTS
data = SentinelHubDownloadClient(config=config).download(lijst, max_threads=1)


# REMOVE DATES WITHOUT DATA
data_new = []
for i in data:
    if sum(i[0]) != 0:
        data_new.append(i)


##############################################################################
# VISUALISATION
##############################################################################



# some stuff for pretty plots
ncols = 3
nrows = 3
aspect_ratio = BB_size[0] / BB_size[1]
subplot_kw = {"xticks": [], "yticks": [], "frame_on": False}

fig, axs = plt.subplots(ncols=ncols, nrows=nrows, figsize=(5 * ncols * aspect_ratio, 5 * nrows), subplot_kw=subplot_kw)

for idx, image in enumerate(data_new):
    ax = axs[idx // ncols][idx % ncols]
    ax.imshow(np.clip(image * 2.5 / 255, 0, 1))
    ax.set_title(f"{slots[idx][0]}  -  {slots[idx][1]}", fontsize=10)

plt.tight_layout()

for idx, image in enumerate(data_new):
    ax = axs[idx // ncols][idx % ncols]
    ax.imshow(np.clip(image * 2.5 / 255, 0, 1))
    ax.set_title(f"{slots[idx]}", fontsize=10)
 
plt.suptitle('Flood event in Cap Haïtien', fontweight = 'bold', fontsize = 13, y = 0.98)

