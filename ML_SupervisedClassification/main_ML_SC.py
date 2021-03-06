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
    
## Please make sure that your current working directory is set to the parent
## directory of the project files,
## such that the variable stacked_images_folder refers to a valid path and a folder
## containing stacks of the Sentinel-1 images.
## These stacks os VV, VH and VV/VH-index are created by first running the script
## LoadAndStackSentinelData.py in the parent directory.
# =============================================================================
import os

from ML_SupervisedClassification.py.Visualize import show_backscatter, show_histograms, visualizePrediction, visualizeData
from ML_SupervisedClassification.py.LoadTrainingData import loadTrainingData
from ML_SupervisedClassification.py.TrainModel import GaussianNaiveBayes, RandomForest, knn, svm
from ML_SupervisedClassification.py.Predict import predict, getAccuracy_ConfMatrix
from ML_SupervisedClassification.py.CreateFrequencyMaps import createFrequencyMap
from ML_SupervisedClassification.py.ClipAndMask import clipRaster, maskWater
from ML_SupervisedClassification.py.LoadDEM_GHS import addDEM_GHS
from ML_SupervisedClassification.py.DifferenceFunction import diff_map
# =============================================================================
# Create folders and load file names
# These folders should exist in your wd 
stacked_images_folder = './data/SentinelTimeSeriesStacked' #Created by running LoadAndStackSentinelData.py
training_folder = "./data/TrainingDataHaiti" #Containing training data (check load_training_data for procedures)
ghs_folder = "./data/GHS_Haiti" #Containing a zipfile which has a tile of the GHS dataset
DEM_folder = "./data/DEM_Haiti" #Containg a DEM
waterbodies_folder = "./data/WaterBodiesHaiti" #Clips of the waterbodies dataset will be stored here
# These files should exist
#Filepath to a DEM tile that includes the extents of the Sentinel-1 images
DEM = "./data/DEM_Haiti/2022-06-16-00_00_2022-06-16-23_59_DEM_COPERNICUS_30__Grayscale.tiff"
#DEM = "./data/DEM_Chad/2022-06-16-00_00_2022-06-16-23_59_DEM_COPERNICUS_30__Grayscale.tiff"
#Filepath to a water bodies tile that includes the extents of the Sentinel-1 images
water = "./data/WaterBodiesHaiti/occurrence_80W_20Nv1_3_2020.tiff" 
#water = "./data/WaterBodiesChad/occurrence_10E_20Nv1_3_2020.tif"
# =============================================================================
# These names are used later to store the files
DEM_name = "DEMCrop"
waterbodies_name = "WaterBodiesCrop"
# =============================================================================
#These folders are created by the script:
    #Folders to store output files:
if not os.path.exists("./ML_SupervisedClassification/output"): os.makedirs("./ML_SupervisedClassification/output")
stacked_images_folder_incl_ghs='./ML_SupervisedClassification/output/SentinelTimeSeriesStacked_Incl_DEM_GHS'
predictions_folder = "./ML_SupervisedClassification/output/FloodPredictions"
masked_predictions_folder = './ML_SupervisedClassification/output/FloodPredictions_masked'        
output_folder = "./ML_SupervisedClassification/output/FloodingFrequencyRasters"
# =============================================================================
#When creating training data:
## Only run addDEM_GHS on a folder with a stack of vv, vh, and vv/vh-index
## and store the output image (which has five bands) in a training data folder
## See the file InstructionsForPreparations for instructions !
# =============================================================================
## Also consult the file InstructionsForPreparations for instructions 
## to see how to download data
## BE AWARE that some tiff files are stored as '.tif' and some as '.tiff'
# =============================================================================

#Indicate whether all images and histograms need to be plotted:
show_sentinel_histograms, show_sentinel_images = False, True




## STEP 1: Load data
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
#Create pairplot of training data
visualizeData(trainingdata)

#We recommed k-Nearest Neighbours: Run the other lines to explore other options
#The RF, KNN and SVM functions perform cross validation: 
    #find the results in the folder 'CV_Results' in 'data'
#model = GaussianNaiveBayes(trainingdata)   
model, results, best_params= knn(trainingdata)
#model, results, best_params = svm(trainingdata)  
#model, results, best_params = RandomForest(trainingdata) 

#Estimate test accuracy, user's accuracies and producer's accuracies.
#A confusion matrix is shown to visualize the errors of the model
test_acc, accuracies, cm = getAccuracy_ConfMatrix(model,testdata)




#STEP 3: Use a trained model to predict flooded pixels in each image
## Classify each pixel of each image as flooded area, flooded urban area or dry area
predict(stacked_images_folder_incl_ghs, predictions_folder, model, apply_sieve = True, sieve_size=25)

#Now mask the water bodies from each prediction
#First load local subsets of the water dataset, then use these to mask permanent water from the predictions
clipRaster(stacked_images_folder_incl_ghs, water, waterbodies_folder, waterbodies_name)
maskWater(predictions_folder, waterbodies_folder, masked_predictions_folder, mask_value=100)





## STEP 4: Visualize Results
#show all prediction results:
visualizePrediction(masked_predictions_folder, stacked_images_folder_incl_ghs)
## Create a flood frequency map based on the time series
## How often is each pixel flooded?
createFrequencyMap(masked_predictions_folder, output_folder)



## STEP 5: Create difference maps
## Create different maps of all consecutive sentinel-1 images
## The function uses the stacks created in STEP 1
## The polarization which is wanted to create difference map from has to be entered as well:
### Options are: 'vv', 'vh', and 'ratio'. If another string is entered, the 'vv' will be used.
## The threshold needs to be entered: everything above this threshold will be 1
## the remaining will be 0. This will visualise only the high backscatter
## All the data will be stored in a folder which will be created called "DifferenceMaps"
diff_map(stacked_images_folder_incl_ghs, 'vv', 0.5)








