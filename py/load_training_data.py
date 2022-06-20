#This file contains a function to load training data
#When running the script, the following should be present in your working directory:
######A folder ‘TrainingData’ that includes the following:
###########at least one folder called ‘xxxx_xx_xx’, containing:
###########one set of features (shapefile) with the title ‘Train_Polys_xxx_xx_xx.shp’
#################The shapefile should have an attribute ("Label") with class labels
###########some other files to support the shapefile
###########one Sentinel-1 raster with the title ‘TrainingSentinel_xxxx_xx_xx.tiff’:
######################This raster should have three bands (VV,VH,VV/VH)
######################optional: later include DEM as fourth band

# xxxx_xx_xx is the date (yyyy-mm-dd)
#the script then extracts the raster values of the corresponding Sentinel image within the training polygons
#the training polygons are classified as 0,1,2: 0=non-flooded, 1 = flooded land, 2= flooded urban area

import geopandas as gpd
import numpy as np
import os
from shapely.geometry import mapping
import rasterio as rio
from rasterio.mask import mask
from sklearn.model_selection import train_test_split


def loadTrainingData(training_folder):
    #Retrieve all folders in the training_folder
    trainingDates = os.listdir(training_folder)
    
    X = np.array([], dtype=np.int8).reshape(0,5) # pixels for training
    y = np.array([], dtype=np.string_) # labels for training
    
    #For each folder, we are going to extract the pixel values in the training polygons:
    for index, date_folder in enumerate(trainingDates):
        for file in os.listdir(os.path.join(training_folder,date_folder)):
            #Load shapefile using geopandas:
            if file.endswith(".shp"):
                polys = gpd.read_file(os.path.join(training_folder,date_folder,file))
                                #If you get an CRSError: uninstall geopandas and pyproj and reinstall them in your env
                                #should solve this
            #Retrieve the filepath to get the raster file (used later to open the file)                   
            if file.endswith(".tiff") and file.startswith("TrainingSentinel"):
                sentinel_location = os.path.join(training_folder,date_folder,file)
        #generate a list of shapely geometries
        geoms = polys.geometry.values 
        
        # extract the raster values within the polygon 
        with rio.open(sentinel_location) as src:
            band_count = src.count
            for index, geom in enumerate(geoms):
                feature = [mapping(geom)]
        
                # the mask function returns an array of the raster pixels within this feature
                out_image, out_transform = mask(src, feature, crop=True) 

                # reshape the array to [pixel count, bands]
                out_image_reshaped = out_image.reshape(-1, band_count)
                
                # append the labels to the y array
                y = np.append(y,[polys["Label"][index]] * out_image_reshaped.shape[0]) 
                # stack the pizels onto the pixel array
                X = np.vstack((X,out_image_reshaped))   
       
        # What are our classification labels?
    labels = np.unique(polys["Label"])
    print('The training data include {n} classes: {classes}\n'.format(n=labels.size, 
                                                                          classes=labels))
    """
    # We will need a "X" matrix containing our features, and a "y" array containing our labels
    print('Our X matrix is sized: {sz}'.format(sz=X.shape))
    print('Our y array is sized: {sz}'.format(sz=y.shape))
    """
    #After the for-loop, we have two arrays: X and y
    #X has all pixel values of the 3 bands
    #y has the labels per pixels
    
    #We randomly split X and y in training and test datasets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    #These arrays can later be used to train machine or deep learning models
    # and to get unbiased estimates of test accuracy
    return(X_train, X_test, y_train, y_test, polys)


#credit: http://patrickgray.me/open-geo-tutorial/chapter_5_classification.html 