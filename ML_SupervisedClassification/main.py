# =============================================================================
# MAIN.py
# =============================================================================
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
# =============================================================================
import os
from py.load_data_from_zip_folders import load_data
from py.visualize import show_backscatter, show_histograms, visualizePrediction, visualizeData
from py.load_training_data import loadTrainingData
from py.train_model import GaussianNaiveBayes, RandomForest, knn, svm
from py.predict import predict, getAccuracy_ConfMatrix
from py.postprocessing import createFrequencyMap
from py.ClipAndMask import clipRaster, maskWater
from py.loadDEM_GHS import addDEM_GHS
from py.diff_function import diff_map
# =============================================================================
# Create folders and load file names
# These folders should exist in your wd 
input_folder = './data/CapHaitienDownloadsFebruary2021' #Containing zip files with vv and vh Sentinel-1 data
training_folder = "./data/TrainingDataHaiti" #Containing training data (check load_training_data for procedures)
ghs_folder = "./data/GHS_Haiti" #Containing a zipfile which has a tile of the GHS dataset
DEM_filename = '2022-06-16-00_00_2022-06-16-23_59_DEM_COPERNICUS_30__Grayscale.tiff' #Filename of DEM that includes the extents of the Sentinel-1 images
DEM_folder = "./data/DEM_Haiti"
DEM = os.path.join(DEM_folder,DEM_filename)
DEM_name = "DEMCrop"
# =============================================================================
# These names are used later to store the files
waterbodies_folder = "./data/WaterBodies" #Containing a water bodies dataset
waterbodies_name = "WaterBodiesCrop"
water = "./data/WaterBodies/occurrence_80W_20Nv1_3_2020.tiff" #Filename of raster file that includes the extents of the Sentinel-1 images
# =============================================================================
#These folders are created by the script:
masked_predictions_folder = './data/FloodPredictions_masked'
images_folder = './data/SentinelTimeSeries'
stacked_images_folder = './data/SentinelTimeSeriesStacked'
stacked_images_folder_incl_ghs='./data/SentinelTimeSeriesStacked_Incl_DEM_GHS'
predictions_folder = "./data/FloodPredictions"
masked_predictions_folder = "./data/FloodPredictionsMasked"
output_folder = "./data/FloodingFrequencyRasters"
# =============================================================================
#When creating training data:
#input_folder="./data/ChadDownloadsNovember2020"
#ghs_folder="./data/GHS_Chad"
#DEM_folder="./data/DEM_Chad"

# =============================================================================
## For instructions on downloading data: refer to the file
## TimeSeriesFloodAnalysis_Instructions.pdf
## BE AWARE that some tiff files are stored as '.tif' and some as '.tiff'
# =============================================================================

#Indicate whether all images and histograms need to be plotted:
show_sentinel_histograms, show_sentinel_images = False, True




## STEP 1: Load data
## Unzip images from the input_folder to the images_folder
## Stack vv and vh bands, together with a vv/vh index which is calculated by the function
load_data(input_folder, images_folder,stacked_images_folder,lee=True)

#Append information from the DEM and GHS data to each raster stack
addDEM_GHS(stacked_images_folder, stacked_images_folder_incl_ghs, ghs_folder, DEM_folder)

#Show some simple histograms and plot the images, if specified in line 40:
if show_sentinel_histograms:
    show_histograms(stacked_images_folder_incl_ghs)

if show_sentinel_images:
    show_backscatter(stacked_images_folder_incl_ghs)




##STEP 2: Load training data and train a supervised classification model
#Check load_training_data.py to check how the training folder should be structured
trainingdata, testdata = loadTrainingData(training_folder)
#visualizeData(X_train, y_train)
#We recommed Random Forest: Run the other lines to explore other options
#The RF, KNN and SVM functions perform cross validation: 
    #find the results in the folder 'CV_Results' in 'data'
#model = GaussianNaiveBayes(trainingdata)   
model, results, best_params = RandomForest(trainingdata) 
#model, results, best_params= knn(trainingdata)
#model, results, best_params = svm(trainingdata)    
    
#Estimate test accuracy. A confusion matrix is shown to visualize the errors of the model
test_acc, accuracies, cm = getAccuracy_ConfMatrix(model,testdata)




#STEP 3: Use a trained model to predict flooded pixels in each image
## Classify each pixel of each image as flooded area, flooded urban area or dry area
predict(stacked_images_folder_incl_ghs, predictions_folder, model, apply_sieve = True, sieze_size=25)
# =============================================================================
#Now mask the water bodies from each prediction
#First load local subsets of the water dataset, then use these to mask permanent water from the predictions
clipRaster(stacked_images_folder_incl_ghs, water, waterbodies_folder, waterbodies_name)
maskWater(predictions_folder, waterbodies_folder, masked_predictions_folder, mask_value=100)
# =============================================================================




## STEP 4: Visualize Results
#show all prediction results:
visualizePrediction(masked_predictions_folder, stacked_images_folder_incl_ghs)
## Create a flood frequency map based on the time series
## How often is each pixel flooded?
frequencymaps= createFrequencyMap(masked_predictions_folder, output_folder)



## STEP 5: Create difference maps
## Create different maps of all consecutive sentinel-1 images
## The function uses the stacks created in STEP 1
## The polarization which is wanted to create difference map from has to be entered as well:
### Options are: 'vv', 'vh', and 'ratio'. If another string is entered, the 'vv' will be used.
## The threshold needs to be entered: everything above this threshold will be 1
## the remaining will be 0. This will visualise only the high backscatter
## All the data will be stored in a folder which will be created called "DifferenceMaps"
diff_freq_map = diff_map(stacked_images_folder_incl_ghs, 'vv', 0.5)

# Misschien nog een frequency map van maken???????????????????????????????????????
# Misschien stacken??????????????????????????????????????????????






