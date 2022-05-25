import rasterio as rio
import os

##stack images from the list of dataset readers
##the function returns a list containing all rasterio dataset readers for each date
## where each dataset reader contains three bands: VV, VH and VV/VH ratio
##dest_name is the folder in which images are stored

def stack_images(image_names, images, input_name='radar_time_series', output_name = 'radar_time_series_stacked'):
    if not os.path.exists(output_name): os.makedirs(output_name)
    for name in image_names:
        date = name[0:10]
        file_list_one_date = [name]
        
        #Second for-loop to loop over all images and find the filenames of images of the same date
        for sec_name in image_names:
            if sec_name[0:10] == date and name != sec_name:
                file_list_one_date.append(sec_name)
        
        #Now we have a list with two elements: filenames of tiff files of the same date
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
                    
stack_images(list_of_images, rasters)                
