# =============================================================================
# STEP 4: CREATE AND SAVE TASKS
# =============================================================================
from eolearn.core import SaveTask, FeatureType, OutputTask, OverwritePermission
from eolearn.io import SentinelHubEvalscriptTask, SentinelHubDemTask
from sentinelhub import DataCollection, SHConfig
import os

def sentinelHubTasks(VV_script, VH_script, card4l_processing, time_difference, resolution, file_name):
    # Process API task to download VV data using evalscript
    # (VV and VH have a separate task which is more convenient when exporting data as tiff)   
    EO_SAR_VV = SentinelHubEvalscriptTask(
                    data_collection=DataCollection.SENTINEL1_IW,
                    features=[(FeatureType.DATA, 'VV')],
                    evalscript=VV_script,
                    resolution=resolution,
                    time_difference=time_difference,
                    aux_request_args={'processing': card4l_processing},
                    config=SHConfig(),
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
                    config=SHConfig(),
                    max_threads=3,
                    )
    
    # Adds DEM data to DATA_TIMELESS EOPatch feature.
    EO_DEM = SentinelHubDemTask(data_collection=DataCollection.DEM_COPERNICUS_30, 
                                resolution=resolution,
                                time_difference=time_difference,
                                config=SHConfig())
    
    path = os.path.join('data/', file_name)
    
    # Saves the given EOPatch to a filesystem
    save = SaveTask(path, overwrite_permission=OverwritePermission.OVERWRITE_FEATURES)
    
    # Stores data as an output of EOWorkflow results.
    output_task = OutputTask(path)
    
    return EO_SAR_VV, EO_SAR_VH, EO_DEM, save, output_task