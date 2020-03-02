# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 11:54:22 2020

@author: DHOLSAPP
"""


import pandas as pd
import pvlib

from utility import utility



# Testing enviornment

#First lets speed up and get away from the .apply in the final output summary.  I need faster speed for processing

currentDirectory = r'C:\Users\DHOLSAPP\Desktop\WorldMapProject\WorldMapProject'

fileNames = utility.filesNameList( currentDirectory , 'level_1_data' )
locationData , raw_df = pd.read_pickle( currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_RawData\\' + fileNames[0])
summaryFrame = pd.read_pickle( r'C:\Users\DHOLSAPP\Desktop\WorldMapProject\WorldMapProject\Pandas_Pickle_DataFrames\Pickle_Level1_Summary\Pickle_Level1_Summary.pickle')

# Make a script to process the single axis tracker

latitude = locationData.get(key = 'Site latitude')  
longitude = locationData.get(key = 'Site longitude')

level_1_df = raw_df

#hoursAheadorBehind will be the number of hours ahead or behind universal time
#            hoursAheadOrBehind = locationData.get(key = 'Site time zone (Universal time + or -)')
#If the latitude is in the southern hemisphere of the globe then surface azimuth of the panel must be 0 degrees
if latitude <= 0:
    surface_azimuth = 0
# If the latitude is in the northern hemisphere set the panel azimuth to 180
else:
    surface_azimuth = 180 
# Set the suface tilt to the latitude   
# PVlib requires the latitude tilt to always be positve for its irradiance calculations
surface_tilt = abs(latitude)        

#            level_1_df = firstClean.cleanedFrame( raw_df , hoursAheadOrBehind , longitude )
################  
# Calculate the Solar Position
# Create a dataframe of solar parameter from pvlib using NREL spa algorithm
solarPosition_df = pvlib.solarposition.get_solarposition( level_1_df['Universal Date Time'], 
                                                                         latitude, 
                                                                         longitude, 
                                                                         altitude=None, 
                                                                         pressure=None, 
                                                                         method='nrel_numba', 
                                                                         temperature=12 ) 
level_1_df['Solar Zenith'] = solarPosition_df['zenith'].values
level_1_df['Solar Azimuth'] = solarPosition_df['azimuth'].values
level_1_df['Solar Elevation'] = solarPosition_df['elevation'].values


singleAxisTracker = pvlib.tracking.singleaxis(level_1_df['Solar Zenith'], level_1_df['Solar Azimuth'], axis_tilt=0, axis_azimuth=0, max_angle=90, backtrack=True, gcr=0.2857142857142857)

singleAxisTracker = pvlib.tracking.singleaxis(level_1_df['Solar Zenith'], level_1_df['Solar Azimuth'], max_angle=90, backtrack=True, gcr=0.2857142857142857)


