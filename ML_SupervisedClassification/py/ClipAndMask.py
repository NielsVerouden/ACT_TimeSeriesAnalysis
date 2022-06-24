import rasterio as rio
import numpy as np
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
from pycrs.parse import from_epsg_code
from skimage.transform import resize
import os
import json
import glob


def clipRaster(bounding_rasters_folder, raster_to_be_clipped_name, output_folder, output_name):
    """
    Parameters
    ----------
    bounding_rasters_folder: str: folder containing the mask rasters (small rasters)
    raster_to_be_clipped_name: str: filepath to the raster that needs to be clipped
    output_folder: str: folder where the clips will be located
    output_name: str: suffix of output file names
    -------
    Creates clips of the raster_to_be_clipped for each file in bounding_rasters_folder.
    Make sure that all files overlap with the file from raster_to_be_clipped_name
    -------
    """
    if not os.path.exists(output_folder): os.makedirs(output_folder)

    #for bounding_raster_name in bounding_raster_names:
    for bounding_raster_name in os.listdir(bounding_rasters_folder):
        
        ## Open the big raster and save metadata for later
        raster = rio.open(raster_to_be_clipped_name)
        raster_meta = raster.meta.copy()
        epsg_code = int(raster.crs.data['init'][5:])
    
        ## Open small raster
        bounding_raster_path=os.path.join(bounding_rasters_folder,bounding_raster_name)
        boundingraster = rio.open(bounding_raster_path)
        
        #Crop the raster to the sentinel image:
        #No need for reprojection since both have the same coordinate system
        #1. Get the bounding box of the sentinel-1 image:
        bounds=boundingraster.bounds    
        geom = box(*bounds)
        
        #2. Get a GeoDataFrame of the bounds:
        geodf = gpd.GeoDataFrame({"id":1,"geometry":[geom]})
        
        ## Parse features from GeoDataFrame in such a manner that rasterio wants them
        ### Create a function to do it
        def getFeatures(gdf):
            #Function to parse features from GeoDataFrame in such a manner that rasterio wants them
            return [json.loads(gdf.to_json())['features'][0]['geometry']]
        
        coords = getFeatures(geodf)
        
        #Mask the raster using the bounding box of the smaller raster
        out_img, out_transform = mask(raster, shapes=coords, crop=True)
        
        #Get ready to save the numpy array as a geotiff: update metadata
        raster_meta.update({"driver": "GTiff", "height": out_img.shape[1],
                           "width": out_img.shape[2], "transform": out_transform,
                          "crs": from_epsg_code(epsg_code).to_proj4()})
        
        # Save file in correct path
        compl_output_name="%s_%s.tiff"%(output_name,bounding_raster_name[0:10])
        output_path=os.path.join(output_folder,compl_output_name)
        with rio.open(output_path, "w", **raster_meta) as dest:
            dest.write(out_img)
        
        raster.close()
        boundingraster.close()
    return 


def maskWater(predictions_folder,waterbodies_folder, dest_folder,mask_value=100):
    """
    Parameters
    ----------
    predictions_folder: str: folder containing the predictions of flooded pixels
    waterbodies_folder: str: folder containing the images of clipped water bodies
    dest_folder: str: folder where the masked predictions will be located 
    mask_value (opt): int: value of the mask
    -------
    Masks permanent water bodies from each image in predictions_folder and
    saves the results in dest_folder.
    -------
    """
    if not os.path.exists(dest_folder): os.makedirs(dest_folder)
    
    for prediction_raster in os.listdir(predictions_folder):
        prediction_path = os.path.join(predictions_folder, prediction_raster)
        
        #The data is in the last characters of the filename (before .tiff)
        date = prediction_raster[-15:-5]
        #Look for the file in the water bodies  folder
        #that corresponds to the date of the prediction
        pattern = os.path.join(waterbodies_folder, "WaterBodiesCrop_%s.tiff" %date)
        for file in glob.glob(pattern):
            water_name= file
        
        with rio.open(water_name) as dst:
            water_data=dst.read()
            #water_meta = dst.meta
            
        with rio.open(prediction_path) as dst:
            raster =  dst.read()
            raster_meta=dst.meta
            
        # For the water bodies, you only want the map to indicate where is water and
        # where is not, therefore only 1 and 0 will be visible on map. The following
        # function is used for that. All pixels > 1 are converted to 1 (water)
        def create_mask (array): 
            #create a binary raster of the first band of array
            array[0][array[0]>0]=1
            return(array)
        
        water_binary= create_mask(water_data)
        
        #Resample low res water dataset to the same resolution as the sentinel array
        band = water_binary[0] #band with values 0 and 1
        #Resize function from scikit image
        band_resized = resize(band, (raster.shape[1], raster.shape[2]), anti_aliasing=True)
        #Due to default interpolation: again assing binary values
        band_resized[band_resized>0]=1
        #Add extra dimension (->1 by x by y)
        water_binary_resized = np.expand_dims(band_resized, 0)
        water_binary_resized = water_binary_resized.astype(int)
        
        #Give all pixels in the raster image a specified value if there is water
        #for-loop over each band
        for i in range(0,raster.shape[0]):
            raster[i][water_binary_resized[0]==1]=mask_value
        
        # Save the rasters as tif
        output_name="MaskedPrediction_%s.tiff"%date
        outputpath = os.path.join(dest_folder,output_name)
        print(outputpath)
        with rio.open(outputpath, 'w', **raster_meta) as dst:
            dst.write(raster.astype(rio.float32))
    return 