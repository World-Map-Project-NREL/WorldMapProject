# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 11:54:22 2020

@author: DHOLSAPP
"""

from utility import utility
from energyCalcs import energyCalcs
from firstClean import firstClean
import pandas as pd
import datetime as dt
from solarTime import solarTime



def my_to_datetime(date_str):
    
    '''
    HELPER METHOD
    
    my_to_datetime()
    
    Create a datetime object from a string of Date and Time.  
    
    @param date_str   -String, of Date and Time
    
    @return datetime  -dateTime object, return a datetime object of the string passed
    
    '''
    #If the time is not 24:00
    if date_str[11:13] != '24':
        # Return the date time object without any changes
        return pd.to_datetime(date_str, format='%m/%d/%Y %H:%M')
    
    # Correct the 24:00 by changing 24 to 0
    date_str = date_str[0:11] + '00' + date_str[13:]
    # Add 1 day to the date time object and return
    return pd.to_datetime(date_str, format='%m/%d/%Y %H:%M') + \
           dt.timedelta(days=1)





















# Testing enviornment

#First lets speed up and get away from the .apply in the final output summary.  I need faster speed for processing

currentDirectory = r'C:\Users\DHOLSAPP\Desktop\WorldMapProject\WorldMapProject'

fileNames = utility.filesNameList( currentDirectory , 'rawData' )
locationData , raw_df = pd.read_pickle( currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_RawData\\' + fileNames[50])

h = locationData.get(key = 'Site elevation (meters)') 
tD =  raw_df['Dew-point temperature'].values
tA =    raw_df['Dry-bulb temperature'].values 
windSpeed =   raw_df['Wind speed'].values 

raw_df['Total sky cover(okta)'] = (raw_df['Total sky cover'].astype(float) * 8) / 10

n =   raw_df['Total sky cover(okta)'].values




raw_df['Dew Yield'] = energyCalcs.dewYield( h , tD , tA , windSpeed , n )
#Replace negative numbers with 0
raw_df['Dew Yield'].values[raw_df['Dew Yield'].values < 0] = 0

raw_df['Water Vapor Pressure'] = energyCalcs.waterVaporPressure( raw_df['Dew-point temperature'] )


raw_df['Corrected Albedo'] = raw_df['Albedo']
raw_df['Corrected Albedo'].values[raw_df['Corrected Albedo'].values < 0 ] = 0.133
raw_df['Corrected Albedo'].values[raw_df['Corrected Albedo'].values > 100 ] = 0.133


DateTimeStrings = raw_df['Date (MM/DD/YYYY)'].str.cat(raw_df['Time (HH:MM)'],sep=" ")

raw_df['Local Date Time'] = DateTimeStrings.apply(lambda x: firstClean.my_to_datetime(x))

raw_df['Universal Date Time'] = firstClean.universalTimeCorrected(raw_df['Local Date Time'], 5)



raw_df['Local Solar Time'] = raw_df.apply(lambda x: solarTime.localTimeToSolarTime( 32 , 5 , x['Local Date Time']), axis=1)

raw_df['Hourly Local Solar Time'] = raw_df['Local Solar Time'].dt.hour + (raw_df['Local Solar Time'].dt.minute/60)












