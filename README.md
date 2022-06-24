# README ACT project - Flood risk assessment using time series analysis
Project for ACT module
Project members: Jakko-Jan van Ek, Julia Sipkema, Mark Boeve, Niels Verouden & Raimon Bach Pareja
Coach: Sytze de Bruin
Commissioner: S.M.J. Arts, Ministerie van Defensie

## Name
Flood risk assessment using time series analysis

## Description
#nog aanpassen met uiteindelijke executive summary

In recent years, climate change has become an important factor for conflict. 
Since the Dutch Ministry of Defence strives for a world of freedom and security, getting insight into flooding is highly valuable to the Ministry for proper planning of operations. 
Therefore, the main objective of this project is to create a globally applicable time series analysis method which analyses the spatial and temporal patterns of flood prone areas. 
Even though the analysis should work on a global scale, the project focuses on three different study areas. 
Ordered by their priority, these are 1). Haiti, 2). Suriname, and 3). Chad. 

This project explores opportunities and possibilities of applying remote sensing techniques to synthetic aperture radar (SAR) data to create a methodology of time series analysis for flood risk assessment. 
Since flood events are often characterised by persistent cloud cover, SAR data is used in our project since clouds do not obstruct radar signals. 
Hence, the analysis solely relies on Sentinel-1 data since this satellite captures SAR data on a global scale. 
Besides, a simple thresholding classifications is used to create flood frequency maps of the selected study areas. 
The outcome of this method consists of maps displaying the frequency of flooding, as well as a workflow report of the time series analysis. 
The team will use the MoSCoW method to assign four levels of priority to the different products defined in our project. 

## Visuals
#hier miss een plaatje van (een van) de uitkomsten?

## Installation
For this project an environment was made using anaconda. This is recommended for optimal running of the project.
If anaconda is not use, ensure that all the packages used in the project are downloaded correctly. 

For the project to run optimally all the data should be downloaded and stored properly and training data should be created (for the machine learnign models). 
For downloading the data using a script api_main.py in the folder eo_learn_API can be used. 
For information on downloading the data manually, how to store it and how to create the training data look in the file InstructionsForPreparation.pdf.

## Usage
Since the project is exploratory there are many different methods that were used and thus also many scripts. 
There are four folders with different scripts:
- ML_SupervisedClassification
- Thresholding
- eo_learn_API
- urban_areas
These all contain different parts of the project. 
The eo_learn_API contains a script to automatically download data. This should be used first. 
The other folders contain different methods for the time series analysis and thus should be used second. 
For more information about the different methods, their constraints and their advantages take a look at the report.  

## Contact information
#moeten we nog één van ons hier aanstellen als contact persoon voor het project?

## Roadmap
#misschien hier iets wat nog verbeterd of toegevoegd kan worden?

## Authors and acknowledgment
The five authors of this project are: Mark Boeve (manager), Julia Sipkema (controller), Jakko-Jan van Ek (secretary), Raimon Barch Pareja (team-member) and Niels Verouden (team-member). 

A special thanks to Stefan, our commissioner, Sytze, our coach, and Dainius, our expert, for helping and guiding us throughout the project. 

## Project status
IThis project has been finished on 28-06-2022


