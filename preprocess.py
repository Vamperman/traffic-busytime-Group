import glob
import os
import pandas as pd

files = glob.glob('extractbusiness/cleanoutput/*.csv')

def getData():
    traffic = pd.read_csv('out/traffic.csv')
    traffic = traffic.loc[traffic['avg'] != -1]
    business_info = []
    for file in files:
        info = pd.read_csv(file)
        info['business_type'] = os.path.splitext(file)[0]
        business_info.append(info)
    data = pd.concat(business_info)
    data = pd.melt(data, id_vars=['index','name','address','category','latitude','longitude','business_type'], var_name="date", value_name='popularity')
    data['popularity'] = pd.to_numeric(data["popularity"].str[:-1])

    date = pd.DataFrame(data['date'].str[14:].str.split(" ").to_list(), columns=['day','hour','period'])

    date['hour']  = pd.to_numeric(date['hour'])
    date['hour']  = date['hour'] + (date['period']=="p.m.")*12
    date['hour']  = date['hour'] - (date['hour']==24)*12

    data['day'] = date['day']
    data['hour'] = date['hour']
    traffic['ave_traffic'] = traffic['avg']
    traffic['max_traffic'] = traffic['max']
    data = data.drop('date', axis=1)

    data =  data.merge(traffic, on=['latitude','longitude','day','hour'], how='inner')
    return data.dropna()
