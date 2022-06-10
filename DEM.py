# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 15:03:32 2022

@author: julia
"""
import rasterio
from rasterio.plot import show
from osgeo import gdal
import os

# downloading DEM and cropping it to the right extent

"""
caphaitien_coords = [-72.273903,19.671135,-72.159233,19.798714]
resolution = 10
caphaitien_bbox = BBox(bbox = caphaitien_coords, crs = CRS.WGS84)
caphaitien_size = bbox_to_dimensions(caphaitien_bbox, resolution = resolution)
"""

# os.chdir('C:/Users/julia/Documents/WUR/ACT/') 


# load DEM from files
# fp = r'C:/Users/julia/Documents/WUR/ACT/DEM/Haiti2.tif'
# img = rasterio.open(fp)
# show(img)

# bbox = (-72.273903,19.671135,-72.159233,19.798714)

# gdal.Translate('DEM/Haiti_cropped.tif', fp, projWin=bbox)


# Crop DEM
bbox = (-72.273903,19.671135,-72.159233,19.798714)
input_file = "./Data/Haiti2.tif"
output_file = "./Output/DEM_crop.tif"

ds = gdal.Open(input_file)
DEM_crop = gdal.Warp(output_file, ds, options=gdal.WarpOptions(
    options=['outputBounds'], outputBounds=bbox))

img = rasterio.open(output_file)
show(img)

