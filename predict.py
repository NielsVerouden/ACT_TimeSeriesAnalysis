#Predict flood/dry/flooded urban based on a model


import rasterio as rio
from rasterio.plot import show
from rasterio.plot import show_hist
from rasterio.windows import Window
from rasterio.plot import reshape_as_raster, reshape_as_image
import numpy as np
from matplotlib import pyplot as plt

def predict(image_path, model, training_polys):
    with rio.open(image_path) as src:
        # may need to reduce this image size if your kernel crashes, takes a lot of memory
        img = src.read()
    
    # Take our full image and reshape into long 2d array (nrow * ncol, nband) for classification
    reshaped_img = reshape_as_image(img)
    class_prediction = model.predict(reshaped_img.reshape(-1, 3))
    # Reshape our classification map back into a 2D matrix so we can visualize it
    class_prediction = class_prediction.reshape(reshaped_img[:, :, 0].shape)
    
    #Helper function to convert numbers to string labels:
    def str_class_to_int(class_array):
       class_array[class_array == np.unique(training_polys["Label"])[0]] = 0
       class_array[class_array == np.unique(training_polys["Label"])[1]] = 1
       class_array[class_array == np.unique(training_polys["Label"])[2]] = 2
       return(class_array.astype(int))
    
    class_prediction = str_class_to_int(class_prediction)
    return(class_prediction)

