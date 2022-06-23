'''
||  POWER API SINGLE-POINT DOWNLOAD   ||
|| Version: 2.0 Published: 2021/03/09 ||

This is an overview of the process to request data from a single data point 
from the POWER API. The input parameters should be defined at step 1 (define
input parameters).

Source: https://power.larc.nasa.gov/
'''
import os
import requests
import csv
import datetime
import pandas as pd

def downloadClimateData(lon, lat, start, end, dest_name, time_interval):
    # =============================================================================
    #  STEP 1: DOWNLOAD DATA WITH POWER API
    # =============================================================================
    # Create directory
    if not os.path.exists(os.path.join('data',dest_name)):
        os.makedirs(os.path.join('data',dest_name))
    
    # Define start and end date
    start = datetime.datetime.strptime(start, '%Y-%m-%d')
    start = int(start.strftime("%Y%m%d"))
    end = datetime.datetime.strptime(end, '%Y-%m-%d')
    end = int(end.strftime("%Y%m%d"))

    # Define API url from parameters
    api_url = f"https://power.larc.nasa.gov/api/temporal/{time_interval}/point?parameters=WS10M,WD10M,T2MDEW,T2MWET,T2M,V10M,RH2M,PS,PRECTOT,QV2M,U10M&community=RE&longitude={lon}&latitude={lat}&start={start}&end={end}&format=CSV"

    # Download from api_url
    download = requests.Session().get(api_url)
    decoded_content = download.content.decode('utf-8')
    
    # Define file name    
    file_name = download.headers['content-disposition'].split('filename=')[1]
    file_name = file_name[0:35] +'.csv'
    # Read CSV file with line splitter
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    
    # Create path_name and open file
    path_name = os.path.join('data', dest_name, file_name)
    file = open(path_name, 'w+', newline ='')
    
    # Write CSV file to directory
    with file:   
        write = csv.writer(file)
        write.writerows(list(cr))

    # =============================================================================
    #  STEP 2: FILTER CLIMATE DATA AND RETURN PANDAS DATAFRAME
    # =============================================================================
    # Open the climate data
    climate_data = pd.read_csv(path_name, header = 19)
    
    # Keep only the year, month, day and precipitation data
    climate_data = climate_data[['YEAR','MO', 'DY', 'PRECTOTCORR']]

    # Create a new column for the dates
    climate_data[["date"]] = 0
    
    # Create for loop to create the date from the collumns "YEAR", "MO", and "DY"
    for i in range(0, len(climate_data[["YEAR"]])):
        
        year = climate_data.iat[i, 0] 
        month = climate_data.iat[i, 1]
        day = climate_data.iat[i, 2]
        
        a = datetime.datetime(year.astype(int), month.astype(int), day.astype(int))
        date = a.strftime('%Y-%m-%d')  
        
        climate_data.iat[i, 4] = date

    # Remove the columns "YEAR", "MO", and "DY"
    df_rain = climate_data[["PRECTOTCORR", "date"]]
    
    # =============================================================================
    # STEP 3: WRITE PD DATAFRAME TO CSV
    # =============================================================================
    # Create name for csv file based on dates, and write dataframe to csv file
    csv_name = os.path.join('data', dest_name, 'cleaned_'+file_name)
    df_rain.to_csv(csv_name, encoding='utf-8', index=False)
    
    ########
    # REMOVE OLD CSV FILE
    ########
    
    return df_rain