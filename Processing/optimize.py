# -*- coding: utf-8 -*-
"""
Class to create a Optimized Tilt/Azimuth and combined Tilt/Azimuth

@author: Derek Holsapple
"""

import pandas as pd
import pvlib
import numpy as np
import pickle

from utility import utility

#from Processing.energyCalcs import energyCalcs
from energyCalcs import energyCalcs

class optimize:

   
    def optimizedTiltSummaryFramePickles(currentDirectory):  
        '''
        EXECUTION FUNCTION
        
        optimizedTiltsPickles()
        
        Create a summary frame of all the Optimized Tilts  
        
        @param currentDirectory   -string, Current working directory
        @param tiltDelta          -int, delta of degrees to optimize tilt         
                                 
        @return void              -pickle, summary datafraem of OptimizedTilt               
        '''  
        # Create a list of file names of optimal tilt processed tuples
        fileNames = utility.filesNameList( currentDirectory , 'optimizedTilt' )
        
        summary_df = pd.DataFrame(columns = ['Site Identifier Code', 
                                     'Station name',
                                     'Station State',
                                     'Site time zone (Universal time + or -)',
                                     'Site latitude',
                                     'Site longitude',                              
                                     'Site elevation (meters)',
                                     'Station country or political unit',
                                     'WMO region',
                                     'Time zone code',
                                     'Koppen-Geiger climate classification',
                                     'Optimal Tilt'
                                     ]) 
        for i in range( 0 , len( fileNames )):
            locationData = pd.read_pickle( currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_Optimization\\Pickle_Optimal_Tilt\\' + fileNames[i])
            summary_df = summary_df.append(locationData)
    
        with open(currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_Optimization_Summary\\OptimalTiltSummary.pickle' , 'wb') as f:
            pickle.dump(summary_df, f)
    
    
    
    
    def optimizedTiltsPickles(currentDirectory , tiltDelta ):
        '''
        EXECUTION FUNCTION
        
        optimizedTiltsPickles()
        
        Create a pickle containing site specific data (series) for all 
        locations and save it into a directory
        
        @param currentDirectory   -string, Current working directory
        @param tiltDelta          -int, delta of degrees to optimize tilt         
                                 
        @return void              -pickle, series of site location data with optimized tilt               
        '''     
        # Delete files in directory
        utility.deleteAllFiles(currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_Optimization\\Pickle_Optimal_Tilt')
        
        # Create a list of file names of level_1 processed tuples
        fileNames = utility.filesNameList( currentDirectory , 'level_1_data' )
        
        for i in range(0, len(fileNames)):
            level_1_tuple = pd.read_pickle( currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_Level1\\' + fileNames[i])
            optimizedTilt = optimize.getOptimizeTilt( level_1_tuple , tiltDelta )
            print(i)
            location_series , level_1_data_df = level_1_tuple
            location_series['Optimal Tilt'] = optimizedTilt
            
            #TODO Add the dataframe as a tuple and then you will have all the data.... need to create a function to create another frame here
            with open(currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_Optimization\\Pickle_Optimal_Tilt\\' + fileNames[i], 'wb') as f:
                pickle.dump(location_series, f)

    
    
    
    
    
    def getOptimizeTilt( level_1_tuple , tiltDelta ):
        '''
        HELPER FUNCTION
        
        optimizeTilt()
        
        optimize the tilt of a given location based on the highest summation of 
        relative power.  Select the delta of degrees to test.  
        
        Example: If latitude tilt is 45(degrees) and delta was set to 15(degrees)
            All tilts from 30 to 60 degrees are measures by 1/10 incerements
            In this scenario there would be 300 different test cases
            
        @param level_1_tuple        -tuple,   (Series: Location Data,
                                               Dataframe: Level_1_ProcessedData)       
        @param tiltDelta               -int,   delta within latitude tilt to optimize 
                                           
        @return optimizedTilt      - float, optimized tilt to tenth degree accuracy               
        '''    
    

        #Unpack processed level_1 pickles
        locationData , level_1_df = level_1_tuple
        
        latitude = locationData.get(key = 'Site latitude')  
        #If the latitude is in the southern hemisphere of the globe then surface azimuth of the panel must be 0 degrees
        if latitude <= 0:
            module_azimuth = 0
        # If the latitude is in the northern hemisphere set the azimuth to 180
        else:
            module_azimuth = 180         

        latitude = abs(latitude)
        #Create a list of all the different delta test cases
        tilt_list = list( utility.range_inc( latitude - tiltDelta , latitude + tiltDelta , .1) ) 
        for i in range(0, len(tilt_list)):
            tilt_list[i] = round( tilt_list[i] , 1 )
        
        #Make a dataframe of necissary columns to save memory
        allTilts_df = level_1_df[['Solar Zenith(degrees)',
                                  'Solar Azimuth(degrees)',
                                  'Direct normal irradiance(W/m^2)',
                                  'Global horizontal irradiance(W/m^2)',
                                  'Diffuse horizontal irradiance(W/m^2)',
                                  'Albedo(ratio of reflected solar irradiance to GHI)',
                                  'Wind speed(m/s)',
                                  'Dry-bulb temperature(C)'
                                  ]]

        #let the games begin
        allTilts_df = pd.concat([allTilts_df]*len(tilt_list), ignore_index=True)
        
        #Create a array from the list of possible solar module angle tilts
        deltas_array = np.repeat(tilt_list, len(level_1_df))
        allTilts_df['Tilt'] = deltas_array       
        
        
        
        totalIrradiance_df = pvlib.irradiance.get_total_irradiance(allTilts_df['Tilt'], 
                                                                   module_azimuth, 
                                                                         allTilts_df['Solar Zenith(degrees)'], 
                                                                         allTilts_df['Solar Azimuth(degrees)'], 
                                                                         allTilts_df['Direct normal irradiance(W/m^2)'], 
                                                                         allTilts_df['Global horizontal irradiance(W/m^2)'], 
                                                                         allTilts_df['Diffuse horizontal irradiance(W/m^2)'], 
                                                                         dni_extra=None, 
                                                                         airmass=None, 
                                                                         albedo= allTilts_df['Albedo(ratio of reflected solar irradiance to GHI)'], 
                                                                         surface_type=None, 
                                                                         model= 'isotropic', 
                                                                         model_perez='allsitescomposite1990')
        #’open_rack_cell_glassback’ Module and Cell Temp with King Model (C)
        temp_open_rack_cell_glassback_df = pvlib.pvsystem.sapm_celltemp(totalIrradiance_df['poa_global'],
                                                            allTilts_df['Wind speed(m/s)'], 
                                                            allTilts_df['Dry-bulb temperature(C)'],
                                                            model = 'open_rack_cell_glassback' )
        #Build the needed frame to calculate the sum of relative power
        allTilts_df['Relative Power'] = energyCalcs.power( temp_open_rack_cell_glassback_df['temp_cell'] )

        sumOfPowerTiltList = allTilts_df.groupby(['Tilt'])['Relative Power'].sum()
        optimizedTilt = sumOfPowerTiltList.idxmax()

        return optimizedTilt
    



            
            
    
tiltDelta = 15

currentDirectory = r'C:\Users\DHOLSAPP\Desktop\WorldMapProject\WorldMapProject'

optimize.optimizedTiltsPickles(currentDirectory , tiltDelta )
optimize.optimizedTiltSummaryFramePickles(currentDirectory)

#fileName = '690150TYA.pickle'    
#level_1_tuple = pd.read_pickle( currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_Level1\\' + fileName)



#test = optimize.getOptimizeTilt( level_1_tuple , delta ) 
#test = optimize.getOptimizeTilt(currentDirectory, fileName,  latitude , delta )         
    











































































        
 