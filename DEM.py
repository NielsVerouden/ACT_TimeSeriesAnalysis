# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 15:03:32 2022

@author: julia
"""
import elevation
import os


# downloading DEM and cropping it to the right extent

"""
caphaitien_coords = [-72.273903,19.671135,-72.159233,19.798714]
resolution = 10
caphaitien_bbox = BBox(bbox = caphaitien_coords, crs = CRS.WGS84)
caphaitien_size = bbox_to_dimensions(caphaitien_bbox, resolution = resolution)
"""

west, south, east, north = bounds = -72.273903, 19.671135, -72.159233, 19.798714


output = 'C:/Users/julia/Documents/WUR/ACT/DEM/Haiti.tif'

elevation.clip(bounds=bounds, output=output)
