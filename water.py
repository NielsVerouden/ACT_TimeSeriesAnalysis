# Import packages
import rasterio as rs
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import fiona
import rasterio
import rasterio.mask
from rasterio.mask import mask
import gdal

# Open dataset
test = rs.open(r'data/really_small_area/really_small.tif')

whole = rs.open(r'data/occurrence_80W_20Nv1_3_2020.tif')

# PLot data
plt.imshow(test.read(1), cmap='pink')

# Create an array
test_arr = test.read(1)

# PLot the water data
plt.imshow(test_arr)


# Create metadata about the file to save it
metadata = test.profile


metadata.update(
        dtype=rs.uint8,
        count=1,
        compress='lzw')

# Set the land values to None
metadata['nodata'] = None

# Create only 0 and 1 values
def create_mask (water_data): 
    for i in range(0,len(water_data)):
        for j in range(0, len(water_data)):
            if water_data[i][j] < 1:
                water_data[i][j] = 0
            else:
                water_data[i][j] = 1
    return(water_data)

create_mask(test_arr)
            
# Plot the result
plt.imshow(test_arr)

# Set crs
crs=test.crs

# Create and save as raster file again
def save_raster(file_path, array,crs):
    with rs.open(file_path, 
                           'w',
                    driver='GTiff',
                    height=test_arr.shape[0],
                    width=test_arr.shape[1],
                    count=1,
                    dtype=test_arr.dtype,
                    crs=test.crs,
                    nodata=None, # change if data has nodata value
                    transform=test.transform) as dst:
        dst.write(test_arr, 1)
    

# Open landuse map
landuse = rs.open("data/2022-02-01_stack.tiff", driver="GTiff")
landuse_arr = landuse.read()

# Maintain only the first layer
landuse_arr = landuse_arr[0]
    
# Plot the landuse map
plt.imshow(landuse_arr)

with rasterio.open('data/really_small_area/really_small.tif') as dataset:
    mask = test.dataset_mask()
    
    for geom, val in rasterio.features.shapes(
        mask, transform=dataset.transform):
        # Transform shapes from the dataset's own coordinate
        # reference system to CRS84 (EPSG:4326).
        geom = rasterio.warp.transform_geom(
            dataset.crs, 'EPSG:4326', geom, precision=6)

      # Print GeoJSON shapes to stdout.
    shapes = geom

# Crop DEM
bbox = (-72.273903,19.671135,-72.159233,19.798714)
input_file = "data/2022-02-01_stack.tiff"
output_file = "./data/landuse_crop.tif"

ds = gdal.Open(input_file)
landuse_crop = gdal.Warp(output_file, ds, options=gdal.WarpOptions(
    options=['outputBounds'], outputBounds=small_crop))

img = rasterio.open(output_file)
plt.show(img)




out_image, out_transform = mask(landuse_arr, shapes, crop=True)



caphaitien_coords = [-72.273903,19.671135,-72.159233,19.798714]

small_crop = [-72.206603569, -72.203443465, 19.7478899750001, 19.7503596370001]
