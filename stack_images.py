import rasterio as rio
from rasterio.plot import show
import os
import numpy as np
import re
##stack images from the list of dataset readers
##the function returns a list containing all rasterio dataset readers for each date
## where each dataset reader contains three bands: VV, VH and VV/VH ratio
##dest_name is the folder in which images are stored

def stack_images(image_names, input_name='radar_time_series', output_name = 'radar_time_series_stacked'):
    if not os.path.exists(output_name): os.makedirs(output_name)
    list_of_stacked_images = []
    for name in image_names:
        date = name[0:10]
        file_list_one_date = [name]
        
        #Second for-loop to loop over all images and find the filenames of images of the same date
        for sec_name in image_names:
            if sec_name[0:10] == date and name != sec_name:
                file_list_one_date.append(sec_name)
        
        #Now we have a list with two elements: filenames of tiff files of the same date
   
        #Let's create a stack for each date containing the two tiff files 
        # Read metadata of first file of each date
        # Metadata is to be used later when writing the files
        with rio.open(input_name+'/'+ file_list_one_date[0]) as src0:
            meta = src0.meta
        # Update meta to reflect the number of layers
        # If it is not updated an error is raised
        meta.update(count = len(file_list_one_date))
        
        # Read each layer and write it to stack
        """
        with rio.open(output_name+'/'+str(date)+'_stack.tiff', 'w', **meta) as dst:
            for id, layer in enumerate(file_list_one_date, start=1):
                with rio.open(input_name+'/'+ layer) as src1:
                    dst.write_band(id, src1.read(1))
        """
        
        #Finding the VV and VH tiff files using regex pattern:
        with rio.open(output_name+'/'+str(date)+'_stack.tiff', 'w', **meta) as dst:
            vvreg = re.compile(r'\S*_VV_\S*')
            vvlayer = list(filter(vvreg.search, file_list_one_date))[0]
            
            vhreg = re.compile(r'\S*_VH_\S*')
            vhlayer = list(filter(vhreg.search, file_list_one_date))[0]
            
            with rio.open(input_name+'/'+ vvlayer) as src1:
                dst.write_band(1, src1.read(1))
            with rio.open(input_name+'/'+ vhlayer) as src1:
                dst.write_band(2, src1.read(1))
        dst.close()  
         
        list_of_stacked_images.append(output_name+'/'+str(date)+'_stack.tiff')
        
    #stacked_rasters = [rio.open(filename) for filename in list_of_stacked_images]
    list_of_stacked_images = sorted(list(set(list_of_stacked_images)))
    return(list_of_stacked_images)             

def add_ratio(stacked_names, folder='radar_time_series_stacked'):
    for stack in stacked_names:
        
        raster_stack = rio.open(stack)
        
        meta = raster_stack.meta
        meta.update(count=3)
        vv = raster_stack.read(1)
        vh = raster_stack.read(2)
        
        #np.seterr(divide='ignore', invalid='ignore')
        vvvh_ratio = np.empty(raster_stack.shape, dtype=rio.float32)
        check = np.logical_or ( vv > 0, vh > 0 )
        
        #VV/VH ratio is calculated as VV-VH, since our data is measured in decibels
        vvvh_ratio = np.where ( check,  (vv-vh), -999 )
        vvvh_ratio = vvvh_ratio.astype(rio.float32)
        
        #close datareader: necessary to prevent errors when appending the new band to the files
        raster_stack.close()
        
        with rio.open(stack, 'w', **meta) as dst:
            #append vv/vh ratio to the band
            dst.write_band(1,vv.astype(rio.float32))
            dst.write_band(2,vh.astype(rio.float32))
            dst.write_band(3,vvvh_ratio)
            dst.descriptions = tuple(['VV','VH','VV/VH_ratio'])
    return(stacked_names)

## credit: https://automating-gis-processes.github.io/CSC18/lessons/L6/raster-calculations.html
"""
stacked_rasters_names = stack_images(list_of_images, input_name=images_folder, output_name=stacked_images_folder)

for stack in stacked_rasters_names:
    
    raster_stack = rio.open(stack)
    
    meta = raster_stack.meta
    print(raster_stack.tags(ns='polar'))

raster_stack.close()
"""
