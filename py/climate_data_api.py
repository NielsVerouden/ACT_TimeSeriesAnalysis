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
import time
import os
import requests
import csv
import datetime
import pandas as pd

start_time = time.time()

# =============================================================================
# STEP 1: DEFINE INPUT PARAMETERS
# =============================================================================
# Possible time intervals are hourly, daily, or monthly. The data is downloaded
# to the 'dest_name' folder in the 'data' folder. The standard dest_name is 
# climate_data, so data is stored in "./data/climate_date/___.csv".

# Input parameters: EXAMPLE
longitude = -72.206768
latitude =  19.737036
start = '2020-01-01'
end = '2022-04-25'
dest_name = "climate_data"  
time_interval =  'daily'




# =============================================================================
# STEP 1: DOWNLOAD CLIMATE DATA
# =============================================================================
def downloadClimateData (longitude, latitude, start, end, dest_name, time_interval):
    
    # Create the api_url to download the data
    api_url = f"https://power.larc.nasa.gov/api/temporal/{time_interval}/point?parameters=WS10M,WD10M,T2MDEW,T2MWET,T2M,V10M,RH2M,PS,PRECTOT,QV2M,U10M&community=RE&longitude={longitude}&latitude={latitude}&start={start}&end={end}&format=CSV"

    # =============================================================================
    # STEP 2: DEFINE URL AND CONVERT START AND END DATE
    # =============================================================================
    start = datetime.datetime.strptime(start, '%Y-%m-%d')
    start = int(start.strftime("%Y%m%d"))

    end = datetime.datetime.strptime(end, '%Y-%m-%d')
    end = int(end.strftime("%Y%m%d"))
    
    
    # Create directory
    if not os.path.exists(os.path.join('data',dest_name)):
        os.makedirs(os.path.join('data',dest_name))
        
    # Create link to directory
    ## This will be used in the functionget_climate_data as input
    climate_data_folder = os.path.join('data', dest_name)
    
    # Download from api_url
    download = requests.Session().get(api_url)
    
    decoded_content = download.content.decode('utf-8')
    
    # Define file name    
    file_name = download.headers['content-disposition'].split('filename=')[1]
    file_name = file_name[0:35]+'.csv'
    
    # Read CSV file with line splitter
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    
    # Create path_name and open file
    path_name = os.path.join('data', dest_name, file_name)
    file = open(path_name, 'w+', newline ='')
    
    # Write CSV file to directory
    with file:   
        write = csv.writer(file)
        write.writerows(list(cr))
    return(climate_data_folder)

# Execute download climate data function
#cl_dat_fol = downloadClimateData(api_url, dest_name)
#print(f"----- {round((time.time() - start_time), 2)} seconds -----")





def get_climate_data(input_folder):

    # Check all the files in the list
    list_files = os.listdir(input_folder)

    # Create the directory of the file
    open_file = os.path.join(input_folder, list_files[0])
    
    # Open the climate data
    climate_data = pd.read_csv(open_file, header = 19)
    
    # Keep only the year, month, day and precipitation data
    climate_data = climate_data[['YEAR','MO', 'DY', 'PRECTOTCORR']]
    
    # Change the name "PRECTOTCORR" to "prec"
    climate_data[["prec"]] = climate_data[["PRECTOTCORR"]]
    
    # Create a new column for the dates
    climate_data[["date"]] = 0
    
    # Create for loop to create the date from the collumns "YEAR", "MO", and "DY"
    for i in range(0, len(climate_data[["YEAR"]])):
        
        year = climate_data.iat[i, 0] 
        month = climate_data.iat[i, 1]
        day = climate_data.iat[i, 2]
        
        a = datetime.datetime(year.astype(int), month.astype(int), day.astype(int))
        date = a.strftime('%Y-%m-%d')  
        
        
        climate_data.iat[i, 5] = date

    # Remove the columns "YEAR", "MO", and "DY"
    climate_data = climate_data[["prec", "date"]]
    return(climate_data)







