"""
This script applies a simple thresholding method to a folder with downloaded SAR images
It is clearly inferior to the machine learning method but could still quickly give
an impression of the situation in a certain area. 
"""

# =============================================================================
# IMPORTS
# =============================================================================

from thresholding_functions import apply_thresholding
from thresholding_functions import show_stats
from thresholding_functions import visualise 

# =============================================================================
# FILE SETUP
# =============================================================================

folder_name = 'data/SentinelTimeSeriesStacked' # folder with unzipped, stacked and filtered SAR images

# =============================================================================
# STEP 1: APPLY THRESHOLDING
# =============================================================================

thresholding, images, dates = apply_thresholding(folder_name) 

# =============================================================================
# STEP 2: VISUALISE
# =============================================================================

show_stats(images[1])

visualise(thresholding, 2, 3, dates, 'Thresholding method') # 2 = nrows, 3 = ncols
