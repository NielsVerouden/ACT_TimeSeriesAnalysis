# Import packages
import rasterio as rs
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from fiona.crs import from_epsg
import rasterio
from rasterio.mask import mask
from rasterio.mask import mask
import gdal
from rasterio.plot import show
from shapely.geometry import mapping
import json
from shapely.geometry import box
import geopandas as gpd

# Open dataset
test = rs.open(r'data/really_small_area/really_small.tif')

# PLot data
plt.imshow(test.read(1), cmap='pink')

# Create an array
test_arr = test.read(1)

# PLot the water data array
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

masked = create_mask(test_arr)
            
# Plot the result
plt.imshow(test_arr)









    

# Open landuse map
landuse = rs.open("data/2022-02-01_stack.tiff")

# Create landuse array
landuse_arr = landuse.read()

# Maintain only the first layer
landuse_arr = landuse_arr[1]
    
# Plot the landuse map
show(landuse_arr)




# https://automating-gis-processes.github.io/CSC18/lessons/L6/clipping-raster.html

# Create bounding box
minx, miny = -72.206603569, 19.7478899750001
maxx, maxy = -72.203443465, 19.7503596370001
bbox = box(minx, miny, maxx, maxy)

# Insert the bounding box into the dataframe
landuse_df = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(4326))

# Reproject to the correct crs
landuse_df = landuse_df.to_crs(crs=landuse.crs.data)

# Parse features from GeoDataFrame in such a manner that rasterio wants them
def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


# Get the geometry coordinates by using the function
coords = getFeatures(landuse_df)
print(coords)

out_img, out_transform = mask(landuse, coords, crop=True)





# Mask the water bodies
with rs.open("./data/2022-02-01_stack.tiff") as landuse:
    out_image, out_transform = mask(landuse, test_arr, crop=True)










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
    
df = pd.DataFrame(shapes)

geoms = df.coordinates
    
small_crop = [-72.206603569, -72.203443465, 19.7478899750001, 19.7503596370001]



caphaitien_coords = [-72.273903,19.671135,-72.159233,19.798714]

small_crop = [-72.206603569, -72.203443465, 19.7478899750001, 19.7503596370001]


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
