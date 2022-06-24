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
from rasterio.features import sieve, shapes

def predict(images_folder, predictions_folder, model, apply_sieve=True, sieze_size=13):
    if not os.path.exists(predictions_folder): os.makedirs(predictions_folder)
    input_files = os.listdir(images_folder)
    for file in input_files:
        #Create path to the input images
        path = os.path.join(images_folder,file)
        #Open the input image with rasterio and save the metadata and the 5 arrays (i.e. bands)
        with rio.open(path) as src:
            meta=src.meta
            bands=src.read()
    
        #Reshape to (nrows, ncols, bands)
        bands_reshaped = reshape_as_image(bands)
        
        #Reshaope  to 2d array
        bands_ready_for_classification = bands_reshaped.reshape(int(np.prod(bands_reshaped.shape)/5),5)
        
        r = model.predict(bands_ready_for_classification) #Predict using the model and Sentinel2 bands
        r = r.reshape(bands[0].shape) #Reshape into a 2d array
        
        ##################################################
        # Helper function to convert strings to integers #
        def str_class_to_int(class_array):
            class_array[class_array == 'Dry'] = 0
            class_array[class_array == 'Flooded'] = 1
            class_array[class_array == 'FloodedUrban'] = 2
            return(class_array.astype(int))
        ##################################################
        
        r=str_class_to_int(r)
        
        #Write the r (result) array to a georeferenced image based on the updated metadata
        meta.update(dtype='int16',
                    count=1,
                    compress='lzw')
        outputfilename = "FloodPrediction_%s.tiff" %file[0:10]
        dest_path = os.path.join(predictions_folder, outputfilename)
        with rio.open(dest_path, 'w', **meta) as dst:
            dst.write_band(1, r)
        ##################################################
        ## Now sieve the prediction, a.k.a remove randomly scattered pixels
        if apply_sieve:
            # Register GDAL and OGR drivers.
            with rio.Env():
    
                # Read a raster to be sieved.
                with rio.open(dest_path, "r") as src:
                    prediction = src.read(1)

                # Sieve out features x pixels or smaller.
                sieved = sieve(prediction, sieze_size, out=np.zeros(src.shape, src.dtypes[0]))

                # Write out the sieved raster.
                kwargs = src.meta
                kwargs.update(dtype=rio.int8)
                kwargs['transform'] = rio.transform.guard_transform(kwargs['transform'])
                with rio.open(dest_path, 'w', **kwargs) as dst:
                    dst.write(sieved, indexes=1)
    return
      

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

#Credit:
    #https://github.com/rasterio/rasterio/blob/master/examples/sieve.py
    #https://gis.stackexchange.com/questions/373720/performing-supervised-classification-on-sentinel-images
