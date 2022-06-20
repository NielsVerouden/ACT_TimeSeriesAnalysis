import time
start_time = time.time()

# =============================================================================
# IMPORT FUNCTIONS
# =============================================================================
from py.s1Configuration import configSentinelHub
from py.s2InputParameters import inputParameters
from py.s3Evalscripts import inputEvalscripts
from py.s4SentinelHubTasks import sentinelHubTasks
from py.s5ExecuteTasks import executeWorkflow
from py.s6ExportResults import exportResults
from py.s7RewriteTIF import rewriteTIF
from py.s8Visualise import visualiseResults

# =============================================================================
# DEFINE PARAMETERS
# =============================================================================
INSTANCE_ID =   'e08dbb9f-9ec4-4a81-ae2c-ae31d9ccd4f6'
CLIENT_ID =     'fa722f2a-4dec-487e-aebd-16a03646379a'
CLIENT_SECRET = ']GsJ)JrZ<s:iXxK4KerK{vfvG-e;_3TB[eXIX+8,'

start = '2021-06-01'
end = '2021-09-01'
longitude = 15.815437
latitude =  9.330509
zoom = 5
file_name = "Chad_Tandjile_JunJulAug2021"
dest_name = "output"

# Visualise results (y/n)? And if so, which band(s) (VV, VH, VVVH)?
visualize = "y"
bands = ["VV", "VH"]

# =============================================================================
# EXECUTE STEPS
# =============================================================================
# STEP 1: CONFIGURE SENTINELHUB SETTINGS
configSentinelHub(CLIENT_ID, CLIENT_SECRET, INSTANCE_ID)

# STEP 2: DEFINE INPUT PARAMETERS
time_interval, time_difference, roi_bbox, resolution = inputParameters(start, end, longitude, latitude, zoom)

# STEP 3: DEFINE EVALSCRIPT AND PROCESSING SCRIPT
VV_script, VH_script, card4l_processing = inputEvalscripts()

# STEP 4: CREATE AND SAVE TASKS
tasks = sentinelHubTasks(VV_script, VH_script, card4l_processing, time_difference, resolution, file_name)

# STEP 5: RUN WORKFLOW
eopatch = executeWorkflow(time_interval, file_name, tasks, roi_bbox)

# STEP 6: WRITE RESULTS TO FILESYSTEM
vv_path, vh_path, dem_path = exportResults(eopatch, file_name, dest_name)

# STEP 7: REWRITE TIF NAMES WITH CORRECT DATES
names = rewriteTIF(eopatch, dest_name, file_name, vv_path, vh_path, dem_path)

# STEP 8: VISUALISE RESULTS
visualiseResults(visualize, bands, names, dest_name, file_name)


print("--- %s seconds ---" % (time.time() - start_time))
