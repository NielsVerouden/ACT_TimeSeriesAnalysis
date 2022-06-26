# =============================================================================
# STEP 2: DEFINE INPUT PARAMETERS
# =============================================================================
import datetime
from sentinelhub import BBox, CRS

def inputParameters(start, end, coordinates):
    # Define interval between start and end
    time_interval = (start, end)
    
    # Time difference parameter (minimum allowed time difference; if two observations 
    # are closer than this, they will be mosaicked into one observation)
    time_difference = datetime.timedelta(days=1)

    # Define bbox around given coordinates
    [min_y,min_x,max_y,max_x] = coordinates
    bbox = BBox(bbox = coordinates, crs = CRS.WGS84)

    return time_interval, time_difference, bbox