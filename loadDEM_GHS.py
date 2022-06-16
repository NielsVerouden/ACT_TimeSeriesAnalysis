### Add DEM and GHS to the raster stacks
import os
from zipfile import ZipFile
import glob
import rasterio as rio
from ClipAndMask import clipRaster
from skimage.transform import resize
import numpy as np

def addDEM_GHS(sentinel_folder, output_folder, GHSfolder, DEMfolder=None):
    #Unzip global human settlement data
    extension=".zip"
    for item in os.listdir(GHSfolder): # loop through items in dir
        if item.endswith(extension): # check for ".zip" extension
            path=os.path.join(GHSfolder,item)
            # Create a ZipFile Object and load sample.zip in it
            with ZipFile(path, 'r') as zipObj:
               # Get a list of all archived file names from the zip
               listOfFileNames = zipObj.namelist()
               # Iterate over the file names
               for fileName in listOfFileNames:
                   # Check filename endswith csv
                   if fileName.endswith('.tif'):
                       #path=os.path.join(GHSfolder,fileName)
                       # Extract a single file from zip
                       zipObj.extract(fileName,GHSfolder)
                       ghs_path=os.path.join(GHSfolder,fileName)
                       
    #Load the GHS and crop to extent of images in the sentinel folder
    ghs_combis = clipRaster(sentinel_folder, ghs_path, GHSfolder, "GHS_Clipped") 
    
    #Resample to same resolution and stack as fourth band
    for date, ghs in ghs_combis.items(): 
        
        pattern = "%s\\*%s*.tiff" % (sentinel_folder,date)
        for file in glob.glob(pattern):
            raster_name= file
            
        with rio.open(raster_name) as dst:
            raster=dst.read()
        
        with rio.open(ghs) as dst:
            ghs_data=dst.read()
            meta=dst.meta.copy()
            
        ghs_band=ghs_data[0]
        ghs_band_resized = resize(ghs_band, (raster.shape[1], raster.shape[2]), anti_aliasing=True)      
        ghs_band_resized = np.expand_dims(ghs_band_resized, 0)
        
        with rio.open(raster_name, "w") as dst:
            meta=dst.meta
            meta.update(count=4)
            dst.write_band(4,ghs_band_resized)
            
    return        


tst = addDEM_GHS("SentinelTimeSeriesStacked", 
           "SentinelTimeSeriesStacked_Incl_DEM_GHS",
           "GLobalHumanSettlement")