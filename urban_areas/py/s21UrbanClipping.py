# This script contains all functions for running the main script for urban
# =============================================================================
# IMPORTS
# =============================================================================
import os, json,pycrs
import numpy as np 
import rasterio as rio
import pandas as pd
import geopandas as gpd 
import rioxarray as rxr 
import geopandas
import matplotlib.pyplot as plt
from rasterio.mask import mask
from rasterio import plot
from rasterio.features import shapes 
from shapely.geometry import box, mapping 
# =============================================================================
# STEP 1: CREATE BOUNDING BOX AROUND URBAN AREA
# =============================================================================

def createBbox(coordinates, SAR_path, show_bbox='n'):
    """ 
    Function that creates bbox based on inserted coordinates
    """
    minx, miny, maxx, maxy = coordinates
    
    # Create geometry of coordinates
    geom = box(*[minx, miny, maxx, maxy])
    
    # Create GeoDataFrame based on geometry
    gdf = gpd.GeoDataFrame({'id': 1, 'geometry': [geom]})
    
    # Assign correct coordinate system (only needed when coordinates are in different crs)
    gdf = gdf.set_crs('epsg:4326')
    gdf = gdf.to_crs('epsg:4326')
    
    if show_bbox == 'y':
        # Open first SAR file as rasterio object
        path = os.path.join('data', SAR_path)
        file = os.listdir(path)[0]
        raster = rio.open(os.path.join(path, file))
        
        # Plot them
        fig, ax = plt.subplots(figsize=(5, 15))
        rio.plot.show(raster, ax=ax)
        gdf.plot(ax=ax, facecolor='none', edgecolor='blue')

    return gdf

# =============================================================================
# STEP 2: MASK URBAN RASTER BY BBOX
# =============================================================================

def get_features(gdf):
    """
    Function to parse features from GeoDataFrame in such a manner that rasterio 
    can use the features.
    """
    ## Create json file from GeoDataFrame
    # credit: https://automating-gis-processes.github.io/site/notebooks/Raster/clipping-raster.html
    json_load = [json.loads(gdf.to_json())['features'][0]['geometry']]
    
    return json_load

def maskUrban(urban_raster, bbox):
    """ 
    Function that masks an urban raster by a defined bbox and saves the output 
    as a new temporary tif file which is automatically removed during the next
    step. 
    """
    ## Create path to temporarily store masked urban raster
    temp_path_masked = os.path.join('data', 'temp_urban_masked.tif')
    
    # Create path to open large urban raster file (.tif)
    urban_path = os.path.join('data', urban_raster)
    
    ## Open urban raster for masking with bounding box
    with rio.open(urban_path) as src:
        # Save epsg code of urban raster
        epsg_code = int(src.crs.data['init'][5:])
        
        # Assign epsg of raster to bbox
        bbox = bbox.to_crs(epsg = epsg_code)
        
        # Convert features of bbox
        coordinates = get_features(bbox)
        
        ## Apply mask to raster and features
        out_image, out_transform = mask(src, coordinates, crop=True)
        
        # Save meta data of raster and update it with new info
        out_meta = src.meta
        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform,
                         "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()}) # update meta
        
    ## Write masked tif file to data folder
    with rio.open(temp_path_masked, "w", **out_meta,) as dest:
        dest.write(out_image)
       
    return temp_path_masked


# =============================================================================
# STEP 3: CONVERT MASKED RASTER TO POLYGON
# =============================================================================

def rasterToPolygon(temp_path_masked, SAR_path, urban_grade=3):
    """ 
    Function that converts the masked urban raster to one polygon
    """
    ## Check if urban grade is between 3 and 6, and if not, raise TypeError
    if urban_grade <= 2 or urban_grade > 6:
        raise TypeError("Variable 'urban_grade'; Choose value between 3 and 6!")
    
    ## Get epsg code from SAR data
    path = os.path.join('data', SAR_path)
    file = os.listdir(path)[0]

    # Open first SAR file as rasterio object
    raster = rio.open(os.path.join(path, file))
    
    # Assign CRS of SAR image to variable
    epsg_code = int(raster.crs.data['init'][5:])
    
    ## Open temp urban mask and convert to geometry object
    # credit: https://gis.stackexchange.com/questions/187877/how-to-polygonize-raster-to-shapely-polygons
    with rio.Env():
        with rio.open(temp_path_masked, 'r') as src:
            image = src.read() # first band
            src.crs
            results = ({'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v) in enumerate(shapes(image, mask = None, transform = src.transform)))
            geoms = list(results)

    ## Create geopandas dataframe of geometry
    gpd_polygon = gpd.GeoDataFrame.from_features(geoms)

    # Set to original CRS ('epsg:3857') and convert to new CRS of SAR data
    gpd_polygon = gpd_polygon.set_crs(epsg = 3857)
    gpd_polygon = gpd_polygon.to_crs(epsg = epsg_code)

    ## Select only values based on urban_grade
    gpd_urban = gpd_polygon.loc[gpd_polygon['raster_val'] >= urban_grade].copy()
    
    # Assign column with a constant value
    gpd_urban['dissolve'] = 1
    
    # Dissolve to one polygon using the newly assigned column
    gpd_urban = gpd_urban.dissolve(by = 'dissolve')
    
    ## Remove temporary urban masked tif file    
    if os.path.exists(temp_path_masked):
        os.remove(temp_path_masked)
    
    return gpd_urban

# =============================================================================
# STEP 4: CLIP POLYGON WITH SAR IMAGES
# =============================================================================

def clipSAR(SAR_path, urban_polygon_masked):
    """
    Function to clip the SAR data based on the polygon of the urban data. A list 
    of dates and means are returned. 
    """
    # Create empty lists where dates and means of SAR are stored
    list_of_dates = []
    list_of_means = []
    
    # Create path to load SAR data
    SAR_path = os.path.join('data', SAR_path)
    
    for tif in os.listdir(SAR_path):
        # Create path to load each file in sar_path
        file_path = os.path.join(SAR_path, tif)
        
        # Open SAR file with rioxarray and keep only first band (which is VV)
        SAR = rxr.open_rasterio(file_path, masked = True).squeeze()[0]
        
        # Clip the SAR image with the urban polygon
        # credit: https://www.earthdatascience.org/courses/use-data-open-source-python/intro-raster-data-python/raster-data-processing/crop-raster-data-with-shapefile-in-python/
        SAR_clipped = SAR.rio.clip(urban_polygon_masked.geometry.apply(mapping))
        
        # Calculate the means of each clipped SAR image
        means = float(np.mean(SAR_clipped))
        
        # Append the date and mean of each SAR image to the corresponding lists
        list_of_dates.append(tif[:10])
        list_of_means.append(means)
    
        # # Plot clipped SAR images
        # fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 15))
        # ax.imshow(SAR_clipped) 
    
    return list_of_means, list_of_dates

# =============================================================================
# STEP 5: EXPORT AS CSV
# =============================================================================

def exportToCSV(mean_values, dates, SAR_path):
    """
    Function to export the mean SAR values and the corresponding dates as a CSV
    file to the output folder.
    """
    # Create output folder if it does not exist yet
    if not os.path.exists(os.path.join('urban_areas', 'output')):
        os.makedirs(os.path.join('urban_areas', 'output'))
    
    # Create dataframe of mean VV values per date
    df_vv = pd.DataFrame({'mean_VV':mean_values, 'date':dates})

    # Create name for csv file based on dates, and write dataframe to csv file
    csv_name = f'meanVV_{SAR_path}_{dates[0]}_{dates[-1]}.csv'
    csv_path = os.path.join('urban_areas', 'output', csv_name)
    
    df_vv.to_csv(csv_path, encoding='utf-8', index=False)
    return df_vv
