#Predict flood/dry/flooded urban based on a model


import rasterio as rio
import numpy as np
from rasterio.plot import reshape_as_raster, reshape_as_image
from sklearn.metrics import accuracy_score, confusion_matrix, mean_squared_error, mean_absolute_percentage_error, r2_score, mean_absolute_error
from sklearn.metrics import ConfusionMatrixDisplay
import os
from scipy.ndimage.filters import generic_filter
import numpy as np
from scipy.stats import mode
import pandas as pd
from matplotlib import pyplot as plt

"""
from rasterio.plot import show
from rasterio.plot import show_hist
from rasterio.windows import Window
from matplotlib import pyplot as plt
"""
def predict(folder, model, training_polys, dest_name="./data/FloodPredictions", 
            majorityfilter=False, size=7):
    
    if not os.path.exists(dest_name): os.makedirs(dest_name)
    #if image_path is a list, we have to predict for each file in the list,
    #    else we predict only once
    #image_path = image_path.split() if type(image_path) != list else image_path
    predictions = {} #dictionary that will contain dates and corresponding numpy arrays
    preds_filenames = [] #list that will contain the file locations of tiff files
    
    input_files = os.listdir(folder)
    for file in input_files:
        path = os.path.join(folder,file)
        with rio.open(path) as src:
            # may need to reduce this image size if your kernel crashes, takes a lot of memory
            img = src.read()
            kwargs = src.meta
            kwargs.update(
                    dtype=rio.float32,
                    count=1,
                    compress='lzw')
        # Take our full image and reshape into long 2d array (nrow * ncol, nband) for classification
        reshaped_img = reshape_as_image(img)
        #reshaped_img=img.reshape(-1,5)
        class_prediction = model.predict(reshaped_img.reshape(-1, 5))
        # Reshape our classification map back into a 2D matrix so we can visualize it
        class_prediction = class_prediction.reshape(reshaped_img[:, :, 0].shape)
        
        #Helper function to convert numbers to string labels:
        def str_class_to_int(class_array):
            class_array[class_array == 'Dry'] = 0
            class_array[class_array == 'Flooded'] = 1
            class_array[class_array == 'FloodedUrban'] = 2
            return(class_array.astype(int))

        
        class_prediction = str_class_to_int(class_prediction)
        
        
        ####
        ##filter the prediction result to remove isolated spots (takes quite some time)
        if majorityfilter:
            print("Applying majority filter ... \nMight take a few minutes.")
            #filter_function takes an array of x values and returns an array of the same size only 
            #containing the most occuring value
            
            #this filter function is applied to parts of the the array containing the predictions
            # by means of a lambda function (sliding window approach)
            # the size of the sliding window is 3x3 by default but can be specified by the user
            def filter_function(invalues):
               invalues_mode = mode(invalues, axis=None, nan_policy='omit')
               return invalues_mode[0]
            
            function = lambda array: generic_filter(array, function=filter_function, size=size)
            class_prediction = function(class_prediction)
            #credit: https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html

        predictions[file[0:10]]=class_prediction #key=date, value=prediction array
        
        outputfilename = "FloodPrediction_%s.tiff" %file[0:10]
        outputpath = os.path.join(dest_name,outputfilename)
        with rio.open(outputpath, 'w', **kwargs) as dst:
            dst.write_band(1, class_prediction.astype(rio.float32))
        preds_filenames.append(outputpath)
        
    return(predictions, preds_filenames)

def getAccuracy_ConfMatrix(model,test_data):
    predictor_cols = ['mean_VV','mean_VH','mean_VV/VH_ratio','mean_Population','mean_DEM']
    #Load X and y data
    Xtest = test_data[predictor_cols].values.tolist()
    ytest = test_data['Label']
    
    #Predict y based on x
    y_pred = model.predict(Xtest)
    
    #Obtain accuracy score and create confusion matrix
    acc = accuracy_score(ytest, y_pred)
    cm = confusion_matrix(ytest, y_pred)
    plt.figure()
    ConfusionMatrixDisplay(cm).plot()
    plt.show()
    #Create arrays containing the user and producer accuracies
    #Divide the N of classified cases by the amount of predicted cases (-> user acc)
    users_accs = cm.diagonal()/np.sum(cm,axis=0,keepdims=False)
    
    #Divide the N of classified cases by the amount of actual cases (-> producer acc)
    #Axis=1 -> horizontal sum (in the confusion matrix)
    producers_accs = cm.diagonal()/np.sum(cm,axis=1,keepdims=False)
    
    df = pd.DataFrame(np.array([users_accs,producers_accs]),
                      columns=["Dry Area",
                               "Flooded Land",
                               "Flooded Urban"])
    df.insert(0, "Metric", ["User's Accuracy","Producer's Accuracy"])
    print("="*60,"\n",df,"\n", "="*60,"\n","Overall test accuracy = %.2f"%acc)
    return(acc,df,cm)

"""
#Formerly used:
def getAccuracy_ConfMatrix(model,x,y_true):
    y_pred = model.predict(x)
    acc = accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred)
    plt.figure()
    ConfusionMatrixDisplay(cm).plot()
    plt.show()
    #Create arrays containing the user and producer accuracies
    #Divide the N of classified cases by the amount of predicted cases (-> user acc)
    users_accs = cm.diagonal()/np.sum(cm,axis=0,keepdims=False)
    
    #Divide the N of classified cases by the amount of actual cases (-> producer acc)
    #Axis=1 -> horizontal sum (in the confusion matrix)
    producers_accs = cm.diagonal()/np.sum(cm,axis=1,keepdims=False)
    
    df = pd.DataFrame(np.array([users_accs,producers_accs]),
                      columns=["Dry Area",
                               "Flooded Land",
                               "Flooded Urban"])
    df.insert(0, "Metric", ["User's Accuracy","Producer's Accuracy"])
    print("="*60,"\n",df,"\n", "="*60,"\n","Overall test accuracy = %.2f"%acc)
    return(acc,df,cm)
"""


