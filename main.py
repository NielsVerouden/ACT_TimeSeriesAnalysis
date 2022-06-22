#############
## MAIN
#############
## This script is created by the authors as part of the RGIC-05 project
## The script includes a time series analysis method that can be used to gain
## insight into flood patterns in a specific area.
## The project is commissioned by the Dutch Ministry of Defence and is 
## conducted as part of the Remote Sensing and Geo-information Integration Course
## at Wageningen University & Research.
## June 2022
##
## Authors:
    ## Raimon Bach Pareja
    ## Mark Boeve
    ## Jakko-Jan van Ek
    ## Julia Sipkema
    ## Niels Verouden
    
## Please make sure that your current working directory contains a folder that 
## corresponds to the title of the variable input_folder.
## This folder should contain several zip folders: each zip folder should contain 
## a VV and VH Sentinel-1 image downloaded from sentinel hub.
## The images_folder is automatically created by the script if it is not yet 
## present in the current working directory.
import os
from py.load_data_from_zip_folders import load_data
from py.visualize import show_backscatter, show_histograms, visualizePrediction, visualizeData
from py.load_training_data import loadTrainingData
from py.train_model import GaussianNaiveBayes, RandomForest, knn, svm, RandomForest_FindParams
from py.predict import predict, getAccuracy_ConfMatrix
from py.postprocessing import createFrequencyMap
from py.ClipAndMask import clipRaster, maskWater
from py.loadDEM_GHS import addDEM_GHS

#### Create folders and load file names
#These folders should exist in your wd 
input_folder = './data/CapHaitienDownloadsApril2021' #Containing zip files with vv and vh Sentinel-1 data
training_folder = "./data/TrainingDataHaiti" #Containing training data (check load_training_data for procedures)
ghs_folder = "./data/GHS_Haiti" #Containing a zipfile which has a tile of the GHS dataset
DEM_filename = '2022-06-16-00_00_2022-06-16-23_59_DEM_COPERNICUS_30__Grayscale.tiff' #Filename of DEM that includes the extents of the Sentinel-1 images
DEM_folder = "./data/DEM_Haiti"
DEM = os.path.join(DEM_folder,DEM_filename)
DEM_name = "DEMCrop"

# These names are used later to store the files
waterbodies_folder = "./data/WaterBodies" #Containing a water bodies dataset
waterbodies_name = "WaterBodiesCrop"
water = "./data/WaterBodies/occurrence_80W_20Nv1_3_2020.tiff" #Filename of raster file that includes the extents of the Sentinel-1 images


#These folders are created by the script:
masked_predictions_folder = './data/FloodPredictions_masked'
images_folder = './data/SentinelTimeSeries'
stacked_images_folder = './data/SentinelTimeSeriesStacked'
stacked_images_folder_incl_ghs='./data/SentinelTimeSeriesStacked_Incl_DEM_GHS'

#When creating training data:
#input_folder="./data/ChadDownloadsNovember2020"
#ghs_folder="./data/GHS_Chad"
#DEM_folder="./data/DEM_Chad"

# Open water and DEM names
## Water data can be downloaded as tiff files from: Global Surface Water - Data Access
## (European Commission’s Joint Research Centre, 2022). https://global-surface-water.appspot.com/download 
## DEM data can be downloaded as tiff files from: EO Browser (2022). 
## EO Browser, Home, Explore, derived from, https://www.sentinel-hub.com/explore/eobrowser/
## More extensive explanation of downloading and storing data is in the file "TrainingDataProcedures.docx"
## BE AWARE that some tiff files are stored as '.tif' and some as '.tiff'

### Indicate preferences
#Indicate whether all images and histograms need to be plotted:
show_sentinel_histograms, show_sentinel_images = False, True

#Change your preferred model according to your preferences:
# Some models have additional parameters that can be adjusted to your liking
options = ["GaussianNaiveBayes", "RandomForest", "K-NearestNeighbours", "SupportVectorMachine"]
preferred_model = options[1] #Counting starts at zero !

## STEP 1: Load data
## Unzip images from the input_folder to the images_folder
## Stack vv and vh bands, together with the vv/vh ratio which is calculated by the function
load_data(input_folder, images_folder,stacked_images_folder,lee=True)
#This function stores all stacked rasters in the folder stacked_images_folder
addDEM_GHS(stacked_images_folder, stacked_images_folder_incl_ghs, ghs_folder, DEM_folder)



## Load a local subset of the water dataset to mask permanent water from the predictions
## NB it doesn't matter if the images referred to from stacked_rasters_names have different extents
water_sentinel_combis = clipRaster(stacked_images_folder_incl_ghs, water, waterbodies_folder, waterbodies_name)

#Show some simple histograms and plot the images, if specified in line 40:
if show_sentinel_histograms:
    show_histograms(stacked_images_folder_incl_ghs)

if show_sentinel_images:
    show_backscatter(stacked_images_folder_incl_ghs)


##STEP 3: Load training data and train a supervised classification model
#Check load_training_data.py to check how the training folder should be structured
X_train, X_test, y_train, y_test, training_polys = loadTrainingData(training_folder)
visualizeData(X_train, y_train)

#Find the best parameters for random forest using a cross validation approach
model, results,best_params = RandomForest_FindParams(X_train,y_train)
#Train a random forest classifier
#And estimate test accuracy. A confusion matrix is shown to visualize the errors of the model
#model = GaussianNaiveBayes(X_train,y_train)    
model = RandomForest(X_train, y_train) #See train_model.py for additional parameters
#model= knn(X_train, y_train)
#model = svm(X_train, y_train)    
    
    
test_acc, accuracies, cm = getAccuracy_ConfMatrix(model,X_test, y_test)

#Predict flooded areas
## Classify each pixel of each image as flooded area, flooded urban area or dry area
## Either for one file (e.g. stacked_rasters_names[0]) or for all files in a list
# Set majorityfilter to True to apply majority filter (more accurate but takes a few minutes)
predictions_dict, predictions_filenames= predict(stacked_images_folder_incl_ghs, model, training_polys, majorityfilter=False)

## predictions is a dictionairy containing a time series of classified maps
#Now mask the water bodies from each prediction
masked_predictions_names = maskWater(water_sentinel_combis,masked_predictions_folder,mask_value=100)

## STEP 3: Visualize Results
#show prediction results of one image (uncomment):
#visualizePrediction(prediction)
#show all prediction results:
visualizePrediction(masked_predictions_names, stacked_images_folder_incl_ghs)


## STEP 4: Post processing
## Create a flood frequency map based on the time series
## How often is each pixel flooded?
## Create nice visualization
frequencymaps= createFrequencyMap(masked_predictions_names)
## Optionally: make animated map that shows classification for each time step in order
## to visualize flood extent over time