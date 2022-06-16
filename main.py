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

from load_data_from_zip_folders import load_data
#from load_images import load_images
#from stack_images import stack_images, add_ratio
#from stack_images import add_ratio
from visualize import show_backscatter, show_histograms, visualizePrediction
from speckle_filter import apply_lee_filter
from load_training_data import loadTrainingData
from train_model import GaussianNaiveBayes, RandomForest, knn, svm
from predict import predict, getAccuracy_ConfMatrix
from postprocessing import createFrequencyMap
from ClipAndMask import clipRaster, maskWater

#These folders should exist in your wd 
input_folder = 'CapHaitienDownloadsApril2021' #Containing zip files with vv and vh Sentinel-1 data
DEM_folder = "./data/DEM"
human_settlement_folder = "GlobalHumanSettlement"
training_folder = "TrainingData" #Containing training data (check load_training_data for procedures)
waterbodies_folder = "./data/WaterBodies" #Containing a water bodies dataset


#These folders are created by the script:
masked_predictions_folder = 'FloodPredictions_masked'
images_folder = 'SentinelTimeSeries'
stacked_images_folder = 'SentinelTimeSeriesStacked'
waterbodies_name = "WaterBodiesCrop"
DEM_name = "DEMCrop"

# Open water and DEM names
water = "./data/WaterBodies/occurrence_10E_20Nv1_3_2020.tif" #Filename of raster file that includes the extents of the Sentinel-1 images
DEM = './data/DEM/2022-06-16-00_00_2022-06-16-23_59_DEM_MAPZEN_Topographic.tiff' #Filename of DEM that includes the extents of the Sentinel-1 images

# you can download tiff files with water bodies/DEM from ... 

#Indicate whether all images and histograms need to be plotted:
show_sentinel_histograms, show_sentinel_images = True, True

#Change your preferred model according to your preferences:
# Some models have additional parameters that can be adjusted to your liking
options = ["GaussianNaiveBayes", "RandomForest", "K-NearestNeighbours", "SupportVectorMachine"]
preferred_model = options[0] #Counting starts at zero !

## STEP 1: Load data
## Unzip images from the input_folder to the images_folder
## Stack vv and vh bands, together with the vv/vh ratio which is calculated by the function
load_data(input_folder, images_folder,stacked_images_folder, human_settlement_folder)
#This function stores all stacked rasters in the folder stacked_images_folder

## To be done: load a local subset of a global DEM and global water bodies dataset to aid in the classification
#Load DEM from a folder and crop to the extent of the radar image ...
## Crop the DEM to the same extent
DEMCrop = clipRaster(stacked_images_folder, DEM, DEM_folder, DEM_name)

# DEM will also have to be resampled so that it matches the radar images
#Load water bodies from a folder and crop to the extent of the radar image ...
clipRaster()


## STEP 2: Process data 
## If needed: speckle filter ... 
#list_of_images = apply_lee_filter(list_of_images, input_folder=images_folder, size = 5)


##Create crops of the water bodies dataset to the extent of each sentinel image
## NB it doesn't matter if the images referred to from stacked_rasters_names have different extents
water_sentinel_combis = clipRaster(stacked_images_folder, water, waterbodies_folder, waterbodies_name)




## To be done: also add DEM to the stacks


#Show some simple histograms and plot the images, if specified in line 40:
if show_sentinel_histograms:
    show_histograms(stacked_images_folder)

if show_sentinel_images:
    show_backscatter(stacked_images_folder)


##STEP 3: Load training data and train a supervised classification model
#Check load_training_data.py to check how the training folder should be structured
## To be done: use global DEM as fourth band to aid in the classification
X_train, X_test, y_train, y_test, training_polys = loadTrainingData(training_folder)

#Train a Gaussian Naive Bayes model
#And estimate test accuracy. A confusion matrix is shown to visualize the errors of the model
if preferred_model == "GaussianNaiveBayes":
    model = GaussianNaiveBayes(X_train,y_train)    

elif preferred_model == "RandomForest":
    model = RandomForest(X_train, y_train) #See train_model.py for additional parameters
    
elif preferred_model == "K-NearestNeighbours":
    model= knn(X_train, y_train)

elif preferred_model == "SupportVectorMachine":
    model = svm(X_train, y_train)    
    
else:
    raise Exception("Preferred model does not exist, please pick one of %s"%options)
    
test_acc, cm = getAccuracy_ConfMatrix(model,X_test, y_test)

#Predict flooded areas
## Classify each pixel of each image as flooded area, flooded urban area or dry area
## Either for one file (e.g. stacked_rasters_names[0]) or for all files in a list
# Set majorityfilter to True to apply majority filter (more accurate but takes a few minutes)
predictions_dict, predictions_filenames= predict(stacked_images_folder, model, training_polys, majorityfilter=False)

## predictions is a dictionairy containing a time series of classified maps
#Now mask the water bodies from each prediction
masked_predictions_names = maskWater(water_sentinel_combis,masked_predictions_folder,mask_value=100)

## STEP 3: Visualize Results
#show prediction results of one image (uncomment):
#visualizePrediction(prediction)
#show all prediction results:
visualizePrediction(masked_predictions_names, stacked_images_folder)


## STEP 4: Post processing
## Create a flood frequency map based on the time series
## How often is each pixel flooded?
## Create nice visualization
frequencymaps = createFrequencyMap(masked_predictions_names)
## Optionally: make animated map that shows classification for each time step in order
## to visualize flood extent over time