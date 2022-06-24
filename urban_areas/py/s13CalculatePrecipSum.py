# =============================================================================
# STEP 3: ADD SUM OF AVERAGES TO DATAFRAME
# =============================================================================
import os

def calculatePrecipSum(dest_name, df_total, sum_days):
    # Create new dataframe to work with
    df_sum = df_total[["average_(mm/day)"]].copy()
    
    # Create new column name
    col_name = f'sum_{sum_days}days'
    
    # Rename the column to the new column name based on sum_days
    df_sum[col_name] = 0
    
    start = 0
    
    while (start+sum_days-1) < len(df_sum):
        # Define first date to assign sum to
        count = start+sum_days
        
        # Sum the average precipitation values
        sum_xdays = df_sum["average_(mm/day)"][start:count].sum()
        
        # Get row and column label to which the sum_xdays should be assigned to
        row_label = df_sum.index[count-1]
        column_label = col_name
        
        # Add sum of xdays to specific position in dataframe
        df_sum.at[row_label, column_label] = sum_xdays
        
        # Add one to start to iterate through the dataframe
        start += 1
        
    # Keep only the 'sum' column so it can be joined to the larger dataframe
    df_sum = df_sum.drop("average_(mm/day)", axis=1)
    
    # Join df with sum column to total df
    df_total = df_total.join(df_sum)
    
    # Remove date as an index and add as a column to dataframe
    df_total = df_total.reset_index(level=0)
    
    ### Write final df to files
    # csv_name = os.path.join('data', dest_name, f'average_daily_precipitation_{file_names[0][5:23]}.csv')
    csv_path = os.path.join('data', 'precipitation_data', f'daily_precipitation_avg{sum_days}days_{dest_name}.csv')
    df_total.to_csv(csv_path, encoding='utf-8', index=False)
    
    print(f'\nThe data can be found in:\n"{csv_path}"')
    
    return df_total, csv_path
