import rasterio as rio
from rasterio.plot import show
import os
import numpy as np
##stack images from the list of dataset readers
##the function returns a list containing all rasterio dataset readers for each date
## where each dataset reader contains three bands: VV, VH and VV/VH ratio
##dest_name is the folder in which images are stored

def stack_images(image_names, images, input_name='radar_time_series', output_name = 'radar_time_series_stacked'):
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
        '''
        #Let's calculate the vv/vh ratio
        vv = rio.open(input_name+'/'+ file_list_one_date[0]).read(1)
        vh = rio.open(input_name+'/'+ file_list_one_date[1]).read(1)
        np.seterr(divide='ignore', invalid='ignore')
        vvvh_ratio = np.empty(vv.shape, dtype=rio.float32)
        check = np.logical_or ( vv > 0, vh > 0 )
        
        #VV/VH ratio is calculated as VV-VH, since our data is measured in decibels
        vvvh_ratio = np.where ( check,  (vv-vh), -999 )
        '''
        #######
        #Let's create a stack for each date containing the two tiff files and a third calculated raster
        # Read metadata of first file of each date
        with rio.open(input_name+'/'+ file_list_one_date[0]) as src0:
            meta = src0.meta
        # Update meta to reflect the number of layers
        meta.update(count = len(file_list_one_date))
        
        # Read each layer and write it to stack
        with rio.open(output_name+'/'+str(date)+'_stack.tiff', 'w', **meta) as dst:
            for id, layer in enumerate(file_list_one_date, start=1):
                with rio.open(input_name+'/'+ layer) as src1:
                    dst.write_band(id, src1.read(1))
            dst.descriptions = tuple([file_list_one_date[0], file_list_one_date[1]])
        list_of_stacked_images.append(output_name+'/'+str(date)+'_stack.tiff')
        
    #stacked_rasters = [rio.open(filename) for filename in list_of_stacked_images]
    return(list_of_stacked_images)             

def add_ratio(stacked_names, folder='radar_time_series_stacked'):
    for stack in stacked_names:
        
        raster_stack = rio.open(stack)
        meta = raster_stack.meta
        meta.update(count=3)
        vv = raster_stack.read(1)
        vh = raster_stack.read(2)
        np.seterr(divide='ignore', invalid='ignore')
        vvvh_ratio = np.empty(raster_stack.shape, dtype=rio.float32)
        check = np.logical_or ( vv > 0, vh > 0 )
        
        #VV/VH ratio is calculated as VV-VH, since our data is measured in decibels
        vvvh_ratio = np.where ( check,  (vv-vh), -999 )
        vvvh_ratio = vvvh_ratio.astype(rio.float32)
        
        #vvvh_ratio_rst.meta = raster_stack.meta
        #stack.meta.update(count=3)
    #print(vvvh_ratio.astype(raster.width)
        raster_stack.close()
        with rio.open(stack, 'w', **meta) as dst:
            #meta = dst.meta
            dst.write_band(3,vvvh_ratio)
    return(stacked_names)

## credit: https://automating-gis-processes.github.io/CSC18/lessons/L6/raster-calculations.html


#stacked_rasters, ratio = add_ratio(stacked_rasters_names, stacked_rasters, folder='stacked_images_folder')
'''
with rio.open('radar_time_series_stacked/2022-01-25_stack.tiff','r') as src0:
    meta = src0.meta 
    
with rio.open("test.tiff",'w',**meta) as dst:
    dst.write(ratio,3)

with rio.open("test.tiff",'r') as dst:
    print(dst.meta)
''' 
