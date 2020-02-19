# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 11:54:22 2020

@author: DHOLSAPP
"""


import pandas as pd
import numpy as np
#Boltzmann constant

from utility import utility
from energyCalcs import energyCalcs


# Testing enviornment

#First lets speed up and get away from the .apply in the final output summary.  I need faster speed for processing

currentDirectory = r'C:\Users\DHOLSAPP\Desktop\WorldMapProject\WorldMapProject'

fileNames = utility.filesNameList( currentDirectory , 'level_1_data' )
locationData , raw_df = pd.read_pickle( currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_Level1\\' + fileNames[0])
summaryFrame = pd.read_pickle( r'C:\Users\DHOLSAPP\Desktop\WorldMapProject\WorldMapProject\Pandas_Pickle_DataFrames\Pickle_Level1_Summary\Pickle_Level1_Summary.pickle')

# Develop a script to process the PBSn solder bump fatigue

#########################################
#Get the maximum Cell temp average for the year
#raw_df['Local Date Time'] = pd.to_datetime(raw_df['Local Date Time'])

k = energyCalcs.k(summaryFrame['Average of Yearly Water Vapor Pressure(kPa)'])
edgeSealWidth = energyCalcs.edgeSealWidth( k )