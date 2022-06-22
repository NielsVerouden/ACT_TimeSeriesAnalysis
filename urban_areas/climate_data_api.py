'''
//Version: 2.0 Published: 2021/03/09//

POWER API SINGLE-POINT DOWNLOAD
This is an overview of the process to request data from a single data point 
from the POWER API. The input parameters should be defined at step 1 (define
input parameters).

Source: https://power.larc.nasa.gov/
'''
# =============================================================================
# STEP 0: IMPORT PACKAGES
# =============================================================================
import os
import requests
import csv
import datetime

# =============================================================================
# STEP 1: DEFINE INPUT PARAMETERS
# =============================================================================
# Possible time intervals are hourly, daily, or monthly. The data is downloaded
# to the 'dest_name' folder in the 'data' folder. The standard dest_name is 
# climate_data, so data is stored in "./data/climate_date/___.csv".

longitude = -72.206768
latitude =  19.737036
start = '2020-01-01'
end = '2020-10-01'
dest_name = "climate_data"  
time_interval =  'daily'

# =============================================================================
# STEP 2: DEFINE URL AND CONVERT START AND END DATE
# =============================================================================
start = datetime.datetime.strptime(start, '%Y-%m-%d')
start = int(start.strftime("%Y%m%d"))

end = datetime.datetime.strptime(end, '%Y-%m-%d')
end = int(end.strftime("%Y%m%d"))

api_url = f"https://power.larc.nasa.gov/api/temporal/{time_interval}/point?parameters=WS10M,WD10M,T2MDEW,T2MWET,T2M,V10M,RH2M,PS,PRECTOT,QV2M,U10M&community=RE&longitude={longitude}&latitude={latitude}&start={start}&end={end}&format=CSV"

# =============================================================================
# STEP 1: DOWNLOAD CLIMATE DATA
# =============================================================================
def downloadClimateData (api_url, dest_name):
    # Create directory
    if not os.path.exists(os.path.join('data',dest_name)):
        os.makedirs(os.path.join('data',dest_name))
    # Download from api_url
    download = requests.Session().get(api_url)
    
    decoded_content = download.content.decode('utf-8')
    
    # Define file name    
    file_name = download.headers['content-disposition'].split('filename=')[1]
    
    # Read CSV file with line splitter
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    
    # Create path_name and open file
    path_name = os.path.join('data', dest_name, file_name)
    file = open(path_name, 'w+', newline ='')
    
    # Write CSV file to directory
    with file:   
        write = csv.writer(file)
        write.writerows(list(cr))

# Execute download climate data function
downloadClimateData(api_url, dest_name)
