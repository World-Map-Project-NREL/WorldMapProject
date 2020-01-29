# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 11:00:22 2020

World Tab of Excel sheet

This will be the inputs for the Vant Hoff Irradiance degradation function 
applied to the TMY data



@author: dholsapp
"""

from Processing.utility import utility
from Processing.energyCalcs import energyCalcs

#from utility import utility
#from energyCalcs import energyCalcs

import pandas as pd


class customCalculations:

    def generateVantHoffSummarySheet(configType , refTemp , Tf , x , Ichamber , currentDirectory ):
        '''
        Create a summary frame of Vant Hoff Irradiance Degradation based on level_1
        dataframes naming convention
        
        @param configType            -string, name of the dataframe column containing temperature
                                          'Module Temperature(open_rack_cell_glassback)(C)'
                                          'Module Temperature(roof_mount_cell_glassback)(C)'
                                          'Module Temperature(open_rack_cell_polymerback)(C)'
                                          'Module Temperature(insulated_back_polymerback)(C)'                                        
                                          'Module Temperature(open_rack_polymer_thinfilm_steel)(C)' 
                                          'Module Temperature(22x_concentrator_tracker)(C)'
        @param currentDirectory      -string, path of current working directory
        @param refTemp               -float, reference temperature (C) "Chamber Temperature"  
        @param Tf                    -float, multiplier for the increase in degradation
                                          for every 10(C) temperature increase                                          
        @param x                     -float, fit parameter
        @param Ichamber              -float, Irradiance of Controlled Condition W/m^2
                 
        @return  degSummarySheet     -dataframe, Summary of Vant Hoff Degradation Calculation
                                                      'FilePath'
                                                      'Station name'
                                                      'Station country or political unit'
                                                      'Station State'
                                                      'Data Source'
                                                      'Site latitude'
                                                      'Site longitude'
                                                      'Site time zone (Universal time + or -)'
                                                      'Site elevation (meters)'
                                                      'Avg Rate of Degradation Environmnet'
                                                      'Sum Rate of Degradation Environmnet'
                                                      'Rate Of Degradation Controlled Environmnet'
                                                      'Acceleration Factor'
        '''
        #Get all the file names of level_1 pickles
        fileNames = utility.filesNameList( currentDirectory , 'level_1_data' )
    
        #Create the blank summary df
        degSummarySheet = pd.DataFrame(columns=['Site Identifier Code',
                                                'FilePath', 
                                                'Station name',
                                                'Station country or political unit', 
                                                'Station State', 
                                                'Data Source',
                                                'Site latitude', 
                                                'Site longitude',
                                                'Site time zone (Universal time + or -)', 
                                                'Site elevation (meters)',
                                                'Avg Rate of Degradation Environmnet',
                                                'Sum Rate of Degradation Environmnet',
                                                'Rate Of Degradation Controlled Environmnet',
                                                'Acceleration Factor'
                                                ])
        
        #Fill the blank summary sheet with content
        for i in range (0 , len(fileNames)):
            # Import the raw dataframe of the individual location to clean and process
            locationData , level_1_df = pd.read_pickle( currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_Level1\\' + fileNames[i])    
        
            globalPOA = level_1_df['POA Global(W/m^2)']
            moduleTemp = level_1_df[configType]
        
            sumOfDegEnv, avgOfDegEnv, rateOfDegChamber, accelerationFactor = energyCalcs.vantHoffDeg( x , Ichamber , globalPOA , moduleTemp , Tf , refTemp )    
            
            degSummarySheet = degSummarySheet.append({'Site Identifier Code':  locationData.get(key = 'Site Identifier Code'), 
                              'FilePath': fileNames[i], 
                              'Station name': locationData.get(key = 'Station name'),
                              'Station country or political unit': locationData.get(key = 'Station country or political unit'),
                              'Station State': locationData.get(key = 'Station State'), 
                              'Data Source': locationData.get(key = 'Data Source'), 
                              'Site latitude': locationData.get(key = 'Site latitude'),
                              'Site longitude': locationData.get(key = 'Site longitude'),
                              'Site time zone (Universal time + or -)': locationData.get(key = 'Site time zone (Universal time + or -)'),
                              'Site elevation (meters)': locationData.get(key = 'Site elevation (meters)'), 
                              'Avg Rate of Degradation Environmnet': avgOfDegEnv, 
                              'Sum Rate of Degradation Environmnet': sumOfDegEnv,
                              'Rate Of Degradation Controlled Environmnet': rateOfDegChamber,
                              'Acceleration Factor': accelerationFactor}, 
                               ignore_index=True)
            
        #Save the frame as a pickle for additional functionality  
        degSummarySheet.to_pickle( currentDirectory + r'\Pandas_Pickle_DataFrames\Pickle_CustomCals\vantHoffSummary.pickle')
        
        return degSummarySheet

#refTemp = 60 
#Tf = 1.41
#x = .64 
#Ichamber = 2189 
#currentDirectory = r'C:\Users\DHOLSAPP\Desktop\WorldMapProject\WorldMapProject'
#configType = 'Module Temperature(open_rack_polymer_thinfilm_steel)(C)'

#test = customCalculations.generateVantHoffSummarySheet(configType , refTemp, Tf , x , Ichamber , currentDirectory )


