from rasterio.plot import show
import rasterio as rio
from rasterio.plot import show_hist
import matplotlib.pyplot as plt


def show_histograms(filenames):
    for id in range(0,15):
        title = str(filenames[id][-21:-11])
        with rio.open(filenames[id],'r',title=title) as src:
            #show(src)
            #print(src.meta)
            
            fig, axhist = plt.subplots(1, 1, figsize=(20, 20))
            show_hist(src, ax=axhist, bins=100, lw=0.0, stacked=False, 
                      alpha=0.3, histtype='stepfilled', density=True)
    
            axhist.set_title(title, size=60)
            axhist.legend(list(src.descriptions), prop={'size': 40})
            axhist.set_ylim([0,0.01])
            plt.show()
            #optional: add code to save histograms in a folder

def show_backscatter(filenames):
    for id in range(0,15):
        title = str(filenames[id][-21:-11])
        with rio.open(filenames[id],'r') as src:
            show(src,title=title, transform=src.transform)
            
         