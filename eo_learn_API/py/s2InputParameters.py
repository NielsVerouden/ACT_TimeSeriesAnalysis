# =============================================================================
# STEP 2: DEFINE INPUT PARAMETERS
# =============================================================================
import datetime
from sentinelhub import BBox, CRS

def inputParameters(start, end, lat, lon, zoom):
    # Define interval between start and end
    time_interval = (start, end)
    
    # Time difference parameter (minimum allowed time difference; if two observations 
    # are closer than this, they will be mosaicked into one observation)
    time_difference = datetime.timedelta(days=1)

    # Define bbox around given coordinates
    min_x, min_y = (i - (0.5 * zoom)/10 for i in (lon, lat))
    max_x, max_y = (i + (0.5 * zoom)/10 for i in (lon, lat))
    coordinates = [min_y,min_x,max_y,max_x]
    boundBox = BBox(bbox = coordinates, crs = CRS.WGS84)
    
    # resolution of the request, according to zoom_level (in metres)
    resolution = zoom * 5       # 5 is the lowest one can go (otherwise request will give an error)
    
    return time_interval, time_difference, boundBox, resolution