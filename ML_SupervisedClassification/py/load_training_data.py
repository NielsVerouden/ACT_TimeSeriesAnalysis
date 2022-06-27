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
import rasterio as rio
import pandas as pd
from rasterstats import zonal_stats


#Function to load data from training folder
#Which returns two dataframes that can be used for training
def loadTrainingData(training_folder, train_size=0.7):
    """
    Parameters
    ----------
    training_folder: str: folder containing training data
    train_size (opt): float: value indicating the amount of data to use for training (0-1)
    -------
    Loads the mean values of the Sentinel images in the training polygons
    and returns a dataset with training and one with test data.
    For information on how to manage the training_folder: refer to TimeSeriesFloodAnalysis_Instructions.pdf
    -------
    """
    #Retrieve all folders in the training_folder
    trainingDates = os.listdir(training_folder)
    dataframes = []
    #For each folder, we are going to extract the mean pixel values in the training polygons:
    for index, date_folder in enumerate(trainingDates):
        for file in os.listdir(os.path.join(training_folder,date_folder)):
            #Load shapefile using geopandas:
            if file.endswith(".shp"):
                pointfile=os.path.join(training_folder,date_folder,file)
        
            #Retrieve the filepath to get the raster file (used later to open the file)                   
            if file.endswith(".tiff") and file.startswith("TrainingSentinel"):
                sentinel_location = os.path.join(training_folder,date_folder,file)
        #sentinel_location = "./data/SentinelTimeSeriesStacked/2021-04-05_vv_vh_vvvhratio_Stack.tiff"
                
        df = gpd.read_file(pointfile) #Create geodataframe from the points
        stats = ['mean'] 
        
        with rio.open(sentinel_location, "r+") as src:
            transform = src.transform
            names=src.descriptions
            band_count = src.count
            #For each band, calculate the mean pixel values using zonal statistics
            #Put these means in a dataframe called df2
            #Then, join this dataframe to df, which contains the information from the shapefile
            for i in range(1,band_count+1):
                df2 = pd.DataFrame(zonal_stats(vectors=df['geometry'], raster=src.read(i),affine=transform,  stats=stats))
                df2.columns=['{0}_{1}'.format(stat, names[i-1]) for stat in stats]
                df = df.join(df2)
        dataframes.append(df) 
    #Now concatenate all dataframes in a single dataframe, containing all training data
    df = pd.concat(dataframes)
    df = df.reset_index()
    
    #We now have:
    #df.columns.tolist()
    #['Shape_Leng','Shape_Area','Class','Label','geometry','mean_VV','mean_VH','mean_VV/VH_ratio','mean_Population','mean_DEM']
        
    #Split data into train and test (https://stackoverflow.com/questions/24147278/how-do-i-create-test-and-train-samples-from-one-dataframe-with-pandas)
    msk = np.random.rand(len(df)) < train_size
    train = df[msk]
    test = df[~msk]
    return (train, test)



#credit: http://patrickgray.me/open-geo-tutorial/chapter_5_classification.html 
