#This file contains a function to load training data
#When running the script, the following should be present in your working directory:
######A folder ‘TrainingData’ that includes the following:
###########at least one folder called ‘xxxx_xx_xx’, containing:
###########one set of features (shapefile) with the title ‘Train_Polys_xxx_xx_xx.shp’
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

training_folder = "TrainingData"


#def ..
#Retrieve all folders in the training_folder
trainingDates = os.listdir(training_folder)

#For each folder, we are going to extract the pixel values in the training polygons:
for index, date_folder in enumerate(trainingDates):
    for file in os.listdir(os.path.join(training_folder,date_folder)):
        if file.endswith(".shp"):
            polys = gpd.read_file(os.path.join(training_folder,date_folder,file))
            
import pyproj
print(pyproj.datadir.get_data_dir()            )
