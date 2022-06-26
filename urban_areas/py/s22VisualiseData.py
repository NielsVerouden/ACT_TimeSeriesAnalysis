# =============================================================================
# VISUALISE RESULTS
# =============================================================================
# IMPORT PACKAGES
import matplotlib.pyplot as plt
import pandas as pd
import os
import re
import numpy as np

def visualiseData(SAR_path, precipitation_csv, file_name, path_mean_vv):
    ## Create path to load precipitation csv
    path_precip = os.path.join("data", "precipitation_data", precipitation_csv)
    
    # Find sum_days inside name of precipitation CSV file and assign it to a variable
    days = re.search('_avg(.+?)days_', precipitation_csv).group(1)
    sum_xdays = f"sum_{days}days"
    mean_VV = file_name[0:7]

    # Create DataFrames for both mean VV and precipitation data
    df_vv = pd.read_csv(path_mean_vv)
    df_precip = pd.read_csv(path_precip)

    ## Combine DataFrames based on data
    df_total = pd.merge(df_precip, df_vv, on ='date')
    
    
    ##### LINEPLOT MEAN_VV AND AVERAGE PRECIPITATION
    ## Set parameters for the lineplot
    fig, ax = plt.subplots(figsize=(25, 5))
    plt.xticks(np.arange(0, len(df_total), (len(df_total)*0.015)))
    [lab.set_rotation(90) for lab in ax.get_xticklabels()]
    plt.title(f'Mean VV backscatter and average precipitation in urban area ({SAR_path})', 
              fontdict={'fontsize': 20})
    ax.set_xlabel('date', fontdict={'fontsize': 15})
    
    ## Plot first lineplot
    ax.plot(df_total['date'], df_total[mean_VV], color='red')
    ax.legend(labels=["Mean VV backscattter"], 
              loc='upper left')
    ax.set_ylabel("Mean VV backscattter", fontdict={'fontsize': 15})

    # Assign new lineplot to same x-axis but different y-axis
    ax2 = ax.twinx()

    ## Plot second lineplot
    ax2.plot(df_total['date'], df_total["average_(mm/day)"], color='blue')
    ax2.legend(labels=["average precipitation (in mm/day)"], 
                loc='upper right')
    ax2.set_ylabel("average precipitation", fontdict={'fontsize': 15})
    
    ## Plot final result
    plt.show()
    
    ##### LINEPLOT MEAN_VV AND SUM xDAYS PRECIPITATION
    ## Set parameters for the lineplot
    fig, ax = plt.subplots(figsize=(25, 5))
    plt.xticks(np.arange(0, len(df_total), (len(df_total)*0.015)))
    [lab.set_rotation(90) for lab in ax.get_xticklabels()]
    plt.title(f'Mean VV backscatter and {days}-day sum of precipitation in urban area ({SAR_path})', 
              fontdict={'fontsize': 20})
    ax.set_xlabel('date', fontdict={'fontsize': 15})
    
    ## Plot first lineplot
    ax.plot(df_total['date'], df_total[mean_VV], color='red')
    ax.legend(labels=["Mean VV backscattter"], 
              loc='upper left')
    ax.set_ylabel("Mean VV backscattter", fontdict={'fontsize': 15})

    # Assign new lineplot to same x-axis but different y-axis
    ax2 = ax.twinx()

    ## Plot second lineplot
    ax2.plot(df_total['date'], df_total[sum_xdays], color='blue')
    ax2.legend(labels=[f"{days}-day sum of precipitation (in mm)"], 
                loc='upper right')
    ax2.set_ylabel(f"{days}-day sum precipitation", fontdict={'fontsize': 15})
    
    ## Plot final result
    plt.show()


    return df_total, days, mean_VV, sum_xdays





