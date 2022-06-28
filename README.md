# ACT - Flood risk assessment using time series analysis

Project members: Jakko-Jan van Ek, Julia Sipkema, Mark Boeve, Niels Verouden & Raimon Bach Pareja

Coach: Sytze de Bruin

Commissioner: S.M.J. Arts, Ministry of Defence

## Description

The aim of this exploratory research is to develop a model which examines spatial and temporal patterns of floods in flood prone areas. Several methods have been used: Machine Learning classification, Thresholding, Image Differencing and Urban backscatter analysis. 

## Usage
The .yaml files contain all the packages that have been used. Using e.g. the anaconda prompt a new environment can be created based on one of these files, after which the environment can be updated with the remaining .yaml files. Of course the packages can also be downloaded manually. 

The file 'InstructionsForPreparation' includes instructions to manually download SAR, human settlement, precipitation and DEM data and to create training polygons in ArcGIS. 

After downloading the data, the script 'LoadAndStackSentinelData' ought to be used as the first step. The output of this script can be used as input for the developed methods. 

An alternative of using the 'LoadAndStackSentinelData' script is the main EoLearn script, which uses the Sentinel Hub API to download data. The output of this script can also be used as unput for the methods. 

 
