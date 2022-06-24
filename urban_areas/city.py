import os
import rasterio as rio 
import geopandas as gpd
import fiona
import matplotlib.pyplot as plt
from rasterstats import zonal_stats
from rasterio import plot
from shapely.geometry import box, mapping
from speckle_filter import lee_filter
from thresholding import visualise

dest_name = 'input_los'

images = [tif for tif in os.listdir(dest_name) if '_VV_' in tif]
tifs = []
stats = []
for i in images:
    data = os.path.join(dest_name, i) # open and read tif files
    data2 = rio.open(data)
    data3 = data2.read(1)
    trans = data2.transform # to compute zonal statistics
    data3 = lee_filter(data3, 5) # apply speckle filter        
    tifs.append(data3)

visualise(tifs, 2, 3)

"""
bounds = data2.bounds
geom = box(*bounds)
df = gdp.GeoDataFrame({'id':1, 'geometry':[geom]})
df.to_file('bbox2.shp')
"""

# create city bbox
def bbox(left, bottom, right, top):
    city = [left, bottom, right, top]
    city_geom = box(*city)
    city_df = gpd.GeoDataFrame({'id':1, 'geometry':[city_geom]})
    city_df = city_df.set_crs('epsg:4326')
    return city_df

bbox = bbox(-72.202621,19.735209,-72.193866,19.743162)

# visually overlay raster and city bbox
fig, ax = plt.subplots(1, 1, figsize=(10,10))
p1 = rio.plot.show(data2, cmap='nipy_spectral', title='Band 1')
city_df.plot(ax=p1, color='red')
#fig.delaxes(ax=ax[1,1]) 

def zstats(tifs, bbox):
    stats = []
    for i in tifs:
        zstats = zonal_stats(bbox, i, affine = trans)
        stats.append(zstats)
    return stats

stats = zstats(tifs, bbox)  
    

"""
with rio.open('GHS_BUILT_LDSMT_GLOBE_R2018A_3857_30_V2_0_8_10.tif') as src:
    array = src.read(1)
    
    







































"""


#######################################################################################################
#######################################################################################################
#######################################################################################################

shp = gpd.read_file("bbox2.shp",crs='4326').drop('Atr',axis=1)

with rio.open('2022-02-01-00 00_2022-02-01-23 59_Sentinel-1_AWS-IW-VVVH_VV_-_decibel_gamma0_-_radiometric_terrain_corrected(1).tiff') as src:
    array = src.read(1)
    trans = src.transform
zstats = zonal_stats(city_df, array, affine=trans)





# create a Polygon from the raster bounds
bbox = box(*city)

# create a schema with no properties
schema = {'geometry': 'Polygon', 'properties': {}}

# create shapefile
with fiona.open('bbox.shp', 'w', driver='ESRI Shapefile',
                crs=data2.crs.to_dict(), schema=schema) as c:
    c.write({'geometry': mapping(bbox), 'properties': {}})
    
    
"""
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
