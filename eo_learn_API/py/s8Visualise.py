# =============================================================================
# STEP 8: VISUALISE RESULTS
# =============================================================================
import rasterio as rio
from rasterio import plot
import matplotlib.pyplot as plt
import os

def visualiseResults(visualise, bands, names, file_name):
    for i in range(len(bands)):
        for x in range(len(names)):
            path_stacked = os.path.join('data', 'SAR_data', file_name, names[x])
            SAR = rio.open(path_stacked)
            SARi = SAR.read(i+1)
    
            date = names[x][0:10]
            fig, ax = plt.subplots(figsize=(10,10))
            rio.plot.show(SARi, ax=ax)
            plt.title(f'{bands[i]} {date}', fontdict={'fontsize': 20})
            plt.axis(False)
    
