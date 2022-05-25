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
## The images_folder is automatically created by the script if it is not yet present in the 
## current working directory.

from load_data_from_zip_folders import load_data
from load_images import load_images
from stack_images import stack_images

input_folder = 'sentinelhub_downloads'
images_folder = 'radar_time_series'
stacked_images_folder = 'radar_time_series_stacked'
## STEP 1: Load data
## Unzip images from the input_folder to the images_folder
list_of_images = load_data(dir_name=input_folder, dest_name = images_folder)
#This function returns a list of image names and stores all images with those names in a folder

## Load images from the images_folder as rasterio dataset readers
rasters = load_images(list_of_images, dest_name = images_folder)

## Optionally: load a local subset of a global DEM and global water bodies dataset to aid in the classification



## STEP 2: Process data 
## If needed: speckle filter ... 

## Create for each date in the time series a stack of VV, VH and VV/VH ratio images
stacked_rasters = stack_images(list_of_images, rasters, input_name=images_folder, output_name=stacked_images_folder)
## Classify each pixel for each image as open water, flooded area or dry area
## Optionally: use global water bodies dataset to mask open water
## OPtionally: use global DEM to aid in the classification
## Return a time series of classified maps

## STEP 3: Visualize Results
## Create a flood frequency map based on the time series
## Create nice visualization
## Optionally: make animated map that shows classification for each time step in order
## to visualize flood extent over time










