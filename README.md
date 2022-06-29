# Flood risk assessment using time series analysis

**Project members**: Jakko-Jan van Ek, Julia Sipkema, Mark Boeve, Niels Verouden & Raimon Bach Pareja

**Coach**: Sytze de Bruin

**Commissioner**: S.M.J. Arts, Ministry of Defence

### Description
The aim of this exploratory research is to develop a model which examines spatial and temporal patterns of floods in flood prone areas. Several methods have been used: Machine Learning classification, Thresholding, Image Differencing and Urban backscatter analysis.

### Usage
- The report contains a detailed description of the materials, methods and results. In this way, somebody who perhaps has  less background knowledge of the data and techniques will also be able to understand the workflow. 
- The .yaml files contain all the packages that have to be installed (many others are in de standard python library already). Using e.g. the anaconda prompt a new environment can be created based on one of the .yaml files, after which the environment can be updated with the remaining .yaml files. Of course the packages can also be downloaded manually. The eo-learn package in the eo-learn.yaml file is the only package that is downloaded using pip instead of conda, as downloading it with conda did not seem to work properly. Note: if the Sentinel Hub package is not used, the eo-learn.yaml file can be disregarded. 
- The file 'InstructionsForPreparation' includes instructions to manually download SAR, human settlement, precipitation and DEM data and to create training polygons in ArcGIS.
- After downloading the data, the script 'LoadAndStackSentinelData' ought to be used as the first step as this contains the pre-processing of the SAR data. The output of this script can be used as input for the developed methods.
- An alternative for downloading the SAR data manually and using the 'LoadAndStackSentinelData' script is the main script in the eo-learn folder, which uses the Sentinel Hub API to download data. The output of this script can also be used as input for the methods.
- Please read the different main script of each folder carefully, as it may contain additional instructions. E.g. inserting names for input and output folders. 
- The files are structured in such a way that the functions are defined in different files, to further the readability. These files can contain additional explanation of how the functions work. 
