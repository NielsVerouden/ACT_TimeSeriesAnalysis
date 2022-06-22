'''
*Version: 2.0 Published: 2021/03/09* Source: [NASA POWER](https://power.larc.nasa.gov/)
POWER API Multi-Point Download
This is an overview of the process to request data from multiple data points from the POWER API.
Edited by Niels Verouden
'''

##### Import packages #####
import os, json, requests, csv


##### Define parameters #####
locations =      [(19.73736, -72.206768 )]       # Can define single or multiple points (lat, lon)
start =          20220101                    # Start data (yyyyMMdd)
end =            20220501                    # End date (yyyyMMdd)
output =         r"./Data/climate_data"      # Define folder where data is saved
time_interval =  'daily'                     # hourly, daily, or monthly. Default is monthly
file_format =    'CSV'                       # Format of file, CSV or JSON

# Create output folder if it has not been created yet
output_location = './data/climate_data'

if not os.path.exists(output_location):
    os.mkdir(output_location)

##### Define base_url based on time_interval #####
if time_interval == 'hourly':
    base_url = r'https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=WS10M,WD10M,T2MDEW,T2MWET,T2M,V10M,RH2M,PS,PRECTOT,QV2M,U10M&community=RE&longitude={longitude}&latitude={latitude}&start={start}&end={end}&format={file_format}'
    
elif time_interval == 'daily':
    base_url = r"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=WS10M,WD10M,T2MDEW,T2MWET,T2M,V10M,RH2M,PS,PRECTOT,QV2M,U10M&community=RE&longitude={longitude}&latitude={latitude}&start={start}&end={end}&format={file_format}"

else:
    start = int(str(start)[0:4])
    end = int(str(end)[0:4])
    base_url = r"https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=WS10M,WD10M,T2MDEW,T2MWET,T2M,V10M,RH2M,PS,PRECTOT,QV2M,U10M&community=RE&longitude={longitude}&latitude={latitude}&start={start}&end={end}&format={file_format}"

##### Define message if download is successful or not
success = '{time_int} data .{fformat} has been downloaded'.format(time_int = time_interval, fformat = file_format)
fail = "File format .{fformat} not supported, choose either CSV or JSON".format(fformat = file_format)

##### Download climate data based on predefined parameters #####
for latitude, longitude in locations:
    api_request_url = base_url.format(longitude=longitude, latitude=latitude, start=start, end=end, file_format=file_format) 
    
    # Download data as CSV
    if file_format == "CSV":
        
        with requests.Session() as s:
            download = s.get(api_request_url)
        
            decoded_content = download.content.decode('utf-8')
            
            filename = download.headers['content-disposition'].split('filename=')[1]
    
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
           
            my_list = list(cr)
            
            file = open(output+'/'+filename, 'w+', newline ='')
    
            with file:   
                write = csv.writer(file)
                write.writerows(my_list)
        
        print(success)
    
    # Download data as JSON 
    elif file_format == "JSON":
        response = requests.get(url=api_request_url, verify=True, timeout=30.00)

        content = json.loads(response.content.decode('utf-8'))
        filename = response.headers['content-disposition'].split('filename=')[1]

        filepath = os.path.join(output, filename)
        
        with open(filepath, 'w') as file_object:
            json.dump(content, file_object)
        
        print(time_interval+' data .'+file_format+' has been downloaded')

    else:
        print(fail)