# # =============================================================================
# # STEP 7: REWRITE TIF NAMES WITH CORRECT DATES
# # =============================================================================
import rasterio as rio
import numpy as np
import os

def rewriteTIF(eopatch, file_name, vv_path, vh_path, dem_path):
    # Define data within eopatch and write to new list
    timestamp_date = eopatch['timestamp']
    timestamp = []
    for i in timestamp_date:
        timestamp.append(i.strftime("%Y-%m-%d"))
    
    # Open VV data, as well as metadata
    with rio.open(vv_path, 'r') as dst:
        vv_data = dst.read()
        vv_data = vv_data.astype(rio.float64)
        meta = dst.meta
        meta.update(count=4)
    
    # Open VH data
    with rio.open(vh_path, 'r') as dst:
        vh_data = dst.read()
        vh_data = vh_data.astype(rio.float32)
    
    # Open DEM data
    with rio.open(dem_path, 'r') as dst:
        dem = dst.read()
        
    
    # Calculate VV/VH ratio from VV and VH data
    #VV/VH ratio is calculated as VV/VH, since our data is measured on a linear scale
    vvvh_ratio = np.empty(vv_data.shape, dtype=rio.float64)
    vvvh_ratio = np.divide(vv_data, vh_data, out=np.zeros_like(vv_data), where = vh_data!=0)
    
    # Zip VV, VH, and VV/VH arrays together into one array
    stack = [[x]+[y]+[z] for x, y, z in zip(vv_data, vh_data, vvvh_ratio)]
    
    # Create SAR_data folder inside data folder
    if not os.path.exists(os.path.join('data', 'SAR_data')):
        os.makedirs(os.path.join('data', 'SAR_data'))
    
    names = []
    # Write arrays to tif based on their data
    for i in range(len(timestamp)):
        stack_filename="%s_vv_vh_vvvhratio_Stack.tiff"%timestamp[i]   
        stack_filepath= os.path.join('data', 'SAR_data', file_name, stack_filename)
        with rio.open(stack_filepath, "w",**meta) as dst:
            dst.write_band(1, stack[i][0])
            dst.write_band(2, stack[i][1])
            dst.write_band(3, stack[i][2])
            dst.write_band(4, dem[0])
            dst.descriptions = tuple(['VV','VH','VV/VH_ratio','DEM'])
            names.append(stack_filename)
    
    # Remove temporary VV and VH files
    os.remove(vv_path)
    os.remove(vh_path)
    os.remove(dem_path)

    return names
