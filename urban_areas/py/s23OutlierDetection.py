# =============================================================================
# OUTLIER DETECION
# =============================================================================
# IMPORT PACKAGES
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import scipy.stats as stats
import pandas as pd
import os

# =============================================================================
# CHECK OUTLIERS
# =============================================================================
# METHOD 1: VISUALLY CHECK OUTLIERS
def visualOutlierDetection(SAR_path, df_total, days, mean_VV, sum_xdays):
    ## Create copy of dataframe and keep only relevant columns for plotting
    df_plot = df_total.copy()
    df_plot = df_plot[[mean_VV, sum_xdays]]
    
    ## METHOD 1: HISTOGRAM 
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2,figsize=(15, 8))
    ax1 = sns.histplot(data=df_plot, x=mean_VV, kde=True, color="darkred", ax=ax1)
    ax1.set_title('Histogram of mean VV', 
                  fontdict={'fontsize': 15})
    ax2 = sns.histplot(data=df_plot, x=sum_xdays, kde=True, color="skyblue", ax=ax2)
    ax2.set_title(f'Histogram of sum {days}-days precipitation (in mm)', 
                  fontdict={'fontsize': 15})
    plt.show()
    
    ## METHOD 2: BOXPLOT
    sns.set(rc = {'figure.figsize':(15,8)})
    plt.title(f'Boxplot of mean VV and sum {days}-days precipitation (in mm) ({SAR_path})', 
              fontdict={'fontsize': 15})
    sns.boxplot(data=df_plot, orient="h", palette="Set1")
    sns.swarmplot(data=df_plot, orient="h", color=".25", size=5)
    # sns.reset_orig()
    plt.show()
    
    ## METHOD 3: SCATTERPLOT
    sns.set(rc = {'figure.figsize':(15, 8)})
    plt.title(f'Scatterplot with sum {days}-days precipitation (in mm) (y-ax) and mean VV (x-ax) ({SAR_path})', 
              fontdict={'fontsize': 15})
    sns.scatterplot(data=df_plot, x=sum_xdays, y=mean_VV)
    plt.show()
    
    return

# METHOD 2: STATISTICALLY CHECK OUTLIERS
def statisticalOutlierDetection(df_total, mean_VV, sum_xdays):
    variables = [mean_VV, sum_xdays]
    outliers = []
    LR_columns = []
    df_outliers_list = []
    for variable in variables:
        ## METHOD 1: PERCENTAGE THRESHOLDING
        df_threshold = topThresholding(df_total, variable, p=0.1)
    
        ## METHOD 2: TUKEYS METHOD
        df_tukeys = tukeys_method(df_total, variable)
    
        ## METHOD 3: INTERNALLY STUDENTIZED METHOD (Z-SCORE)
        df_zscore = z_score_method(df_total, variable)
    
        ## METHOD 4: MEDIAN ABSOLUTE DEVIATION (MAD) METHOD
        df_mad = mad_method(df_total, variable, threshold=3)

        ## Combine methods into one list
        df_outliers = [df_threshold, df_tukeys, df_zscore, df_mad]
        
        outliers.append(df_outliers)
        
        # Assign column_name of variable to a list
        column_name = f'outlier_LR_{variable}'
        LR_columns.append(column_name)
    
    for idx in range(len(outliers)):
        # Concat the outlier dataframes inside the outliers list
        df_outliers = pd.concat(outliers[idx], axis=1)

        # Create new column with likelihood of being an outlier according to the methods
        df_outliers[LR_columns[idx]] = (df_outliers.sum(axis=1) / len(df_outliers.columns))
        
        # Also create and return DataFrame with only likelihood ratio (LR)
        df_outliers_LR = df_outliers[LR_columns[idx]].copy()
        
        # Apppend DataFrame for each variable to list
        df_outliers_list.append(df_outliers_LR)

    # Clean DataFrame so only date, precip average, precip sum, and mean VV are left
    df_total.drop(list(df_total.filter(regex = 'ppt_')), axis = 1, inplace = True)
    
    df_plot = pd.concat([df_total, df_outliers_list[0], df_outliers_list[1]], axis=1)
    
    return df_plot, LR_columns

# =============================================================================
# OUTLIER DETECTION METHODS
# =============================================================================
## METHOD 1: PERCENTAGE THRESHOLDING
def topThresholding(df, variable, p=0.01):
    """
    This method uses a threshold value to determine the outliers. The default 
    value is set to 5% (0.05). So, in default, this function returns a dataframe 
    with the top 5% highest values of the given variable.
    """
    # Sort dataframe by variable
    df_sort = df.sort_values(variable, axis=0, ascending=False)

    # Define top x% of dataframe relative to the len of the df
    top = round(int(len(df_sort)) * p)

    # Create df based on top x%
    df1 = df_sort[variable].head(top).copy()

    # Create list and enumerate over df to assign indexes of top to list
    outlier = []
    for i, v in enumerate(df1):
        outlier.append(df1.index[i])

    # Create copy of dataframe where outliers are stored
    df_outlier = df[['date']].copy()
    df_outlier = df_outlier.drop('date', axis=1)
    
    # Assign base value to new threshold. 0 -> no outlier, 1 -> outlier
    df_outlier['topThreshold'] = 0
    
    # Give value 1 to dates if the index is in the outlier list
    for idx in outlier:
        df_outlier.at[idx, 'topThreshold'] = 1
    
    return df_outlier

## METHOD 2: TUKEYS METHOD
def tukeys_method(df, variable):
    """
    The distribution’s inner fence is defined as 1.5xIQR below Q1, and 1.5xIQR 
    above Q3. The outer fence is defined as 3xIQR below Q1, and 3xIQR above Q3. 
    Following Tukey, only the probable outliers are treated, which lie outside 
    the outer fence. Possible and probable outliers are returned in this function.
    
    If a distribution is highly skewed (usually found in real-life data), the 
    Tukey method can be extended to the log-IQ method. This is also tried in this
    script but this method has not proven to be more accurate. Hence, the basic
    Tukeys method is used
    
    Source: https://gist.github.com/alice203/86592aa5e91b478f49bde1252b9efb89#file-outlier_tukeymethod
    """
    #Takes two parameters: dataframe & variable of interest as string
    q1 = df[variable].quantile(0.25)
    q3 = df[variable].quantile(0.75)
    iqr = q3-q1
    inner_fence = 1.5*iqr
    outer_fence = 3*iqr
    
    #inner fence lower and upper end
    inner_fence_le = q1-inner_fence
    inner_fence_ue = q3+inner_fence
    
    #outer fence lower and upper end
    outer_fence_le = q1-outer_fence
    outer_fence_ue = q3+outer_fence
    
    outliers_prob = []
    outliers_poss = []
    for index, x in enumerate(df[variable]):
        if x <= outer_fence_le or x >= outer_fence_ue:
            outliers_prob.append(index)
    for index, x in enumerate(df[variable]):
        if x <= inner_fence_le or x >= inner_fence_ue:
            outliers_poss.append(index)
    
    # Create copy of dataframe where outliers are stored
    df_outlier = df[['date']].copy()
    df_outlier = df_outlier.drop('date', axis=1)
    
    # Assign base value to new threshold. 0 -> no outlier, 1 -> outlier
    df_outlier['tukeys_poss'] = 0
    df_outlier['tukeys_prob'] = 0
    
    # Give value 1 to dates if the index is in the outlier list
    for idx in outliers_poss:
        df_outlier.at[idx, 'tukeys_poss'] = 1
    for idx in outliers_prob:
        df_outlier.at[idx, 'tukeys_prob'] = 1
    
    return df_outlier

## METHOD 3: INTERNALLY STUDENTIZED METHOD (Z-SCORE)
def z_score_method(df, variable_name):
    """
    For each observation (Xn), it is measured how many standard deviations the 
    data point is away from its mean (X̄). Following a common rule of thumb, if 
    z > C, where C is usually set to 3, the observation is marked as an outlier. 
    This rule stems from the fact that if a variable is normally distributed, 
    99.7% of all data points are located 3 standard deviations around the mean.
    
    Source: https://gist.github.com/alice203/113eb992cdab5a92f51b9a3bfaa47dbd#file-outlier_zscore
    """
    # Takes two parameters: dataframe & variable of interest as string
    df_single = df[[variable_name]].copy()
    z = np.abs(stats.zscore(df_single))
    threshold = 3
    outlier = []
    for i, v in enumerate(z.iloc[:,0]):
        if v > threshold:
            outlier.append(i)
        else:
            continue
    
    # Create copy of dataframe where outliers are stored
    df_outlier = df[['date']].copy()
    df_outlier = df_outlier.drop('date', axis=1)
    
    # Assign base value to new threshold. 0 -> no outlier, 1 -> outlier
    df_outlier['z_score'] = 0
    
    # Give value 1 to dates if the index is in the outlier list
    for idx in outlier:
        df_outlier.at[idx, 'z_score'] = 1
    
    return df_outlier

## METHOD 4: MEDIAN ABSOLUTE DEVIATION (MAD) METHOD
def mad_method(df, variable_name, threshold=3):
    """
    The median absolute deviation method (MAD) replaces the mean and standard 
    deviation with more robust statistics, like the median and median absolute 
    deviation. The test statistic is calculated like the z-score using robust 
    statistics. Also, to identify outlying observations, the same cut-off point 
    of 3 is used. If the test statistic lies above 3, it is marked as an outlier. 
    Compared to the internally (z-score) and externally studentized residuals, 
    this method is more robust to outliers and does assume X to be parametrically
    distributed. On average, the most points are classed as outliers with the MAD 
    method when compared to the other methods
    
    Source: https://gist.github.com/alice203/020a22493cb10025e4f0b066ea3a25a5#file-outlier_madmethod
    """
    # Takes two parameters: dataframe & variable of interest as string
    df_single = df[[variable_name]].copy()
    med = np.median(df_single, axis=0)
    mad = np.abs(stats.median_abs_deviation(df_single))
    outlier = []
    index=0
    for i, v in enumerate(df_single.loc[:,variable_name]):
        t = (v-med[index])/mad[index]
        if t > threshold:
            outlier.append(i)
        else:
            continue
    
    # Create copy of dataframe where outliers are stored
    df_outlier = df[['date']].copy()
    df_outlier = df_outlier.drop('date', axis=1)
    
    # Assign base value to new threshold. 0 -> no outlier, 1 -> outlier
    df_outlier['mad'] = 0
    
    # Give value 1 to dates if the index is in the outlier list
    for idx in outlier:
        df_outlier.at[idx, 'mad'] = 1
        
    return df_outlier

# =============================================================================
# VISUALISE AND EXPORT OUTLIERS
# =============================================================================
def visualiseStatisticalOutliers(SAR_path, df_outlier, LR_columns, mean_VV, sum_xdays, days):  
    # Get list of indices of both variables (which will be used to marker the outliers)
    indexLR_vv = df_outlier.loc[df_outlier[LR_columns[0]] != 0].index.to_list()
    indexLR_precip = df_outlier.loc[df_outlier[LR_columns[1]] != 0].index.to_list()
    
    ##### VISUALISE RESULTS - SCATTERPLOT 
    variables = [mean_VV, sum_xdays]
    for idx in range(len(variables)):
        variable = variables[idx]       
        sns.set(rc = {'figure.figsize':(15, 8)})
        plt.title(f'Scatterplot with outlier Likelihood Ratio (LR) for {variable} ({SAR_path})', 
                  fontdict={'fontsize': 15})
        sns.scatterplot(data=df_outlier, x=sum_xdays, y=mean_VV, 
                        hue=LR_columns[idx],
                        style=LR_columns[idx],
                        palette="deep")
        plt.legend(loc='upper left')
        plt.show()

    ##### VISUALISE RESULTS - LINEPLOT 
    ## Set parameters for the lineplot
    fig, ax = plt.subplots(figsize=(25, 5))
    plt.xticks(np.arange(0, len(df_outlier), (len(df_outlier)*0.015)))
    [lab.set_rotation(90) for lab in ax.get_xticklabels()]
    plt.title(f'Mean VV backscatter and {days}-day sum of precipitation in urban area ({SAR_path})', 
              fontdict={'fontsize': 20})
    ax.set_xlabel('date', fontdict={'fontsize': 15})
    
    ## Plot first lineplot
    ax.plot(df_outlier['date'], df_outlier[mean_VV],
                color='red',
                marker = 'o', 
                markersize=10, 
                # fillstyle='none', 
                markeredgewidth=1, 
                markeredgecolor='red',
                markevery=indexLR_vv)
    ax.legend(labels=["Mean VV backscattter"], 
              loc='upper left')
    ax.set_ylabel("Mean VV backscattter", fontdict={'fontsize': 15})

    # Assign new lineplot to same x-axis but different y-axis
    ax2 = ax.twinx()

    ## Plot second lineplot
    ax2.plot(df_outlier['date'], df_outlier[sum_xdays],
                color='blue',
                marker = 'o', 
                markersize=10, 
                # fillstyle='none', 
                markeredgewidth=1, 
                markeredgecolor='blue',
                markevery=indexLR_precip)
    ax2.legend(labels=[f"{days}-day sum of precipitation (in mm)"], 
                loc='upper right')
    ax2.set_ylabel(f"{days}-day sum precipitation", fontdict={'fontsize': 15})
    
    ## Plot final result
    plt.show()    
    
def exportOutlierDetection(df_outlier, SAR_path):
    # Create directory
    dest_path = os.path.join('urban_areas', 'output', 'outlierDetection')
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    
    ## Write DataFrame with outliers to output folder
    csv_path = os.path.join(dest_path, f'outliers_{SAR_path}.csv')
    
    df_outlier.to_csv(csv_path, encoding='utf-8', index=False)
    
    print(f'\nThe data can be found in:\n"{csv_path}"')
    
    return
