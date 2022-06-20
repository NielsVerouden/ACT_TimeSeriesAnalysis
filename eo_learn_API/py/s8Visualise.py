# =============================================================================
# STEP 8: VISUALISE RESULTS
# =============================================================================
import rasterio as rio
import matplotlib.pyplot as plt
import os

def visualiseResults(visualise, bands, names, dest_name, file_name):
    # Plot individually
    # if visualise == "y":
    #     for name in names:
    #         for i in range(len(bands)):
    #             eo = os.path.join(dest_name, file_name, name)
    #             with rio.open(eo, 'r') as dst:
    #                 eo_stack = dst.read()
    #                 eo_stack = eo_stack.astype(rio.float64)
                
    #             plt.imshow(eo_stack[i])
    #             plt.title(name[0:10]+f' ({bands[i]})', fontdict={'fontsize': 8,
    #                                       'fontweight' : 8})
    #             plt.axis(False)
    #             plt.show()

    if visualise == "y":
        for i in range(len(bands)):
            for name in names:
                eo = os.path.join(dest_name, file_name, name)
                with rio.open(eo, 'r') as dst:
                    eo_stack = dst.read()
                    eo_stack = eo_stack.astype(rio.float64)
                
                plt.imshow(eo_stack[i])
                plt.title(name[0:10]+f' ({bands[i]})', fontdict={'fontsize': 8,
                                          'fontweight' : 8})
                plt.axis(False)
                plt.show()            
    # Plot bands together
    # if visualise == "y":
