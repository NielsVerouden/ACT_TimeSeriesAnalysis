# This script investigates how a flooded urban area can be distinguished when 
# comparing sar images from e.g. multiple years

# =============================================================================
# IMPORTS
# =============================================================================

from matplotlib.pyplot import imshow

from rai_urban_functions import create_bbox
from rai_urban_functions import mask_urban
from rai_urban_functions import raster_to_polygon
from rai_urban_functions import clip_sar

# =============================================================================
# FOLDER AND FILE SETUP
# =============================================================================

sar_folder = 'input_los' # insert the name of the folder containing unzipped sar files
urban_raster = 'GHS_BUILT_LDSMT_GLOBE_R2018A_3857_30_V2_0_8_10.tif' # insert path to the downloaded urban raster
output_folder_mask = 'all_masked_urban' # insert path to output folder of masked urban rasters. If it does not exist, it will be created 
output_file_mask = 'masked_urban_haitien.tif' # insert name of output file of masked urban raster

# =============================================================================
# STEP 1: CREATE BOUNDING BOX AROUND URBAN AREA
# =============================================================================

# coordinates are in EPSG:3857, WGS 84 / Pseudo-Mercator. x = Easting (metre), y = Northing (metre)
bbox = create_bbox(-8047175.6823,2235485.5296,-8032958.3951,2247021.3680) # x min, y min, x max, y max

# =============================================================================
# STEP 2: MASK URBAN RASTER BY BBOX
# =============================================================================

masked_urban_raster = mask_urban(urban_raster, bbox, output_folder_mask, output_file_mask)
imshow(masked_urban_raster[0]) # for quick visualisation

# =============================================================================
# STEP 3: CONVERT MASKED RASTER TO POLYGON
# =============================================================================

masked_urban_pol = raster_to_polygon(output_folder_mask, output_file_mask)
masked_urban_pol.plot() # for quick visualisation

# =============================================================================
# STEP 4: CLIP POLYGON WITH SAR IMAGES
# =============================================================================

mean_urban_backscatter, dates = clip_sar(sar_folder, masked_urban_pol)

# =============================================================================
# STEP 5: VISUALISATION
# =============================================================================




sar = rio.open('EO/act-main-eo_learn_API/eo_learn_API/output/CapHaitien/2022-02-01_vv_vh_vvvhratio_Stack.tiff')
sar2 = sar.read(3)
imshow(sar2)


