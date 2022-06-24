# This script contains all functions for running the urban_main script

# =============================================================================
# IMPORTS
# =============================================================================

import os 
import json
import pycrs 
import shapely
import numpy as np 
import rasterio as rio 
import geopandas as gpd 
import rioxarray as rxr 
from matplotlib.pyplot import imshow 
from rasterstats import zonal_stats
from rasterio.mask import mask 
from rasterio.features import shapes 
from shapely.geometry import box, mapping, shape 
from fiona.crs import from_epsg
from scipy.ndimage.filters import uniform_filter 
from scipy.ndimage.measurements import variance 

# =============================================================================
# STEP 1: CREATE BOUNDING BOX AROUND URBAN AREA
# =============================================================================

def create_bbox(left, bottom, right, top): # or minx, miny, maxx, maxy
    """ Function that creates bbox based on inserted coordinates """
    city = [left, bottom, right, top]
    city_geom = box(*city)
    city_df = gpd.GeoDataFrame({'id': 1, 'geometry': [city_geom]})
    city_df = city_df.set_crs('epsg:3857')
    return city_df

# =============================================================================
# STEP 2: MASK URBAN RASTER BY BBOX
# =============================================================================

def get_features(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    return [json.loads(gdf.to_json())['features'][0]['geometry']]
# credit: https://automating-gis-processes.github.io/site/notebooks/Raster/clipping-raster.html

def mask_urban(urban_raster, bbox, output_folder, output_file):
    """ Function that masks an urban raster by a defined bbox and 
    saves the output as a new tif file in the output folder of choice"""
    if not os.path.exists(output_folder): os.makedirs(output_folder)
    with rio.open(urban_raster) as src:
        epsg_code = int(src.crs.data['init'][5:]) # save epsg code of urban raster
        bbox = bbox.to_crs(epsg = epsg_code) # make sure bbox has same crs as urban raster
        coordinates = get_features(bbox) # get coordinates how rasterio wants them
        out_image, out_transform = mask(src, coordinates, crop=True) # apply mask
        out_meta = src.meta # save meta data
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform,
                     "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()}) # update meta
    path = os.path.join(output_folder, output_file) # join paths
    with rio.open(path, "w", **out_meta) as dest:
        dest.write(out_image) # write masked urban raster 
    return out_image


# =============================================================================
# STEP 3: CONVERT MASKED RASTER TO POLYGON
# =============================================================================

def raster_to_polygon(output_folder, output_file):
    """ Function that converts the masked urban raster to one polygon """
    path = os.path.join(output_folder, output_file)
    with rio.Env():
        with rio.open(path, 'r') as src:
            image = src.read(1) # first band
            results = ({'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v) in enumerate(shapes(image, mask = None, transform = src.transform)))
    geoms = list(results)
    # credit: https://gis.stackexchange.com/questions/187877/how-to-polygonize-raster-to-shapely-polygons

    poly_urban = gpd.GeoDataFrame.from_features(geoms) # create data frame of polygons
    poly_urban = poly_urban.set_crs(epsg = 3857) # set to original crs, this is NOT 'ESRI:54009' 
    poly_urban = poly_urban.to_crs(epsg = 4326) # convert crs to same as sar raster
    only_urban = poly_urban.loc[poly_urban['raster_val'] >= 3.0] # select only values >= 3 as these are urban settlements
    only_urban['dissolve'] = 1 # assign column with a constant value
    only_urban = only_urban.dissolve(by = 'dissolve') # dissolve to one polygon using the newly assigned column
    return only_urban
    
# =============================================================================
# STEP 4: CLIP POLYGON WITH SAR IMAGES
# =============================================================================

def clip_sar(sar_folder, masked_urban_pol):
    list_of_dates = []
    list_of_means = []
    for tif in os.listdir(sar_folder):
        path = os.path.join(sar_folder, tif) # joint paths
        sar = rxr.open_rasterio(path, masked = True).squeeze()[0] # open sar images
        clip_sar = sar.rio.clip(masked_urban_pol.geometry.apply(mapping)) # clip sar images and urban polygons
        # credit: https://www.earthdatascience.org/courses/use-data-open-source-python/intro-raster-data-python/raster-data-processing/crop-raster-data-with-shapefile-in-python/
        clip_sar = clip_sar[0].values # convert to np array
        means = np.nanmean(clip_sar) # calculate mean, not taking into account Nan 
        list_of_dates.append(tif[:10]) # extract dates
        list_of_means.append(means)
    return list_of_means, list_of_dates

# =============================================================================
# STEP 5: VISUALISATION
# =============================================================================



