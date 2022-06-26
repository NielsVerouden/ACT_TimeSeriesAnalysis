import time
start_time = time.time()
# =============================================================================
# INFORMATION ABOUT THE SCRIPT
# =============================================================================
"""
_______________________________________________________________________________

INFO:
This script contains an API to download Synthetic Aperture Radar (SAR) from the 
Sentinel-1 constellation with the eo-learn package. Eo-learn is a collection of 
open source Python packages that have been developed to seamlessly access and 
process spatio-temporal image sequences acquired by any satellite fleet in a timely 
and automatic manner. This script has been optimized to download SAR data (VV and VH)
between two dates for a given boundingbox. The VV and VH for each date are stacked,
together with the VV/VH ratio and the DEM, and saved as .tif files to your directory
according to the dest_name variable ('data/SAR_data/dest_name/___.tif'). SAR DATA is
processed according to the CARD4L processing standards. 

PARAMETERS:
The first parameters that should be defined are INSTANCE_ID, CLIENT_ID, and 
CLIENT_SECTRET. For more information, see file 'downloadInstructionsEOLearn.pdf'.
SAR data is downloaded between the start and end date, which should be defined
in the format 'yyyy-mm-dd'. However, EO Learn API has a download rate of 100 images/hr
so downloading SAR images for several years at once is not possible with this script. 
!!!HENCE, DOWNLOAD IMAGES OF MAX. 10 MONTHS AT ONCE TO PREVENT API FROM CRASHING!!!

The coordinates variable accepts a tuple of coordinates in the following order: 
xmin, ymin, xmax, ymax. The bbox can easily be downloaded from http://bboxfinder.com/. 
If you download from this website, simply draw a polgon around the area of interest 
with "Draw a polyline" tool, and copy-paste the coordinates from row "Box" at the 
bottom of the webpage. 

Furthermore, the destination name of the data should be defined. In this example,
the start and end date are respectively 2021-01-01 and 2021-07-01, and the 
coordinates are selected around the city of Cap-Haïtien (Haïti). Hence, the
dest_name variable has been set to "CapHaitien_Jan2021Jul2021". It is recommended 
to keep the same structured as shown in this folder.

The resolution variable corresponds to the resolution of the pixels of the SAR
data. A lower pixel size results in a higher the resolution but also larger file
sizes. For instance, a bbox with a circumference of 70km and a resolution set to
'15' result in tif files with a single tif file size of ~20MB, whereas a resolution
set to '8' result in tif files with size ~75MB. (To find the lowest resolution 
possible for the bbox, set the resolution to 1 and keep increasing the variable 
with increments of 1 until the error 'DownloadFailedException' is not raised 
anymore). 

Finally, plotting the SAR images is possible when setting visualise to 'y' instead
of 'n'. Moreover, the bands should be defined as a list. Possible bands are VV, VH, 
VVVH, and DEM. Plotting all bands for all images may take some time. Not advisable 
if you download 20+ images. 
_______________________________________________________________________________

Source: https://eo-learn.readthedocs.io/en/latest/
_______________________________________________________________________________
"""

# =============================================================================
# IMPORT FUNCTIONS
# =============================================================================
from eo_learn.py.s1Configuration import configSentinelHub
from eo_learn.py.s2InputParameters import inputParameters
from eo_learn.py.s3Evalscripts import inputEvalscripts
from eo_learn.py.s4SentinelHubTasks import sentinelHubTasks
from eo_learn.py.s5ExecuteTasks import executeWorkflow
from eo_learn.py.s6ExportResults import exportResults
from eo_learn.py.s7RewriteTIF import rewriteTIF
from eo_learn.py.s8Visualise import visualiseResults

# =============================================================================
# DEFINE PARAMETERS
# =============================================================================
INSTANCE_ID =   'e08dbb9f-9ec4-4a81-ae2c-ae31d9ccd4f6'
CLIENT_ID =     'fa722f2a-4dec-487e-aebd-16a03646379a'
CLIENT_SECRET = ']GsJ)JrZ<s:iXxK4KerK{vfvG-e;_3TB[eXIX+8,'

start = '2021-01-01'
end = '2021-07-31'
coordinates = (-72.304390,19.668729,-72.112816,19.805822)
dest_name = "CapHaitien_Jan2021Jul2021"
resolution = 10

# Visualise results (y/n)? And if so, which band(s) (VV, VH, VVVH, DEM)?
visualise = "y"
bands = ["VV"]

# =============================================================================
# EXECUTE STEPS
# =============================================================================
# STEP 1: CONFIGURE SENTINELHUB SETTINGS
configSentinelHub(CLIENT_ID, CLIENT_SECRET, INSTANCE_ID)

# STEP 2: DEFINE INPUT PARAMETERS
time_interval, time_difference, bbox = inputParameters(start, end, coordinates)

# STEP 3: DEFINE EVALSCRIPT AND PROCESSING SCRIPT
VV_script, VH_script, card4l_processing = inputEvalscripts()

# STEP 4: CREATE AND SAVE TASKS
tasks = sentinelHubTasks(VV_script, VH_script, card4l_processing, time_difference, resolution, dest_name)

# STEP 5: RUN WORKFLOW
eopatch = executeWorkflow(time_interval, dest_name, tasks, bbox)

# STEP 6: WRITE RESULTS TO FILESYSTEM
vv_path, vh_path, dem_path = exportResults(eopatch, dest_name)

# STEP 7: REWRITE TIF NAMES WITH CORRECT DATES
names = rewriteTIF(eopatch, dest_name, vv_path, vh_path, dem_path)

# STEP 8: VISUALISE RESULTS
visualiseResults(visualise, bands, names, dest_name)


print("--- %s seconds ---" % (time.time() - start_time))
