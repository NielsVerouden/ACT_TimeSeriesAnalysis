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

def climateDataAPI(longitude, latitude, start, end):
    # Defines grid of lon/lat coordinates for which ppt data is downloaded. 
    # Either 3 or 4 is recommended
    steps = 3

    # Create directory
    if not os.path.exists(os.path.join('data', 'precipitation_data')):
        os.makedirs(os.path.join('data', 'precipitation_data'))
    
    # Define start and end date
    start = datetime.datetime.strptime(start, '%Y-%m-%d')
    start = int(start.strftime("%Y%m%d"))
    end = datetime.datetime.strptime(end, '%Y-%m-%d')
    end = int(end.strftime("%Y%m%d"))

    # Define boundingbox around given lon and lat
    minx, miny = ((i - 0.1) for i in (longitude, latitude))
    maxx, maxy = ((i + 0.1) for i in (longitude, latitude))
    
    # Create a spacing based on the steps defined above
    x_spacing = ([maxx, maxy][0] - [minx, miny][0]) / (steps + 1)
    y_spacing = ([maxx, maxy][1] - [minx, miny][1]) / (steps + 1)

    # Assign the latitudes and longitudes to different lists
    latitudes = [[minx, miny][1] +  i * y_spacing for i in range(1, steps+1)]
    longitudes = [[minx, miny][0] + i * x_spacing for i in range(1, steps+1)]

    # Create list where all lat/lon combinations are stored
    coordinates = []

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
            coordinates.append([lon, lat])
            count+=1
    
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
            
    return file_names, coordinates
