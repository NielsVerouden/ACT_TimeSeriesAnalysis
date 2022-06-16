#############
## LOAD IMAGES FROM ZIP FILE
############


import os
from zipfile import ZipFile
import glob
import rasterio as rio
import numpy as np

def load_data(input_name, dest_name, stack_dest_name, human_settlement_folder=None):
#input_name =  folder containing multiple zip folders
# dest_name =  destination folder of files from zip folders
# stack_dest_name = destination folder of stacks of vv and vh bands with vv/vh ratio
    if not os.path.exists(dest_name): os.makedirs(dest_name)
    if not os.path.exists(stack_dest_name): os.makedirs(stack_dest_name)
    extension = ".zip"
    #image_names = []
    dates=[] #initialize list of dates
    #Unzip files from input_name to a new folder
    for item in os.listdir(input_name): # loop through items in dir
        if item.endswith(extension): # check for ".zip" extension
            file_name =  os.path.join(input_name, item)  # get full path of files
            zip_ref = ZipFile(file_name) # create zipfile object
            zipinfos=zip_ref.infolist()
            for zipinfo in zipinfos:
                #change filename to something shorter
                date = zipinfo.filename[0:10]
                if date not in dates: dates.append(date) #append date to the list of unique dates
                info = zipinfo.filename[-79:]
                zipinfo.filename = date + '_' + info
                #image_names.append(zipinfo.filename)
                #extract image to destination folder
                zip_ref.extract( zipinfo, dest_name)
            zip_ref.close() # close file
            #os.remove(file_name) # delete zipped file 
     
    #Unzip human settlement layer from human_settlement_folder:
    if human_settlement_folder is not None:
        for item in os.listdir(human_settlement_folder):
            if item.endswith(extension):
                file_name=os.path.join(human_settlement_folder,item)
                zip_ref=ZipFile(file_name)
                zipfilenames=zip_ref.namelist()
                for zipname in zipfilenames:
                    if zipname.endswith(".tif"):
                        zip_ref.extract(zipname, human_settlement_folder)
                zip_ref.close()
        
        #Now load the human settlement raster:
        cities_path=os.path.join(human_settlement_folder,"GHS_BUILT_LDS2014_GLOBE_R2018A_54009_250_V2_0.tiff")
        with rio.open(cities_path, "r") as dst:
            cities_meta=dst.meta
            cities = dst.read(1)
            
    #Now load the files with rasterio and stack the vv and vh files of the same dates together 
    # with the calculated vv/vh ratio
    for date in dates:
        vvname = '%s*_VV_*.tiff' % date
        vvpattern = os.path.join(dest_name,vvname)
        
        vhname = '%s*_VH_*.tiff' % date
        vhpattern = os.path.join(dest_name,vhname)
        
        #Look for the vv and vh files for each date using global pattern
        for file in glob.glob(vvpattern):
            image_path_vv = file
        
        for file in glob.glob(vhpattern):
            image_path_vh = file
        
        #Open files as arrays and get metadata:
        with rio.open(image_path_vv,"r") as vv:
            meta=vv.meta
            vv_data=vv.read(1)
        
        with rio.open(image_path_vh,"r") as vh:
            vh_data=vh.read(1)
        
        #Calculate ratio as third band:
        #np.seterr(divide='ignore', invalid='ignore')
        vvvh_ratio = np.empty(vh_data.shape, dtype=rio.float32)
        check = np.logical_or ( vv_data > 0, vh_data > 0 )
        
        #VV/VH ratio is calculated as VV-VH, since our data is measured in decibels
        vvvh_ratio = np.where ( check,  (vv_data-vh_data), -999 )
        vvvh_ratio = vvvh_ratio.astype(rio.float32)
        
        #Update meta to fit three layers
        meta.update(count=3)
        
        stack_filename="%s_vv_vh_vvvhratio_Stack.tiff"%date
        stack_filepath=os.path.join(stack_dest_name,stack_filename)
        with rio.open(stack_filepath, "w",**meta) as dst:
            dst.write_band(1,vv_data.astype(rio.float32))
            dst.write_band(2,vh_data.astype(rio.float32))
            dst.write_band(3,vvvh_ratio)
            dst.descriptions = tuple(['VV','VH','VV/VH_ratio'])
    return


    