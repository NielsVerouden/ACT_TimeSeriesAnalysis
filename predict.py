#Predict flood/dry/flooded urban based on a model


import rasterio as rio
import numpy as np
from rasterio.plot import reshape_as_raster, reshape_as_image
from sklearn.metrics import accuracy_score, confusion_matrix, mean_squared_error, mean_absolute_percentage_error, r2_score, mean_absolute_error
from sklearn.metrics import ConfusionMatrixDisplay

"""
from rasterio.plot import show
from rasterio.plot import show_hist
from rasterio.windows import Window
from matplotlib import pyplot as plt
"""
def predict(image_path, model, training_polys):
    
    #if image_path is a list, we have to predict for each file in the list,
    #    else we predict only once
    image_path = image_path.split() if type(image_path) != list else image_path
    predictions = {}
    for file in image_path:
        with rio.open(file) as src:
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
        predictions[file[-21:-11]]=class_prediction
    return(predictions)

def getAccuracy_ConfMatrix(model,x,y_true):
    y_pred = model.predict(x)
    acc = accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred)
    cm_display = ConfusionMatrixDisplay(cm).plot()
    return(acc,cm)



