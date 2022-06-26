# =============================================================================
# STEP 6: WRITE RESULTS TO FILESYSTEM
# =============================================================================
from eolearn.io import ExportToTiffTask
from eolearn.core import FeatureType

def exportResults(eopatch, file_name):
    # Define export paths
    vv_path = 'data/SAR_data/'+file_name+"/VV_temp.tif"
    vh_path = 'data/SAR_data/'+file_name+"/VH_temp.tif"
    dem_path = 'data/SAR_data/'+file_name+"/DEM_temp.tif"
    
    # Task exports specified feature to Geo-Tiff
    # Task to export VV to dest_name/file_name
    export_VV = ExportToTiffTask((FeatureType.DATA, 'VV'),
                                    folder=vv_path,
                                    compress=None,
                                    image_dtype='float32')
    
    # Task to export VH to dest_name/file_name
    export_VH = ExportToTiffTask((FeatureType.DATA, 'VH'),
                                    folder=vh_path,
                                    compress=None, 
                                    image_dtype='float32')
    
    # Task to export DEM to dest_name/file_name
    export_DEM = ExportToTiffTask((FeatureType.DATA_TIMELESS, "dem"),
                                    folder=dem_path,
                                    compress=None,
                                    image_dtype='float32')
    
    # Execute export tasks
    export_VV.execute(eopatch)
    export_VH.execute(eopatch)
    export_DEM.execute(eopatch)
 
    return vv_path, vh_path, dem_path