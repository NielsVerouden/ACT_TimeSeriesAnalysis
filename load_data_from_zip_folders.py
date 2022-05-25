#############
## LOAD IMAGES FROM ZIP FILE
############


import os
from zipfile import ZipFile

def load_data(dir_name='sentinelhub_downloads', dest_name = 'radar_time_series'):
#dir_name =  folder containing multiple zip folders
# dest_name =   #destination folder
    if not os.path.exists(dest_name): os.makedirs(dest_name)
    extension = ".zip"
    image_names = []
    
    #Unzip images to a new folder
    for item in os.listdir(dir_name): # loop through items in dir
        if item.endswith(extension): # check for ".zip" extension
            file_name =  os.path.join(dir_name, item)  # get full path of files
            zip_ref = ZipFile(file_name) # create zipfile object
            zipinfos=zip_ref.infolist()
            for zipinfo in zipinfos:
                #change filename to something shorter
                date = zipinfo.filename[0:10]
                info = zipinfo.filename[-79:]
                zipinfo.filename = date + '_' + info
                image_names.append(zipinfo.filename)
                #extract image to destination folder
                zip_ref.extract( zipinfo, dest_name)
            zip_ref.close() # close file
            #os.remove(file_name) # delete zipped file            
    return(image_names)       

