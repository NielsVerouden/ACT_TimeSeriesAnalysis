# =============================================================================
# STEP 1: DOWNlOAD CLIMATE DATA WITH POWER API
# =============================================================================
'''
||  POWER API SINGLE-POINT DOWNLOAD   ||
|| Version: 2.0 Published: 2021/03/09 ||
|| Optimized for multi-point data     ||
This is an overview of the process to request data from a grid of data points
around a coordinate from the POWER API. The input parameters should be defined 
in the main script for downloading the climate data from the API.

Source: https://power.larc.nasa.gov/
'''
import os
import requests
import csv
import datetime
import geopandas as gpd
import rasterio as rio
from rasterio.plot import show
import matplotlib.pyplot as plt
from shapely.geometry import Point

def visualiseCoordinates(coordinates, grid, start, end, visualise, SAR_path):
    # Create directory
    if not os.path.exists(os.path.join('data', 'precipitation_data')):
        os.makedirs(os.path.join('data', 'precipitation_data'))

    # Define start and end date
    start = datetime.datetime.strptime(start, '%Y-%m-%d')
    start = int(start.strftime("%Y%m%d"))
    end = datetime.datetime.strptime(end, '%Y-%m-%d')
    end = int(end.strftime("%Y%m%d"))

    # Create a spacing based on the steps defined above
    minx, miny, maxx, maxy = coordinates
    x_spacing = ([maxx, maxy][0] - [minx, miny][0]) / (grid-1)
    y_spacing = ([maxx, maxy][1] - [minx, miny][1]) / (grid-1)

    # Assign the latitudes and longitudes to different lists
    latitudes = [[minx, miny][1] +  i * y_spacing for i in range(0, grid)]
    longitudes = [[minx, miny][0] + i * x_spacing for i in range(0, grid)]

    # Create list where all lat/lon combinations are stored
    coordinates_list = []

    # Make empty list where all requests should be stored
    request_list = []
    count = 1
    for lon in longitudes:
        for lat in latitudes: 
            # Define API url for each lon/lat combination, as well as the file name
            request = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=WS10M,WD10M,T2MDEW,T2MWET,T2M,V10M,RH2M,PS,PRECTOT,QV2M,U10M&community=RE&longitude={lon}&latitude={lat}&start={start}&end={end}&format=CSV"
            file_name = f'daily_{start}_{end}_loc{count}.CSV'
            # Append request names to list
            request_list.append((request, file_name))
            coordinates_list.append([lon, lat])
            count+=1
   
    ###### Visualise coordinates on SAR data
    if visualise == 'y':
        # Append geometry.Point objects to points list, for conversion to Geopandas DataFrame
        points = []
        for coordinates in coordinates_list:
            pnt = Point(coordinates[0], coordinates[1])
            points.append(pnt)
        
        # Create Geopandas DataFrame for the lat/lon combinations
        gdf = gpd.GeoDataFrame(geometry=points, crs=4326)
        
        # Define path to open the first SAR image
        path = os.path.join('data', 'SAR_data', SAR_path)
        files = os.listdir(path)
        file_path = os.path.join(path, files[0])
        
        # Open first SAR image in files
        src = rio.open(file_path)
        
        ## Plot results
        fig, ax = plt.subplots(figsize=(10, 10))
        # transform rasterio plot to real world coords
        extent=[src.bounds[0], src.bounds[2], src.bounds[1], src.bounds[3]]
        ax = rio.plot.show(src, extent=extent, ax=ax)
        gdf.plot(ax=ax, color='w', 
                 marker = 'o',
                 markersize=100)
        plt.title(f'VV {files[0][0:10]}', fontdict={'fontsize': 20})
        plt.axis(False)
    
    return coordinates_list, request_list

def climateDataAPI(request_list, start, end):
    # Define start and end date
    start = datetime.datetime.strptime(start, '%Y-%m-%d')
    start = int(start.strftime("%Y%m%d"))
    end = datetime.datetime.strptime(end, '%Y-%m-%d')
    end = int(end.strftime("%Y%m%d"))
    
    file_names= []
    for request in request_list:
        # Define API url and file_name for each request in request_list
        api_url, file_name = request
        
        # Append file_name to list
        file_names.append(file_name)
        
        # Download data from api_url
        download = requests.Session().get(api_url) 
        decoded_content = download.content.decode('utf-8')
    
        # Read CSV file with line splitter
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    
        # Create path_name and open file
        path_name = os.path.join('data', 'precipitation_data', file_name)
        file = open(path_name, 'w+', newline ='')
    
        # Write CSV file to directory
        with file:   
            write = csv.writer(file)
            write.writerows(list(cr))       
    
    return file_names
