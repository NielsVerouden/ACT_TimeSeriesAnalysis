from scipy.ndimage.filters import uniform_filter
from scipy.ndimage.measurements import variance
import os
from zipfile import ZipFile
import glob
import rasterio as rio
import numpy as np

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
    """
    Parameters
    ----------
    input_name: str: folder containing multiple zip folders
    dest_name: str: folder where the unzipped rasters will be located
    stack_dest_name: str: folder where stacks of vv and vh bands with vv/vh index will be located
    lee (opt): Boolean: indicated whether to apply the Lee speckle filter to each image (default=True)
    size (opt): int: size used by the Lee filter (default=5) 
    -------
    Loads the Sentinel images from the zip folder.
    Also creates stacks of the images of the same date, 
    containing a vv band, vh band and a vv/vh indx band.
    For information on how to download data: refer to TimeSeriesFloodAnalysis_Instructions.pdf
    -------
    """

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

                #extract image to destination folder
                zip_ref.extract( zipinfo, dest_name)
            zip_ref.close() # close file
  

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
        
        #Calculate an index that highlights water bodies as third band:
        vvvh_sum = np.add(vv_data,vh_data)
        vvvh_dif = np.subtract(vv_data,vh_data)
        vvvh_index = np.divide(vvvh_dif,vvvh_sum,out=np.zeros_like(vvvh_sum), where=vvvh_sum!=0)

        #Update meta to fit three layers
        meta.update(count=3,dtype=rio.float32)
               
        stack_filename="%s_vv_vh_vvvhratio_Stack.tiff"%date
        stack_filepath=os.path.join(stack_dest_name,stack_filename)
        with rio.open(stack_filepath, "w",**meta) as dst:
            dst.write_band(1,vv_data)
            dst.write_band(2,vh_data)
            dst.write_band(3,vvvh_index)
            dst.descriptions = tuple(['VV','VH','VV/VH_index'])
    return

#credit for function lee_filter: https://stackoverflow.com/questions/39785970/speckle-lee-filter-in-python
