# =============================================================================
# IMPORTING AND CONFIGURATION
# =============================================================================
import matplotlib.pyplot as plt
import datetime
import numpy as np
import rasterio as rio

# SENTINELHUB AND EOLEARN PACKAGES
from sentinelhub import BBox, CRS, DataCollection, SHConfig
from eolearn.core import SaveTask, FeatureType, EOWorkflow, linearly_connect_tasks, OutputTask, OverwritePermission
from eolearn.io import SentinelHubEvalscriptTask, ExportToTiffTask, SentinelHubDemTask

# =============================================================================
# STEP 0: DEFINE PARAMETERS
# =============================================================================
INSTANCE_ID =   ''
CLIENT_ID =     ''
CLIENT_SECRET = ''

start = '2022-01-25'
end = '2022-02-10'
longitude = 19.749997
latitude = -72.1999992
zoom_level = 1
input_name = "inputname"
stack_dest_name = "stack_dest"
dest_name = "output"


# =============================================================================
# STEP 1: CONFIGURE SENTINELHUB SETTINGS
# =============================================================================
config = SHConfig()

if CLIENT_ID and CLIENT_SECRET and INSTANCE_ID:
    # An instance ID for Sentinel Hub service used for OGC requests.
    config.instance_id = INSTANCE_ID
    
    # User's OAuth client ID for Sentinel Hub service
    config.sh_client_id = CLIENT_ID
    
    # User's OAuth client secret for Sentinel Hub service
    config.sh_client_secret = CLIENT_SECRET
    config.save()
    
if config.sh_client_id == "" or config.sh_client_secret == "" or config.instance_id == "":
    print("Warning! To use Sentinel Hub services, please provide the credentials (client ID and client secret).")


# =============================================================================
# STEP 2: DEFINE INPUT
# =============================================================================
def id_search(script):
    # Select the name in evalscript after id
    id_all = script.partition('id:')[2]
    id_name = id_all.partition(',')[0]
    return id_name

def input_parameters(start, end, lon, lat, resolution):
    # Define interval between start and end
    time_interval = (start, end)
    
    # Time difference parameter (minimum allowed time difference; if two observations 
    # are closer than this, they will be mosaicked into one observation)
    time_difference = datetime.timedelta(days=1)

    # Define bbox around given coordinates
    min_x, min_y = (i - (0.5 * zoom_level)/10 for i in (lon, lat))
    max_x, max_y = (i + (0.5 * zoom_level)/10 for i in (lon, lat))
    coordinates = [min_y,min_x,max_y,max_x]
    boundBox = BBox(bbox = coordinates, crs = CRS.WGS84)    
    
    # resolution of the request, according to zoom_level (in metres)
    resolution = zoom_level * 5
    
    return time_interval, time_difference, boundBox, resolution

time_interval, time_difference, roi_bbox, resolution = input_parameters(start, end, longitude, latitude, zoom_level)

# =============================================================================
# STEP 3: DEFINE EVALSCRIPT AND PROCESSING SCRIPT
# =============================================================================
# An evalscript (or "custom script") is a piece of Javascript code which defines 
# how the satellite data shall be processed by Sentinel Hub and what values the 
# service shall return. In this case, only VV and VH are returned and processed
# according to the card4l processing standards: 
# https://forum.sentinel-hub.com/t/eo-learn-tutorial-documentation-for-preprocessing-sentinel-1-data/4695

def input_script():
    VV = """
        //VERSION=3
        function setup() {
          return {
            input: ["VV"],
            output: { 
                id:'VV', 
                bands: 1
                }
          }
        }
    function evaluatePixel(sample) {
        return [sample.VV];
    }    
    """
    VH = """
        //VERSION=3
        function setup() {
          return {
            input: ["VH"],
            output: { 
                id:'VH', 
                bands: 1
                }
          }
        }
    function evaluatePixel(sample) {
        return [sample.VH];
    }  
    """
    card4l_processing = {
        "backCoeff": "GAMMA0_TERRAIN",
        "orthorectify": True,
        "demInstance": "COPERNICUS",
        "downsampling": "BILINEAR",
        "upsampling": "BILINEAR",
        "speckleFilter": {
            "type": "LEE",
            "windowSizeX": 5,
            "windowSizeY": 5
            }
    }
    return VV, VH, card4l_processing

VV_script, VH_script, card4l_processing = input_script()

# =============================================================================
# STEP 4: CREATE AND SAVE TASKS
# =============================================================================
def sentinelHubTasks(VV_script, VH_script, card4l_processing, time_difference, resolution, dest_name, file_name):
    # Process API task to download VV data using evalscript
    # (VV and VH have a separate task which is more convenient when exporting data as tiff)
    EO_SAR_VV = SentinelHubEvalscriptTask(
                    data_collection=DataCollection.SENTINEL1_IW,
                    features=[(FeatureType.DATA, 'VV')],
                    evalscript=VV_script,
                    resolution=resolution,
                    time_difference=time_difference,
                    aux_request_args={'processing': card4l_processing},
                    config=config,
                    max_threads=3,
                    )
    
    # Process API task to download VH data using evalscript
    EO_SAR_VH = SentinelHubEvalscriptTask(
                    data_collection=DataCollection.SENTINEL1_IW,
                    features=[(FeatureType.DATA, 'VH')],
                    evalscript=VH_script,
                    resolution=resolution,
                    time_difference=time_difference,
                    aux_request_args={'processing': card4l_processing},
                    config=config,
                    max_threads=3,
                    )
    
    # Adds DEM data to DATA_TIMELESS EOPatch feature.
    EO_DEM = SentinelHubDemTask(data_collection=DataCollection.DEM_COPERNICUS_30, 
                                resolution=resolution,
                                time_difference=time_difference,
                                config=config)
    
    # Saves the given EOPatch to a filesystem
    save = SaveTask(dest_name, overwrite_permission=OverwritePermission.OVERWRITE_FEATURES)
    
    # Stores data as an output of EOWorkflow results.
    output_task = OutputTask(file_name)
    
    return EO_SAR_VV, EO_SAR_VH, EO_DEM, save, output_task

EO_SAR_VV, EO_SAR_VH, EO_DEM, save, output_task = sentinelHubTasks(VV_script, VH_script, card4l_processing, time_difference, resolution, dest_name, dest_name)
# =============================================================================
# STEP 5: RUN WORKFLOW
# =============================================================================
def workflow(time_interval, filename):
    # Creates a list of linearly linked nodes, suitable to construct an EOWorkflow.
    workflow_nodes = linearly_connect_tasks(EO_SAR_VV,
                                            EO_SAR_VH,
                                            EO_DEM,
                                            save, 
                                            output_task)
    # Verifying and executing workflows defined by inter-dependent EONodes.
    workflow = EOWorkflow(workflow_nodes)

    # Execute all tasks defines in the workflow_nodes
    result = workflow.execute(
        {
            workflow_nodes[0]: {"bbox": roi_bbox, "time_interval": time_interval},
            workflow_nodes[-2]: {"eopatch_folder": dest_name},
        }
    )
    # write output to eopatch variable
    eopatch = result.outputs[dest_name]
    
    return eopatch

eopatch = workflow(time_interval, dest_name)

# =============================================================================
# STEP 6: WRITE RESULTS TO FILESYSTEM
# =============================================================================
def exportResults(eopatch, dest_name):
    # Task exports specified feature to Geo-Tiff
    # Task to export VV to dest_name/file_name
    export_VV = ExportToTiffTask((FeatureType.DATA, 'VV'),
                                    folder="Output/VV",
                                    compress=None)
    
    # Task to export VH to dest_name/file_name
    export_VH = ExportToTiffTask((FeatureType.DATA, 'VH'),
                                    folder="Output/VH",
                                    compress=None)
    
    # Task to export DEM to dest_name/file_name
    export_DEM = ExportToTiffTask((FeatureType.DATA_TIMELESS, "dem"),
                                    folder="Output/DEM",
                                    compress=None)
    
    # Execute export tasks
    export_VV.execute(eopatch)
    export_VH.execute(eopatch)
    export_DEM.execute(eopatch)

exportResults(eopatch, dest_name)

# # =============================================================================
# # STEP 7: REWRITE TIF NAMES WITH CORRECT DATES
# # =============================================================================
# METADATA
timestamp_date = eopatch['timestamp']
timestamp_str = []

for i in timestamp_date:
    timestamp_str.append(i.strftime("%Y-%m-%d-%H:%M"))

vv_data = "Output/VV.tif"
vh_data = "Output/VH.tif"
DEM = "Output/DEM.tif"

with rio.open(vv_data, 'r') as dst:
    vv_data = dst.read()
    vv_data = vv_data.astype(rio.float32)
    meta = dst.meta
    # meta.update()

with rio.open(vh_data, 'r') as dst:
    vh_data = dst.read()
    vh_data = vh_data.astype(rio.float32)

with rio.open(DEM, 'r') as dst:
    DEM = dst.read()
    DEM = DEM.astype(rio.float32)

vvvh_ratio = np.empty(vv_data.shape, dtype=rio.float32)
  
#VV/VH ratio is calculated as VV/VH, since our data is measured on a linear scale
vvvh_ratio = np.divide(vv_data, vh_data, out=np.zeros_like(vv_data), where = vh_data!=0)

stack = [[x]+[y]+[z] for x, y, z in zip(vv_data, vh_data, vvvh_ratio)]

meta.update(count=3)

# for date in timestamp_str:
#     stack_filename=f"{date}_vv_vh_vvvhratio_Stack.tiff"    
    
# stack_filepath='output/stack_filename'

# with rio.open(stack_filepath, "w",**meta) as dst:
#     dst.write_band(1,vv_data)
#     dst.write_band(2,vh_data)
#     dst.write_band(3,vvvh_ratio)
#     dst.descriptions = tuple(['VV','VH','VV/VH_ratio'])


plt.imshow(vv_data[0])
plt.axis(False)
plt.show()

plt.imshow(vh_data[0])
plt.axis(False)
plt.show()

plt.imshow(vvvh_ratio[0])
plt.axis(False)
plt.show()

""" 
TO DO -->
- Check if data from eo learn is in gamma (not linear)
- Export tif files as "%Y-%m-%d-%H:%M" for each date (vv, vh, vv/vh ratio)    

"""
