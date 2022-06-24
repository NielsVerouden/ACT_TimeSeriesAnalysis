#############
## LOAD IMAGES FROM ZIP FILE
############
from scipy.ndimage.filters import uniform_filter
from scipy.ndimage.measurements import variance
import os
from zipfile import ZipFile
import glob
import rasterio as rio
import numpy as np
from numpy import linalg
from sklearn.preprocessing import normalize

def lee_filter(img, size):
    #Applies a speckle filter with a specified size to an input array
    img_mean = uniform_filter(img, (size, size))
    img_sqr_mean = uniform_filter(img**2, (size, size))
    img_variance = img_sqr_mean - img_mean**2

    overall_variance = variance(img)

    img_weights = img_variance / (img_variance + overall_variance)
    img_output = img_mean + img_weights * (img - img_mean)
    return img_output

def load_data(input_name, dest_name, stack_dest_name, lee=True,size=5):
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
            vv_data = vv_data.astype('float32')
            
        with rio.open(image_path_vh,"r") as vh:
            vh_data=vh.read(1)
            vh_data = vh_data.astype('float32')
            
        #Optional: Lee speckle filter
        if lee:
            vv_data = lee_filter(vv_data, size)
            vh_data = lee_filter(vh_data, size)
         
        #Scale to range 0-1    
        vv_data /= np.amax(vv_data)
        vh_data /= np.amax(vh_data)
        
              #Calculate ratio as third band:
        #np.seterr(divide='ignore', invalid='ignore')
        #vvvh_ratio = np.empty(vh_data.shape, dtype=rio.float32)
       # check = np.logical_or ( vv_data > 0, vh_data > 0 )
        
        #VV/VH ratio is calculated as VV/VH, since our data is measured in digital numbers
        #If the data is measured in decibels, it would have to be VV-VH
        # Division by zero returns a zero due to the where statement
                    #vvvh_ratio = np.where ( check,  (vv_data/vh_data), -999 )
       # vvvh_ratio = np.divide(vv_data, vh_data, out=np.zeros_like(vv_data), where=vh_data!=0)
        vvvh_sum = np.add(vv_data,vh_data)
        vvvh_dif = np.subtract(vv_data,vh_data)
        vvvh_index = np.divide(vvvh_dif,vvvh_sum,out=np.zeros_like(vvvh_sum), where=vvvh_sum!=0)
        # Replace outliers of the data by the median
       # vvvh_ratio=np.where(vvvh_ratio>5,np.median(vvvh_ratio),vvvh_ratio)
        #vvvh_ratio_rescaled = np.interp(vvvh_ratio, (vvvh_ratio.min(), vvvh_ratio.max()), (np.amin(vh_data), np.amax(vh_data)))

        #Update meta to fit three layers
        meta.update(count=3,dtype=rio.float32)
               
        stack_filename="%s_vv_vh_vvvhratio_Stack.tiff"%date
        stack_filepath=os.path.join(stack_dest_name,stack_filename)
        with rio.open(stack_filepath, "w",**meta) as dst:
            dst.write_band(1,vv_data)
            dst.write_band(2,vh_data)
            dst.write_band(3,vvvh_index)
            dst.descriptions = tuple(['VV','VH','VV/VH_ratio'])
    """
    print(vv_data[0:10])
    print("\n")
    print(vh_data[0:10])
    print("\n")
    print(vvvh_index[0:10])
    print("\n")
    """
    return

#credit for function lee_filter: https://stackoverflow.com/questions/39785970/speckle-lee-filter-in-python
"""
redundant:
path=os.path.join(stacked_images_folder_incl_ghs,"2021-04-05_Stack_vv_vh_vvvh_ghs_dem.tiff")
src=rio.open(path,"r")
vv=src.read(1)
vh=src.read(2)
ratio=src.read(3)

u = np.median(ratio)
s = np.std(ratio)
f1 = u - 2*s
f2 = u + 0.5

new_ratio = np.where(ratio>f2, ratio, np.median(ratio))

new_ratio_rescaled = np.interp(new_ratio, (new_ratio.min(), f2), (np.amin(vh), np.amax(vh)))
print(np.histogram(new_ratio_rescaled))

audio = ratio/(u)
image *= (255.0/image.max())
"""