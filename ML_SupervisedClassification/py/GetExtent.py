## Get extent of tiff file .
## Can be used if you want to add more  data from EO Browser.
## The geojson file that is exported to output_path can be used in EO browser
##   as the extent when downloading new files, to ensure that they have the same extent.


import rasterio as rio
import geopandas as gpd
from shapely.geometry import box
import os

def getExtent(filepath, output_path):
    with rio.open(filepath,"r") as src:
        #Get the bounds of the tiff file
        bounds=src.bounds
        
        #Create a geometry object of the bounds
        geom=box(*bounds)
        
        #Create a gpd geo dataframe based on the geometry
        geodf=gpd.GeoDataFrame({"id":1, "geometry":[geom]})
        
        #Export to geojson
        geodf.to_json()
        geodf.to_file(output_path, driver="GeoJSON")
        
    
#The following is an example:
inputpath=os.path.join('./data/TrainingDataChad/2020_11_02', #folder
                       'TrainingSentinel_2020_11_02.tiff')      #filename

outputpath=os.path.join('./data/TrainingDataChad/2020_11_02',       #folder
                        'bounds.geojson')                               #filename

getExtent(inputpath,outputpath)