# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 11:54:22 2020

@author: DHOLSAPP
"""


import pandas as pd
import numpy as np
#Boltzmann constant
from scipy.constants import k , convert_temperature
from utility import utility
from energyCalcs import energyCalcs


# Testing enviornment

#First lets speed up and get away from the .apply in the final output summary.  I need faster speed for processing

currentDirectory = r'C:\Users\DHOLSAPP\Desktop\WorldMapProject\WorldMapProject'

fileNames = utility.filesNameList( currentDirectory , 'level_1_data' )
locationData , raw_df = pd.read_pickle( currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_Level1\\' + fileNames[237])
summaryFrame = pd.read_pickle( r'C:\Users\DHOLSAPP\Desktop\WorldMapProject\WorldMapProject\Pandas_Pickle_DataFrames\Pickle_Level1_Summary\Pickle_Level1_Summary.pickle')

# Develop a script to process the PBSn solder bump fatigue

#########################################
#Get the maximum Cell temp average for the year
#raw_df['Local Date Time'] = pd.to_datetime(raw_df['Local Date Time'])

timeAndTemp_df = pd.DataFrame( raw_df , columns = ['Local Date Time' , 'Cell Temperature(open_rack_cell_glassback)(C)'])
#timeAndTemp_df['Cell Temperature(open_rack_cell_glassback)(C)'] = convert_temperature(raw_df['Cell Temperature(open_rack_cell_glassback)(C)'], 'Celsius', 'Kelvin')

#Arguments will be Local TIme and Cell Temperature

timeAndTemp_df.index = raw_df['Local Date Time']
timeAndTemp_df['month'] = timeAndTemp_df.index.month
timeAndTemp_df['day'] = timeAndTemp_df.index.day

#Group by month and day to determine the max and min cell Temperature (C) for each day
dailyMaxCellTemp_series = timeAndTemp_df.groupby(['month','day'])['Cell Temperature(open_rack_cell_glassback)(C)'].max()
dailyMinCellTemp_series = timeAndTemp_df.groupby(['month','day'])['Cell Temperature(open_rack_cell_glassback)(C)'].min()

cellTempChange = pd.DataFrame({ 'Max': dailyMaxCellTemp_series, 'Min': dailyMinCellTemp_series})
cellTempChange['TempChange'] = cellTempChange['Max'] - cellTempChange['Min']

#Find the average temperature change for every day of one year (C) arg for model
MeanDailyMaxCellTempChange_Average = cellTempChange['TempChange'].mean()
#Find the average max temp for every day of one year (C) arg for model

dailyMaxCellTemp_Average = convert_temperature(dailyMaxCellTemp_series.mean(), 'Celsius', 'Kelvin')
#dailyMaxCellTemp_Average = dailyMaxCellTemp_series.mean()

################################

##############################
#Find the number of times the temperature crosses over 54.8(C)
temp_df = pd.DataFrame()
temp_df['CellTemp'] = raw_df['Cell Temperature(open_rack_cell_glassback)(C)']
temp_df['COMPARE'] = raw_df['Cell Temperature(open_rack_cell_glassback)(C)']
temp_df['COMPARE'] = temp_df.COMPARE.shift(-1)

reversalTemp = 54.8

temp_df['cross'] = (
    ((temp_df.CellTemp >= reversalTemp) & (temp_df.COMPARE < reversalTemp)) |
    ((temp_df.COMPARE > reversalTemp) & (temp_df.CellTemp <= reversalTemp)) |
    (temp_df.CellTemp == reversalTemp))

numChangesTempHist = temp_df.cross.sum()
###################################



D = 405.6 * (MeanDailyMaxCellTempChange_Average **1.9) * (numChangesTempHist**.33) * np.exp(-(.12/((.00008617333262145)*dailyMaxCellTemp_Average)))

reversalTemp = 54.8
finalTest = energyCalcs.solderFatigue( raw_df['Local Date Time'] , 
                                      raw_df['Cell Temperature(open_rack_cell_glassback)(C)'] , 
                                      reversalTemp)
