# import rasterio
# from rasterio.plot import show
# from rasterio.plot import show_hist
# from rasterio.mask import mask
# from shapely.geometry import box
# import geopandas as gpd
# import matplotlib.pyplot as plt
# import numpy as np
# from fiona.crs import from_epsg
# import pycrs

# urban_areas = "data/built_polygon/urban_areas_polygon.shp"
# path_SAR = "data/SAR/2022-01-27_vv_vh_vvvhratio_Stack.tiff"

# data = rasterio.open(path_SAR)

# # WGS84 coordinates
# bbox = box(-72.212621,19.725209,-72.183866,19.753162)
# geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(4326))
# geo = geo.to_crs(crs=data.crs.data)

# # Convert coordinates of the geometry in such a format that rasterio wants them
# def getFeatures(gdf):
#     """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
#     import json
#     return [json.loads(gdf.to_json())['features'][0]['geometry']]

# coords = getFeatures(geo)

# # Clip the raster with the polygon using the coords variable
# out_img, out_transform = mask(data, shapes=coords, crop=True)
# # plt.imshow(out_img[1])

# out_meta = data.meta.copy()
# epsg_code = int(data.crs.data['init'][5:])

# out_meta.update({"driver": "GTiff",
#                   "height": out_img.shape[1],
#                   "width": out_img.shape[2],
#                   "transform": out_transform,
#                   "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()}
#                 )

# with rasterio.open('data/urban_clipped.tif', "w", **out_meta) as dest:
#     dest.write(out_img)

# clipped = rasterio.open('data/urban_clipped.tif')
# show((clipped, 1), cmap='terrain')


# =============================================================================
# =============================================================================
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from shapely.geometry import mapping
import rioxarray as rxr
import geopandas as gpd
import rasterio as rio

import os
from os import listdir
from os.path import isfile, join

mypath = "data/SAR/"
urban_areas = "data/cap_haitien_polygons/urban_areas_polygon.shp"
mean_values = []

file_names = [file for file in listdir(mypath) if isfile(join(mypath, file))]

for file in file_names:
    path_SAR = os.path.join(mypath, file)
    ## Open the big raster and save metadata for later
    raster = rio.open(path_SAR)
    raster_meta = raster.meta.copy()
    epsg_code = int(raster.crs.data['init'][5:])
    raster = raster.read(1)

    ## Import urban polygons and change CRS system
    urban_poly = gpd.read_file(urban_areas)
    urban_poly = urban_poly.to_crs(epsg=epsg_code)

    ## Open raster again but now as rioxarray (rxr)
    SAR_im = rxr.open_rasterio(path_SAR, masked=True).squeeze()

    # Clip radar data to urban areas
    SAR_clipped = SAR_im.rio.clip(urban_poly.geometry.apply(mapping))

    # Plot the clipped SAR data
    f, ax = plt.subplots(figsize=(10, 10))
    ax.set(title="SAR imagery - Cap-Haitiën")
    ax.set_axis_off()
    plt.imshow(SAR_clipped[0])
    plt.show()

    
    # Calculate statistics
    mean_values.append(int(SAR_clipped.mean()))

print(f"\nMean values of the urban areas are: \n{mean_values}")


# # Visualise raster
# f, ax = plt.subplots(figsize=(10, 10))
# ax.set(title="SAR imagery - Cap-Haitiën")
# ax.set_axis_off()
# plt.imshow(SAR_im[0])
# plt.show()
