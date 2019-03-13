# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 00:24:12 2019

@author: Shiva
"""
import pandas as pd
import numpy as np
from datetime import timedelta
from math import radians, cos, sin, asin, sqrt

#Reading data files
data = pd.read_excel('LABikeData.xlsx')
df_station = pd.read_excel('Station_Table.xlsx')

## Creating new variable Date whose values are taken from start_time
data["Date"] = pd.to_datetime(data["start_time"])  
data = data.set_index("Date")

#Setting plan_duration = 0 for passholder_type = Walk-up
data['plan_duration'].loc[data['passholder_type'] == "Walk-up"] = 0

#Setting annual pass = flex as both of them are the same
data['passholder_type'].loc[data['passholder_type'] == "Annual Pass"] = "Flex Pass"

#Calculating trip duration in minutes
data['start_time']= pd.to_datetime(data['start_time']) 
data['end_time']= pd.to_datetime(data['end_time']) 
data['trip_duration_mins'] = (data.end_time - data.start_time)/ timedelta(minutes=1)

#Calculating Distance traveled 
data["Distance"]=""
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r
  
vfunc = np.vectorize(haversine)
data.Distance= vfunc(data.start_lon,data.start_lat,data.end_lon,data.end_lat)


#Dropping missing values
data = data.dropna()
'''
rides_df = rides_df.join([one_hot_pass,one_hot_trip_type]).reset_index()
'''
#Reading json file which includes address and capabilities of different station
#Parsing out relevant fields
df = pd.read_json("station_details.json", orient='columns')
station_properties = pd.read_json( (df['features']).to_json(),orient='index')
station_details = pd.read_json(station_properties['properties'].to_json(), orient = 'index')
station_info = station_details[['kioskId','addressStreet','name','bikesAvailable','totalDocks','docksAvailable']]

#Adding start station attributes
data = pd.merge(data, station_info, how = "left", left_on = "start_station",
                    right_on =['kioskId']).rename(columns = {'addressStreet':'start_address',
                            'name':'start_station',
                              'bikesAvailable':'start_bikes',
                              'totalDocks':'start_docks',
                              'docksAvailable':'start_docks'}).drop('kioskId',1)

#Adding end station attributes
data = pd.merge(data, station_info, how = "left", left_on = "end_station",
                    right_on =['kioskId']).rename(columns = {'addressStreet':'end_address',
                            'name':'end_station',
                              'bikesAvailable':'end_bikes',
                              'totalDocks':'end_docks',
                              'docksAvailable':'end_docks'}).drop('kioskId',1)

#Saving it as a csv file
data.to_csv("rides_df.csv",index=False)

#Create dummy variables for passholder type
one_hot_pass = pd.get_dummies(data['passholder_type']).rename(columns={
        'Flex Pass': 'annual',
        'Monthly Pass': 'monthly',
        'One Day Pass': 'one_day',
        'Walk-up':'walk_up',
        'Annual Pass': 'annual'})

#Create dummy variables for trip route category
one_hot_trip_type = pd.get_dummies(data['trip_route_category']).rename(columns={
        'Round Trip': 'round_trip',
        'One Way': 'one_way'})



