# =============================================================================
# STEP 2: COMBINE PRECIPITATION DATA INTO ONE DATAFRAME
# =============================================================================
import os
import pandas as pd
import re    

def combinePrecipData(file_names, dest_name):
    ### Create one large dataframe where all rainfall data should be stored
    # Define path name of first file
    path_name = os.path.join('data', 'precipitation_data', file_names[0])
    
    # Create dataframe of first file
    df_total = pd.read_csv(path_name, header = 19)
    
    # Remove all data in this file and keep only the index
    df_total = pd.DataFrame(index=df_total.index)

    ### Loop over all files in file_names and clean data
    for file_name in file_names:
        # Define path name
        path_name = os.path.join('data', 'precipitation_data', file_name)
        
        # Create dataframe of each csv file and remove first 19 rows
        df_single = pd.read_csv(path_name, header = 19)
        
        # Select columns to keep and drop other columns
        columns_keep = ['YEAR', 'MO', 'DY', 'PRECTOTCORR']
        df_single = df_single[df_single.columns[df_single.columns.isin(columns_keep)]]
        
        # Drop year, month, and day columns (so only ppt and date columns are kept)
        df_single = df_single.drop(['YEAR', 'MO', 'DY'], axis=1)

        # Define new column name of each location
        col_name = re.search('_(loc.+?).CSV', file_name).group(1)
        col_name = f'ppt_{col_name}'
        
        # Rename old ppt name with new ppt name of the location
        df_single.rename(columns = {'PRECTOTCORR':col_name}, inplace = True)
        
        # Join each individual dataframe with large df (-> df_rain_all)
        df_total = df_total.join(df_single)
    
    ### Assign date to the final df
    df_date = pd.read_csv(path_name, header = 19)
    df_date = df_date[df_date.columns[df_date.columns.isin(columns_keep[0:3])]]

    # Merge year, month, and day columns into one column and convert to datetime dtype   
    df_date['date'] = df_date[df_date.columns[0:3]].apply(lambda x: ''.join(x.dropna().astype(str)), axis=1)
    df_date['date'] = pd.to_datetime(df_date['date'], format='%Y%m%d')

    # Add dates to large dataframe
    df_total = df_total.set_index(df_date['date'])
    
    # Create new column based on the average precipitation per date (=sum/length(columns))
    df_total['average_(mm/day)'] = (df_total.sum(axis='columns')/len(df_total.columns))
    
    ### Remove rows that contain NoData (value -999)
    df_total = df_total.loc[df_total[col_name] != -999]
    
    ### Remove individual CSV files        
    for file_name in file_names:
        path_name = os.path.join('data', 'precipitation_data', file_name) 
        if os.path.exists(path_name):
            os.remove(path_name)
    
    # Return the final dataframe
    return df_total
