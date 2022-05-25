# -*- coding: utf-8 -*-
"""
Created on Wed May 25 11:52:31 2022

@author: markb
"""

import rasterio as rs   
import numpy as np
from osgeo import gdal, ogr

# Open dataset
dataset = gdal.Open(r'C:\Users\markb\Downloads\W080N20_PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326')


print(dataset.RasterCount)