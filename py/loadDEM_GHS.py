### Add DEM and GHS to the raster stacks
import os
from zipfile import ZipFile
import glob
import rasterio as rio
from py.ClipAndMask import clipRaster
from skimage.transform import resize
import numpy as np

def addDEM_GHS(sentinel_folder, output_folder, GHSfolder, DEMfolder):
    if not os.path.exists(output_folder): os.makedirs(output_folder)
    #sentinel_folder should already contain stacks of vv, vh and vv/vh ratio
    #the function will add GHS population data and a DEM to the stack
    
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
                   # Check filename endswith tif
                   if fileName.endswith('.tif'):
                       # Extract a single file from zip
                       zipObj.extract(fileName,GHSfolder)
                       ghs_path=os.path.join(GHSfolder,fileName)
    #Load the DEM data
    dem_filename=os.listdir(DEMfolder)[0]
    dem_path = os.path.join(DEMfolder, dem_filename)            
      
    #Load the GHS and crop to extent of images in the sentinel folder
    ghs_combis = clipRaster(sentinel_folder, ghs_path, GHSfolder, "GHS_Clipped") 
    dem_combis = clipRaster(sentinel_folder, dem_path, DEMfolder, "DEM_Clipped") 

    #Resample to same resolution and stack on the Sentinel rasters
    for date, ghs in ghs_combis.items(): 
        dem = dem_combis[date]
        
        pattern = "%s\\*%s*.tiff" % (sentinel_folder,date)
        for file in glob.glob(pattern):
            raster_name= file
            
        #Open Sentinel image of the specified date:
        #Also copy metadata for later use
        with rio.open(raster_name) as dst:
            raster=dst.read()
            meta=dst.meta.copy()
        
        #Open ghs data:
        with rio.open(ghs) as dst:
            ghs_data=dst.read(1).astype('float32')
            ghs_data /= np.amax(ghs_data)

        ghs_data_resized = resize(ghs_data, (raster.shape[1], raster.shape[2]), anti_aliasing=True)          
        
        #Open DEM data:
        with rio.open(dem) as dst:
            dem_data=dst.read(1).astype('float32')
            dem_data /= np.amax(dem_data)
               
        dem_data_resized = resize(dem_data, (raster.shape[1], raster.shape[2]), anti_aliasing=True)          

        with rio.open(raster_name, "r") as dst:
            vv=dst.read(1)
            vh=dst.read(2)
            ratio=dst.read(3)
            
         #Rescale values to common range (eases training a model)   
        #dem_band_rescaled = np.interp(dem_band_resized, (dem_band_resized.min(), dem_band_resized.max()), (np.amin(vv), np.amax(vv)))
        #ghs_band_rescaled= np.interp(ghs_band_resized, (ghs_band_resized.min(), ghs_band_resized.max()), (np.amin(vv), np.amax(vv)))

        meta.update(count=5, dtype=rio.float32)
        filename="%s_Stack_vv_vh_vvvh_ghs_dem.tiff"%date
        path = os.path.join(output_folder,filename)
        with rio.open(path,"w",**meta) as dst:
            dst.write_band(1,vv)
            dst.write_band(2,vh)
            dst.write_band(3,ratio)
            dst.write_band(4, ghs_data_resized)
            dst.write_band(5, dem_data_resized)
            dst.descriptions = tuple(['VV','VH','VV/VH_ratio',"Population","DEM"])
    return   

