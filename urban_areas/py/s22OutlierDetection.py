# =============================================================================
# OUTLIER DETECION
# =============================================================================


df_plot = df_total.copy()
df_plot = df_plot[['mean_VV', sumdays_name]]
# =============================================================================
# VISUALLY CHECK OUTLIERS
# =============================================================================
## METHOD 1: HISTOGRAM 
fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2,figsize=(15, 8))
ax1 = sns.histplot(data=df_plot, x='mean_VV', kde=True, color="darkred", ax=ax1)
ax1.set_title('Histogram of mean VV', fontdict={'fontsize': 15})
ax2 = sns.histplot(data=df_plot, x=sumdays_name, kde=True, color="skyblue", ax=ax2)
ax2.set_title(f'Histogram of {sumdays_name}', fontdict={'fontsize': 15})
plt.show()

## METHOD 2: BOXPLOT
sns.set(rc = {'figure.figsize':(15, 10)})
plt.title(f'Boxplot of mean VV and sum {sum_days}-days precipitation (in mm)', fontdict={'fontsize': 25})
ax = sns.boxplot(data=df_plot, orient="h", palette="Set1")
ax = sns.swarmplot(data=df_plot, orient="h", color=".25", size=5)
# sns.reset_orig()
plt.show()


## METHOD 3: SCATTERPLOT
sns.set(rc = {'figure.figsize':(15, 10)})
plt.title(f'Scatterplot with sum {sum_days}-days precipitation (in mm) plotted against mean VV', fontdict={'fontsize': 25})
sns.scatterplot(data=df_plot, y=sumdays_name, x='mean_VV')
plt.show()

# =============================================================================
# STATISTICALLY CHECK OUTLIERS
# =============================================================================
## METHOD 1: PERCENTAGE THRESHOLDING
def topThresholding(df, variable, p=0.03):
    """
    This method uses a threshold value to determine the outliers. The default 
    value is set to 3% (0.03). This function returns a dataframe with the x% 
    highest values of the given variable.
    """
    # Sort dataframe by variable
    df = df.sort_values("mean_VV", axis=0, ascending=False)
    # Define top x% of dataframe relative to the len of the df
    top = round(int(len(df_plot)) * 0.03)
    # Create df based on top x%
    df1 = df["mean_VV"].head(top).copy()
    
    # Create list and enumerate over df to assign indexes of top to list
    outlier = []
    for i, v in enumerate(df1):
        outlier.append(df1.index[i])
    
    return outlier

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
    return outliers_prob, outliers_poss

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
    #Takes two parameters: dataframe & variable of interest as string
    columns = df.columns
    z = np.abs(stats.zscore(df))
    threshold = 3
    outlier = []
    index=0
    for item in range(len(columns)):
        if columns[item] == variable_name:
            index = item
    for i, v in enumerate(z.iloc[:, index]):
        if v > threshold:
            outlier.append(i)
        else:
            continue
    return outlier

## METHOD 4: MEDIAN ABSOLUTE DEVIATION (MAD) METHOD
def mad_method(df, variable_name, threshold=4):
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
    #Takes two parameters: dataframe & variable of interest as string
    columns = df.columns
    med = np.median(df, axis = 0)
    mad = np.abs(stats.median_abs_deviation(df))
    threshold = threshold
    outlier = []
    index=0
    for item in range(len(columns)):
        if columns[item] == variable_name:
            index == item
    for i, v in enumerate(df.loc[:,variable_name]):
        t = (v-med[index])/mad[index]
        if t > threshold:
            outlier.append(i)
        else:
            continue
    return outlier

# =============================================================================
# EXECUTE OUTLIER DETECTION
# =============================================================================
## METHOD 1: PERCENTAGE THRESHOLDING
top_thres_VV = topThresholding(df_plot, "mean_VV", p=0.03)
top_thres_precip = topThresholding(df_plot, sumdays_name, p=0.03)

## METHOD 2: TUKEYS METHOD
prob_outliers_VV, pos_outliers_VV = tukeys_method(df_plot, "mean_VV")
prob_outliers_precip, pos_outliers_precip = tukeys_method(df_plot, sumdays_name)

## METHOD 3: INTERNALLY STUDENTIZED METHOD (Z-SCORE)
outlier_z_VV = z_score_method(df_plot, "mean_VV")
outlier_z_precip = z_score_method(df_plot, sumdays_name)

## METHOD 4: MEDIAN ABSOLUTE DEVIATION (MAD) METHOD
outlier_mad_VV = mad_method(df_plot, "mean_VV")
outlier_mad_precip = mad_method(df_plot, sumdays_name)


"""
TO DO:
-> Add outlier detection methods as column to large dataframe
-> Give either value 0 or 1 to each index per column if they are outlier or not
-> Add percentage/likelihood per date how likely it is to be an outlier
-> Highlight these dates in a linegraph or scatterplot

"""

print(top_thres_VV)
print(prob_outliers_VV)
print(pos_outliers_VV)
print(outlier_z_VV)
print(outlier_mad_VV)

print('\n')

print(top_thres_precip)
print(prob_outliers_precip)
print(pos_outliers_precip)
print(outlier_z_precip)
print(outlier_mad_precip)