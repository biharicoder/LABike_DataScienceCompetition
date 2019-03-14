#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 07:08:55 2019

@author: shirishpandagare
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pyplot
import warnings
warnings.filterwarnings("ignore")
from math import radians, cos, sin, asin, sqrt

"""Load data and create the time stamped index""" 
def load_data(path):
    ext = path.split(".")[-1].lower()
    if ext == "csv":
        data = pd.read_csv(path)
    elif ext == "xlsx":
        data = pd.read_excel(path)
    
    data["Date"] = pd.to_datetime(data["start_time"])
    data = data.set_index("Date")
    data = data.sort_index()
    data = data.dropna()
    data["end_station"] = [int(stn) for stn in data.end_station]   ## Converting float values to interger. 
    return data

"""Adding Dummy Variable and dropping station with no entries"""
"""Adding Dummy Variable and dropping station with no entries"""
def add_variables(data):
    df = data
    start_stn = list(set(df.start_station))
    end_stn = list(set(df.end_station))
    """ length of end station is 142 and length of start station is 140"""

    """As length is not same of these two list, a search method is used to identify which element 
    is missing from the start station, hence the next chunk of code is to find
    the station number not in the start station list"""
    remove_stn = []
    for i in range(len(end_stn)):
        if end_stn[i] not in start_stn:
            remove_stn.append(end_stn[i])
    """Updating end station list"""   
    end_stn = [stn for stn in end_stn if stn not in remove_stn]

    """Removing rows with station number 4110 and 4118 as it is discarded from the analysis"""
    index_df =[]
    for i in range(len(df.end_station)):
        if df.end_station[i] == remove_stn[0] or df.end_station[i] == remove_stn[1]:
            index_df.append(df.index[i])
    data = df.drop(index_df)
    
    from datetime import timedelta
    #Setting plan_duration = 0 for passholder_type = Walk-up
    data['plan_duration'].loc[data['passholder_type'] == "Walk-up"] = 0

    #Setting annual pass = flex as both of them are the same
    data['passholder_type'].loc[data['passholder_type'] == "Annual Pass"] = "Flex Pass"

    #Calculating trip duration in minutes
    data['start_time']= pd.to_datetime(data['start_time']) 
    data['end_time']= pd.to_datetime(data['end_time']) 
    data['trip_duration_mins'] = (data.end_time - data.start_time)/ timedelta(minutes=1)
    
    #Create dummy variables for passholder type
    one_hot_pass = pd.get_dummies(data['passholder_type']).rename(columns={
            'Flex Pass': 'annual',
            'Monthly Pass': 'monthly',
            'One Day Pass': 'one_day',
            'Walk-up':'walk_up'})

    #Create dummy variables for trip route category
    one_hot_trip_type = pd.get_dummies(data['trip_route_category']).rename(columns={
            'Round Trip': 'round_trip',
            'One Way': 'one_way'})
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
    
    data = pd.concat([data , one_hot_pass, one_hot_trip_type], axis=1)

    return data

"""Creating Regression Data"""
def regression_data(data):
    
    def grouping_by_month(data, yr, offset):
        df = data.copy()
        df.index = df.index.year
        df = df.loc[yr]
        df["Date"] = pd.to_datetime(df["start_time"])
        df = df.set_index("Date")
        df["Month"] = df.index.month + offset

        df_sum = df.groupby(by=["start_station","Month",]).sum()[['plan_duration', 'trip_duration_mins', 'annual', 'monthly',
           'one_day', 'walk_up', 'one_way', 'round_trip']]
        df_count = df.groupby(by=["start_station","Month",]).count()[['trip_id']]

        df = pd.concat([df_sum, df_count], axis=1)

        return df
    
    df2016 = grouping_by_month(data, 2016, 0)
    df2017 = grouping_by_month(data, 2017, 12)
    df2018 = grouping_by_month(data, 2018, 24)
    col = list(df2016.columns.values)
    
    data_16_17 = pd.merge(df2016, df2017, left_index=True, right_index=True, how="outer", on= col )
    final_data = pd.merge(data_16_17, df2018, left_index=True, right_index=True, how="outer", on= col )
    
    return final_data

"""Function to get network matrix of the stations"""
def network(data):
    """Now creating a matrix of 140 x 140 with each station number"""
    matrix = np.zeros([140,140])
    station = list(set(data.start_station))
    strt_end_station = np.stack([data.start_station , data.end_station], axis= 0)

    for i in range(len(strt_end_station[0])):
        index1 = station.index(strt_end_station[0][i])
        index2 = station.index(strt_end_station[1][i])
        matrix[index1][index2] +=1

    station_matrix = pd.DataFrame(matrix, index= station, columns=station)
    
    return station_matrix

"""Function for linear regression"""
def linear_regression(data, station_list):
    station = station_list
    reg_coef = {"Demand_in_Stn": ['Distance','trip_duration_mins','annual','monthly','one_day','walk_up',
                             'one_way','round_trip','Time_line'] }
    for i in range(len(station)):
        stn = station[i]
        df = data.loc[stn]
        x = df.drop(["trip_id"], axis=1)
        x["Time_line"] = x.index
        y = df["trip_id"]
        reg = linear_model.LinearRegression()
        reg.fit(x,y)
        reg_coef[stn] =  reg.coef_
        coef_df = pd.DataFrame(reg_coef).T
        coef_df.reset_index()
        coef_df.columns = list(coef_df.iloc[0])
        coef_df = coef_df.drop(['Demand_in_Stn'], axis=0 )
        
    return coef_df