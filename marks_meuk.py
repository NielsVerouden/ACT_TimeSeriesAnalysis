# -*- coding: utf-8 -*-
"""
Created on Wed May 25 11:52:31 2022

@author: markb
"""

import rasterio as rs
from rasterio.plot import show
from rasterio import mask
import numpy as np
from osgeo import gdal, ogr
import matplotlib.pyplot as plt
import os
import seaborn as sns
import geopandas as gpd

# open the two rasters 
dataset = rs.open("./downloads/W080N20_PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326.tif", driver="GTiff")
map1 = dataset.read()





