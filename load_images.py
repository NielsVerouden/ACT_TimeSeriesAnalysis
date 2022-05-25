import rasterio as rio
from rasterio.plot import show
import os

##load images from folder using rasterio
##the function returns a list containing all rasterio dataset readers
##dest_name is the folder in which images are stored

def load_images(image_names, dest_name='radar_time_series'):
    if not os.path.exists(dest_name): os.makedirs(dest_name)


    #Load images from folder using rasterio package:
    rasters = [rio.open(dest_name+'/'+filename) for filename in image_names]
    #show(rasters[0], title=str(rasters[0]), cmap='gist_ncar')
    return(rasters)