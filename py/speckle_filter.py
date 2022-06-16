from scipy.ndimage.filters import uniform_filter
from scipy.ndimage.measurements import variance
import rasterio as rio
from rasterio.plot import show
import os

def lee_filter(img, size):
    img_mean = uniform_filter(img, (size, size))
    img_sqr_mean = uniform_filter(img**2, (size, size))
    img_variance = img_sqr_mean - img_mean**2

    overall_variance = variance(img)

    img_weights = img_variance / (img_variance + overall_variance)
    img_output = img_mean + img_weights * (img - img_mean)
    return img_output

def apply_lee_filter(raster_images, input_folder, size=5):
     
    for stack in raster_images:
        stack = os.path.join(input_folder,stack)

        with rio.open(stack,'r') as dst:
            meta = dst.meta
            image = dst.read(1)
            image_sf = lee_filter(image, size)
            dst.close()
            
        with rio.open(stack, 'w', **meta) as dst:
            dst.write_band(1,image_sf.astype(rio.float32))
            #dst.descriptions = tuple(['bandname'])
    return(raster_images)
            
'''
with rio.open(stacked_rasters_names[10],'r') as src:
    img=src.read(1)
    test_image = lee_filter(img,5)
    
    meta = src.meta   
    
with rio.open('testspeckle.tiff', 'w', **meta) as dst:
    #append vv/vh ratio to the band
    dst.write_band(1,test_image.astype(rio.float32))    
    
with rio.open('testspeckle.tiff', 'r', **meta) as dst:
    show(dst)
    
    #credit for function lee_filter: https://stackoverflow.com/questions/39785970/speckle-lee-filter-in-python
    '''