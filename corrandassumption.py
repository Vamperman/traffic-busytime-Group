import os
import sys
import pandas as pd
from scipy.stats import linregress, normaltest
import matplotlib.pyplot as plt
from preprocess import getData

# List to store DataFrames for test
# data = {
#     'name': ['Restaurant A'] * 10 + ['Gym B'] * 10,
#     'address': ['123 Main St'] * 10 + ['456 Oak St'] * 10,
#     'ave_traffic': [i * 10 for i in range(10)] + [i * 5 for i in range(10)],
#     'max_traffic': [i * 20 for i in range(10)] + [i * 10 for i in range(10)],
#     'day': ['Monday'] * 20,
#     'hour': list(range(8, 18)) * 2,
#     'popularity': [0, 1, 2, 3, 4, 34, 65, 7, 8, 9] * 2,
#     'lat': [49.2827 + i * 0.001 for i in range(10)] + [49.2811 + i * 0.002 for i in range(10)],
#     'lon': [-123.1207 + i * 0.001 for i in range(10)] + [-123.1245 + i * 0.002 for i in range(10)],
#     'business_type': ['Restaurant'] * 10 + ['Gym'] * 10
# }



#data= pd.DataFrame(data)


def crr_each(df):
    correlations = {}
    businesstype = df['business_type'].unique()
    for business in businesstype:
        subset = df[df['business_type'] == business]
        correlations[business] = subset['ave_traffic'].corr(subset['popularity'])
    return correlations


def check_homoscedastic(df, str=''):
    slope, intercept, r_value, p_value, std_err = linregress(df['ave_traffic'], df['popularity'])
    estimated = slope * df['ave_traffic'] + intercept 
    residuals = df['popularity'] - estimated
    name= str + 'homoscedasticity.png'
    plt.scatter(estimated, residuals)
    plt.xlabel('Predicted Values')
    plt.ylabel('Residuals')
    plt.title('Residual Plot')
    plt.axhline(y=0, color='r', linestyle='-')
    plt.savefig(name)
    plt.close()
    
def check_normality(df, str = ''):
    slope, intercept, r_value, p_value, std_err = linregress(df['ave_traffic'], df['popularity'])
    estimated = slope * df['ave_traffic'] + intercept 
    residuals = df['popularity'] - estimated
    name  = str + 'normality.png'
    plt.hist(residuals)
    plt.xlabel('Residuals')
    plt.ylabel('Frequency')
    plt.title('Histogram of Residuals')
    plt.savefig(name)
    plt.close()
    if normaltest(residuals)[1] < 0.05:
        print(normaltest(residuals)[1])
        print('The residuals are not normally distributed.')
    else:
        print(str, p_value, r_value**2)
        print('The residuals are normally distributed.')
        
def each_assumption(df):
    businesstype = df['business_type'].unique()
    for business in businesstype:
        subset = df[df['business_type'] == business]
        check_homoscedastic(subset, business)
        check_normality(subset, business)


    

def main():
        # Directory containing the CSV files
    data = getData()
    #data['transform_ave_traffic'] = data['ave_traffic'].apply(lambda x: x ** 3)
    #data['transform_popularity'] = data['popularity'].apply(lambda x: x ** 3)
    #    df['business_type'] = file_name
    slope, intercept, r_value, p_value, std_err = linregress(data['ave_traffic'], data['popularity'])
    #print(p_value)
    #correlation_coefficient = data['ave_traffic'].corr(data['popularity'])
    check_homoscedastic(data)
    check_normality(data)
    print(crr_each(data))
    #print(correlation_coefficient)
    each_assumption(data)
    
if __name__ == '__main__':
    
    main()
