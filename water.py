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
from rasterio.warp import calculate_default_transform, reproject, Resampling
import resample
import arcpy
from rasterio.features import shapes
from shapely.geometry import shape


# Open data
## Open water map
water = rs.open("data/occurrence_80W_20Nv1_3_2020.tif")

## Open landuse map
landuse = rs.open("data/2022-02-01_stack.tiff")

# Create a common crs based on the input data
## Give the object crs the crs of the input data
crs = landuse.crs

# Create arrays
## Create water array
water_arr = water.read(1)

## Create landuse array
landuse_arr = landuse.read()

### Maintain only the first layer
landuse_arr = landuse_arr[1]

## Change the dtypte to uint8
### Change the dtypte of the water data
water_arr = water_arr.astype('uint8')

### Change the dtypte of the landuse data
landuse_arr = landuse_arr.astype('uint8')










# Create a bounding box
minx, miny = -72.206603569, 19.7478899750001
maxx, maxy = -72.203443465, 19.7503596370001
bbox = box(minx, miny, maxx, maxy)

# Crop the images to the same extent with the boundingbox
## Create a bounding box to use for cropping
crop = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(4326))

## Reproject to the correct crs: the crs of the landuse data
crop = crop.to_crs(crs=landuse.crs.data)

## Parse features from GeoDataFrame in such a manner that rasterio wants them
### Create a function to do it
def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

#### Get the geometry coordinates by using the function "getFeatures"
coords = getFeatures(crop)
print(coords)

## Crop the datasets to the extent of the object "crop"
### Crop the landuse data
landuse_arr_crp, out_transform = mask(landuse, coords, crop=True)

### Crop the water data
water_arr_crp, out_transform = mask(water, coords, crop=True)
            



## Save only the first layer of the data
### Plot the landuse map
landuse_arr_crp = landuse_arr_crp[0]

### Plot the water map
water_arr_crp = water_arr_crp[0]



# For the water bodies, you only want the map to indicate where is water and
# where is not, therefore only 1 and 0 will be visible on map. The following
# function is used for that
def create_mask (water_data): 
    for i in range(0,len(water_data)):
        for j in range(0, len(water_data)):
            if water_data[i][j] < 1:
                water_data[i][j] = 0
            else:
                water_data[i][j] = 1
    return(water_data)

water_arr_crp_bl= create_mask(water_arr_crp)

plt.imshow(water_arr_crp_bl)






mask = None
with rasterio.Env():
    with rs.open('./data/water_bodies.tif') as src:
        image = src.read(1) # first band
        results = (
        {'properties': {'raster_val': v}, 'geometry': s}
        for i, (s, v) 
        in enumerate(
            shapes(image, mask=mask, transform=src.transform)))

geoms = list(results)

print(shape(geoms[1]['geometry'])

# Call the coordinates from water bodies
water_bodies_1 = geoms[1]['geometry']['coordinates']





# Save the data as tif
## Create a function to save data
# Create and save as raster file again
def save_raster(file_path, array, raster,crs):
    with rs.open(file_path, 
                           'w',
                    driver='GTiff',
                    height=array.shape[0],
                    width=array.shape[1],
                    count=1,
                    dtype=array.dtype,
                    crs=crs,
                    nodata=None, # change if data has nodata value
                    transform=raster.transform) as dst:
        dst.write(array, 1)
        
save_raster('./data/water_bodies.tif', water_arr_crp_bl, water, crs)


test = rs.open('./data/water_bodies.tif')




test <- resample(water_arr_crp_bl, landuse_arr_crp, method="ngb")


### Crop the water data
test, out_transform = mask(test, water_arr_crp_bl, crop=True)













np.where(water_arr<1, water_arr, landuse_arr)


water_arr_crp




# Create metadata about the file to save it
metadata = water.profile

metadata.update(
        dtype=rs.uint16,
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

test_arr = create_mask(test_arr)
            
# Plot the result
plt.imshow(test_arr)








    







# https://automating-gis-processes.github.io/CSC18/lessons/L6/clipping-raster.html

# Insert the bounding box into the dataframe
landuse_df = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(4326))

# Reproject to the correct crs
landuse_df = landuse_df.to_crs(crs=landuse.crs.data)

# Parse features from GeoDataFrame in such a manner that rasterio wants them
def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

# Get the geometry coordinates by using the function
coords = getFeatures(test_gdf)
print(coords)

out_img, out_transform = mask(landuse, coords, crop=True)


np.where(test_arr<1, test_arr, landuse_arr)













# Create metadata about the file to save it
metadata = water.profile

metadata.update(
        dtype=rs.uint16,
        count=1,
        compress='lzw')

# Set the land values to None
metadata['nodata'] = None






# Create and save as raster file again
def save_raster(file_path, array, raster,crs):
    with rs.open(file_path, 
                           'w',
                    driver='GTiff',
                    height=array.shape[0],
                    width=array.shape[1],
                    count=1,
                    dtype=array.dtype,
                    crs=crs,
                    nodata=None, # change if data has nodata value
                    transform=raster.transform) as dst:
        dst.write(array, 1)
        
save_raster('./data/landuse_2.tif', landuse_arr_crp[0], landuse, crs)



landuse_2 = rs.open(r'data/landuse_2.tif')

landuse_2
        


# Resample and save the data
## Resample and save the landuse data
with rs.open('./data/2022-02-01_stack.tiff') as src:
    transform, width, height = calculate_default_transform(src.crs, crs, 
                                                           src.width, 
                                                           src.height, 
                                                           *src.bounds)
    kwargs = src.meta.copy()
    kwargs.update({'crs': crs,'transform': transform, 'width': width,'height': height})
    
    with rasterio.open('./data/landuse_res.tif', 'w', **kwargs) as dst:
            reproject(source=rasterio.band(src, 1),destination=rasterio.band(dst, 1),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=crs,
                resampling=Resampling.nearest)

# Open the resampled data
## Open the resampled water data
water = rs.open(r'./data/water_data.tif')

## Open the resampled landuse data
landuse = rs.open(r'./data/landuse_res.tif')







        

