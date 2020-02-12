# -*- coding: utf-8 -*-
"""
Created on Tue May 28 12:10:47 2019

Process files to calculate the Plane of Irradiance.

Create a level one cleaning and store the dataframe as a pickle.  
The level one clean will process the plane of array irradiance along with
the solar Zenith.  The majorityof the procesing is conducted in this code.  


@author: Derek Holsapple
"""

import pandas as pd
#import glob
#import os 
import xlwings as xw
import pvlib
import pickle

#For XLwings ref
from Processing.energyCalcs import energyCalcs
from Processing.utility import utility

#from energyCalcs import energyCalcs
#from utility import utility

class finalOutputFrame:
    
    
    
    def level_1_df_toPickle( currentDirectory ):
        '''
        EXECUTION METHOD
        
        level_1_df()
        
        Create level 1 processed dataframe and store it into a .pickle file. 
        The level 1 processing will be a large computation calculating all site 
        locations withing the TMY3, CWEC and IWEC datasets.
        The results of computation will be stored as a pandas dataframe .pickle   
        Each location file will contain its own .pickle file.  
        Other energy calculations will be implemented in this function and
        stored in the dataframe 
        
        Method:
        1) Use a implementation of the NREL SPA algorithm described in [1] to calculate
            the solar positions including the Solar Zenith, Solar Azimuth, and Solar Elevation
        
        2) Calculate the Plane of Irradiance based off of Solar Zenith [2].
            
            I_{tot} = I_{beam} + I_{sky diffuse} + I_{ground}
            
        3) Calculate the solar module temperature based on the Kings model
    
            References
            ----------
            [1] I. Reda and A. Andreas, Solar position algorithm for solar radiation
            applications. Solar Energy, vol. 76, no. 5, pp. 577-589, 2004.
            NREL SPA code: http://rredc.nrel.gov/solar/codesandalgorithms/spa/
            
            [2] William F. Holmgren, Clifford W. Hansen, and Mark A. Mikofski. 
            “pvlib python: a python package for modeling solar energy systems.”
            Journal of Open Source Software, 3(29), 884, (2018). 
            https://doi.org/10.21105/joss.00884
            
        @ param currentDirectory  -String, of current working directory    
        @ param surface_tilt      -double, degrees of surface tilt
        @ param surface_azimuth   -double, degrees of surface azimuthe    
                                            
        @ return                  -void, stores processed .pickle files into directory
                                        \Pandas_Pickle_DataFrames\Pickle_Level1 
        '''       
        #XLWINGS user feedback
        wb = xw.Book(currentDirectory + '\Output_Tool.xlsm')
        mySheet = wb.sheets[0]
        # Create a list of file names of all the pickles to be processed
        fileNames = utility.filesNameList( currentDirectory , 'rawData' )
        
        finalSummary_df = pd.DataFrame(columns = [   'Site Identifier Code', 
                                                     'FileName',
                                                     'Station name',
                                                     'Station country or political unit',
                                                     'Station State',
                                                     'Data Source',
                                                     'Site latitude',
                                                     'Site longitude',
                                                     'Site time zone (Universal time + or -)',
                                                     'Site elevation (meters)',
                                                     'Koppen-Geiger climate classification',
                                                     
                                                     'Annual Global Horizontal Irradiance (GJ/m^-2)',
                                                     'Annual Direct Normal Irradiance (GJ/m^-2)',
                                                     'Annual Diffuse Horizontal Irradiance (GJ/m^-2)',
                                                     'Annual POA Global Irradiance (GJ/m^-2)',
                                                     'Annual POA Direct Irradiance (GJ/m^-2)',
                                                     'Annual POA Diffuse Irradiance (GJ/m^-2)',
                                                     'Annual POA Sky Diffuse Irradiance (GJ/m^-2)',
                                                     'Annual POA Ground Diffuse Irradiance (GJ/m^-2)',
                                                     'Annual Global UV Dose (MJ/y^-1)',
                                                     'Annual UV Dose at Latitude Tilt (MJ/y^-1)',
                                                      
                                                     'Sum of Relative Power',
                                                     'Avg of Relative Power',
        
                                                     'Annual Minimum Ambient Temperature (C)',
                                                     'Annual Average Ambient Temperature (C)',
                                                     'Annual Maximum Ambient Temperature (C)',
                                                     'Annual Range Ambient Temperature (C)',
                                                     'Average of Yearly Water Vapor Pressure(kPa)',
                                                     'Sum of Yearly Water Vapor Pressure(kPa)',
                                                     "Annual number of Hours Relative Humidity > to 85%",
                                                     'Sum of Yearly Dew(mmd-1)',

                                                     'Annual Average (98th Percentile) Cell Temperature__open_rack_cell_glassback (C)', 
                                                     'Annual Average (98th Percentile) Module Temperature__open_rack_cell_glassback (C)',
                                                     'Annual Minimum Module Temperature__open_rack_cell_glassback (C)',
                                                     'Annual Average Module Temperature__open_rack_cell_glassback (C)',
                                                     'Annual Maximum Module Temperature__open_rack_cell_glassback (C)',
                                                     'Annual Range of Module Temperature__open_rack_cell_glassback (C)',
                                                     'Solder Fatigue Damage__open_rack_cell_glassback', 
                                                     
                                                     'Annual Average (98th Percentile) Cell Temperature__roof_mount_cell_glassback (C)',
                                                     'Annual Average (98th Percentile) Module Temperature__roof_mount_cell_glassback (C)',
                                                     'Annual Minimum Module Temperature__roof_mount_cell_glassback (C)',
                                                     'Annual Average Module Temperature__roof_mount_cell_glassback (C)',
                                                     'Annual Maximum Module Temperature__roof_mount_cell_glassback (C)',
                                                     'Annual Range of Module Temperature__roof_mount_cell_glassback (C)',
                                                     'Solder Fatigue Damage__roof_mount_cell_glassback',                                                          
                                                     
                                                     'Annual Average (98th Percentile) Cell Temperature__open_rack_cell_polymerback (C)',
                                                     'Annual Average (98th Percentile) Module Temperature__open_rack_cell_polymerback (C)',
                                                     'Annual Minimum Module Temperature__open_rack_cell_polymerback (C)',
                                                     'Annual Average Module Temperature__open_rack_cell_polymerback (C)',
                                                     'Annual Maximum Module Temperature__open_rack_cell_polymerback (C)',
                                                     'Annual Range of Module Temperature__open_rack_cell_polymerback (C)', 
                                                     'Solder Fatigue Damage__roof_mount_open_rack_cell_polymerback',                                                         
                                                     
                                                     'Annual Average (98th Percentile) Cell Temperature__insulated_back_polymerback (C)',
                                                     'Annual Average (98th Percentile) Module Temperature__insulated_back_polymerback (C)',
                                                     'Annual Minimum Module Temperature__insulated_back_polymerback (C)',
                                                     'Annual Average Module Temperature__insulated_back_polymerback (C)',
                                                     'Annual Maximum Module Temperature__insulated_back_polymerback (C)',
                                                     'Annual Range of Module Temperature__insulated_back_polymerback (C)',                                                         
                                                     'Solder Fatigue Damage__insulated_back_polymerback', 
                                                     
                                                     'Annual Average (98th Percentile) Cell Temperature__open_rack_polymer_thinfilm_steel (C)',
                                                     'Annual Average (98th Percentile) Module Temperature__open_rack_polymer_thinfilm_steel (C)',
                                                     'Annual Minimum Module Temperature__open_rack_polymer_thinfilm_steel (C)',
                                                     'Annual Average Module Temperature__open_rack_polymer_thinfilm_steel (C)',
                                                     'Annual Maximum Module Temperature__open_rack_polymer_thinfilm_steel (C)',
                                                     'Annual Range of Module Temperature__open_rack_polymer_thinfilm_steel (C)',                                                         
                                                     'Solder Fatigue Damage__open_rack_polymer_thinfilm_steel', 
                                                     
                                                     'Annual Average (98th Percentile) Cell Temperature__22x_concentrator_tracker (C)',
                                                     'Annual Average (98th Percentile) Module Temperature__22x_concentrator_tracker (C)', 
                                                     'Annual Minimum Module Temperature__22x_concentrator_tracker (C)',
                                                     'Annual Average Module Temperature__22x_concentrator_tracker (C)',
                                                     'Annual Maximum Module Temperature__22x_concentrator_tracker (C)',
                                                     'Annual Range of Module Temperature__22x_concentrator_tracker (C)',
                                                     'Solder Fatigue Damage__22x_concentrator_tracker', 

                                                      ])
        
        #Output to the user how many files need to be processed via XLWings
        wb.sheets[mySheet].range(67,6).value = len(fileNames)
          
        for i in range (0 , len(fileNames)):
            
            #Import the aggregated tuple of each site (tuple was aggregated from RawDataImport.class)
            locationData , raw_df = pd.read_pickle( currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_RawData\\' + fileNames[i])
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
            
            # Calculates the angle of incidence of the solar vector on a surface. 
            # This is the angle between the solar vector and the surface normal.
            aoi = pvlib.irradiance.aoi(surface_tilt, surface_azimuth,
                           solarPosition_df['apparent_zenith'], solarPosition_df['azimuth'])
            #Calculate the angle of incidence
            level_1_df['Angle of incidence'] = aoi.values
            ##############################            
            # Calculate the POA
            totalIrradiance_df = pvlib.irradiance.get_total_irradiance(surface_tilt, 
                                                                             surface_azimuth, 
                                                                             level_1_df['Solar Zenith'], 
                                                                             level_1_df['Solar Azimuth'], 
                                                                             level_1_df['Direct normal irradiance'], 
                                                                             level_1_df['Global horizontal irradiance'], 
                                                                             level_1_df['Diffuse horizontal irradiance'], 
                                                                             dni_extra=None, 
                                                                             airmass=None, 
                                                                             albedo= level_1_df['Corrected Albedo'], 
                                                                             surface_type=None, 
                                                                             model= 'isotropic', 
                                                                             model_perez='allsitescomposite1990')   
            level_1_df['POA Diffuse'] = totalIrradiance_df['poa_diffuse'].values
            level_1_df['POA Direct'] = totalIrradiance_df['poa_direct'].values
            level_1_df['POA Global'] = totalIrradiance_df['poa_global'].values
            level_1_df['POA Ground Diffuse'] = totalIrradiance_df['poa_ground_diffuse'].values
            level_1_df['POA Sky Diffuse'] = totalIrradiance_df['poa_sky_diffuse'].values
            ##############################
            # Calculate the Module/Cell Temperature for different configurations
            # using the King model from pvlib
    
            #’open_rack_cell_glassback’ OUTPUT = Module Temperature/Cell Temperature(C)
            temp_open_rack_cell_glassback_df = pvlib.pvsystem.sapm_celltemp(level_1_df['POA Global'],
                                                                level_1_df['Wind speed'], 
                                                                level_1_df['Dry-bulb temperature'],
                                                                model = 'open_rack_cell_glassback' )
            #’roof_mount_cell_glassback’ OUTPUT = Module Temperature/Cell Temperature(C)
            temp_roof_mount_cell_glassback_df = pvlib.pvsystem.sapm_celltemp(level_1_df['POA Global'],
                                                                level_1_df['Wind speed'], 
                                                                level_1_df['Dry-bulb temperature'],
                                                                model = 'roof_mount_cell_glassback')        
            #’open_rack_cell_polymerback’ OUTPUT = Module Temperature/Cell Temperature(C)
            temp_open_rack_cell_polymerback_df = pvlib.pvsystem.sapm_celltemp(level_1_df['POA Global'],
                                                                level_1_df['Wind speed'], 
                                                                level_1_df['Dry-bulb temperature'],
                                                                model = 'open_rack_cell_polymerback')        
            #’insulated_back_polymerback’  OUTPUT = Module Temperature/Cell Temperature(C)
            temp_insulated_back_polymerback_df = pvlib.pvsystem.sapm_celltemp(level_1_df['POA Global'],
                                                                level_1_df['Wind speed'], 
                                                                level_1_df['Dry-bulb temperature'],
                                                                model = 'insulated_back_polymerback')        
            #’open_rack_polymer_thinfilm_steel’  OUTPUT = Module Temperature/Cell Temperature(C)
            temp_open_rack_polymer_thinfilm_steel_df = pvlib.pvsystem.sapm_celltemp(level_1_df['POA Global'],
                                                                level_1_df['Wind speed'], 
                                                                level_1_df['Dry-bulb temperature'],
                                                                model = 'open_rack_polymer_thinfilm_steel') 
            #’22x_concentrator_tracker’  OUTPUT = Module Temperature/Cell Temperature(C)
            temp_22x_concentrator_tracker_df = pvlib.pvsystem.sapm_celltemp(level_1_df['POA Global'],
                                                                level_1_df['Wind speed'], 
                                                                level_1_df['Dry-bulb temperature'],
                                                                model = '22x_concentrator_tracker')        
            # Add the module temp data to the level 1 frame 
            level_1_df['Cell Temperature(open_rack_cell_glassback)'] = temp_open_rack_cell_glassback_df['temp_cell'].values.tolist()
            level_1_df['Module Temperature(open_rack_cell_glassback)'] = temp_open_rack_cell_glassback_df['temp_module'].values.tolist()
            
            level_1_df['Cell Temperature(roof_mount_cell_glassback)'] = temp_roof_mount_cell_glassback_df['temp_cell'].values.tolist()
            level_1_df['Module Temperature(roof_mount_cell_glassback)'] = temp_roof_mount_cell_glassback_df['temp_module'].values.tolist()        
            
            level_1_df['Cell Temperature(open_rack_cell_polymerback)'] = temp_open_rack_cell_polymerback_df['temp_cell'].values.tolist()
            level_1_df['Module Temperature(open_rack_cell_polymerback)'] = temp_open_rack_cell_polymerback_df['temp_module'].values.tolist()        
            
            level_1_df['Cell Temperature(insulated_back_polymerback)'] = temp_insulated_back_polymerback_df['temp_cell'].values.tolist()
            level_1_df['Module Temperature(insulated_back_polymerback)'] = temp_insulated_back_polymerback_df['temp_module'].values.tolist()        
            
            level_1_df['Cell Temperature(open_rack_polymer_thinfilm_steel)'] = temp_open_rack_polymer_thinfilm_steel_df['temp_cell'].values.tolist()
            level_1_df['Module Temperature(open_rack_polymer_thinfilm_steel)'] = temp_open_rack_polymer_thinfilm_steel_df['temp_module'].values.tolist()        
            
            level_1_df['Cell Temperature(22x_concentrator_tracker)'] = temp_22x_concentrator_tracker_df['temp_cell'].values.tolist()
            level_1_df['Module Temperature(22x_concentrator_tracker)'] = temp_22x_concentrator_tracker_df['temp_module'].values.tolist()        

            # Calculate the top 2% 
            #Determine how many elements are equal to 2% of the length of the data
            top2Precent = int( len( level_1_df ) * .02 )
            # Pull out the top 2% of the data.  8760 points will take the highest 175 values          
            open_rack_cell_glassback_top2Precent_Cell_Temp = level_1_df.nlargest( top2Precent , 'Cell Temperature(open_rack_cell_glassback)' ) 
            open_rack_cell_glassback_top2Precent_Module_Temp = level_1_df.nlargest( top2Precent , 'Module Temperature(open_rack_cell_glassback)' )
            ##############################            
            roof_mount_cell_glassback_top2Precent_Cell_Temp = level_1_df.nlargest( top2Precent , 'Cell Temperature(roof_mount_cell_glassback)' ) 
            roof_mount_cell_glassback_top2Precent_Module_Temp = level_1_df.nlargest( top2Precent , 'Module Temperature(roof_mount_cell_glassback)' )        
            ##############################            
            open_rack_cell_polymerback_top2Precent_Cell_Temp = level_1_df.nlargest( top2Precent , 'Cell Temperature(open_rack_cell_polymerback)' ) 
            open_rack_cell_polymerback_top2Precent_Module_Temp = level_1_df.nlargest( top2Precent , 'Module Temperature(open_rack_cell_polymerback)' )        
            ##############################            
            insulated_back_polymerback_top2Precent_Cell_Temp = level_1_df.nlargest( top2Precent , 'Cell Temperature(insulated_back_polymerback)' ) 
            insulated_back_polymerback_top2Precent_Module_Temp = level_1_df.nlargest( top2Precent , 'Module Temperature(insulated_back_polymerback)' )        
            ##############################            
            open_rack_polymer_thinfilm_steel_top2Precent_Cell_Temp = level_1_df.nlargest( top2Precent , 'Cell Temperature(open_rack_polymer_thinfilm_steel)' ) 
            open_rack_polymer_thinfilm_steel_top2Precent_Module_Temp = level_1_df.nlargest( top2Precent , 'Module Temperature(open_rack_polymer_thinfilm_steel)' )        
            ##############################              
            _22x_concentrator_tracker_top2Precent_Cell_Temp = level_1_df.nlargest( top2Precent , 'Cell Temperature(22x_concentrator_tracker)' ) 
            _22x_concentrator_tracker_top2Precent_Module_Temp = level_1_df.nlargest( top2Precent , 'Module Temperature(22x_concentrator_tracker)' )        

            # Find the average of the top 98th percentile for Module/Cell Temperature 
            average98Cell_open_rack_cell_glassback = open_rack_cell_glassback_top2Precent_Cell_Temp['Cell Temperature(open_rack_cell_glassback)'].mean(axis = 0, skipna = True) 
            average98Module_open_rack_cell_glassback = open_rack_cell_glassback_top2Precent_Module_Temp['Module Temperature(open_rack_cell_glassback)'].mean(axis = 0, skipna = True) 
            ##############################            
            average98Cell_roof_mount_cell_glassback = roof_mount_cell_glassback_top2Precent_Cell_Temp['Cell Temperature(roof_mount_cell_glassback)'].mean(axis = 0, skipna = True) 
            average98Module_roof_mount_cell_glassback = roof_mount_cell_glassback_top2Precent_Module_Temp['Module Temperature(roof_mount_cell_glassback)'].mean(axis = 0, skipna = True)         
            ##############################            
            average98CellTemp_open_rack_cell_polymerback = open_rack_cell_polymerback_top2Precent_Cell_Temp['Cell Temperature(open_rack_cell_polymerback)'].mean(axis = 0, skipna = True) 
            average98Module_open_rack_cell_polymerback = open_rack_cell_polymerback_top2Precent_Module_Temp['Module Temperature(open_rack_cell_polymerback)'].mean(axis = 0, skipna = True)         
            ##############################            
            average98Cell_insulated_back_polymerback = insulated_back_polymerback_top2Precent_Cell_Temp['Cell Temperature(insulated_back_polymerback)'].mean(axis = 0, skipna = True) 
            average98Module_insulated_back_polymerback =  insulated_back_polymerback_top2Precent_Module_Temp['Module Temperature(insulated_back_polymerback)'].mean(axis = 0, skipna = True)         
            ##############################            
            average98Cell_open_rack_polymer_thinfilm_steel = open_rack_polymer_thinfilm_steel_top2Precent_Cell_Temp['Cell Temperature(open_rack_polymer_thinfilm_steel)'].mean(axis = 0, skipna = True) 
            average98Module_open_rack_polymer_thinfilm_steel = open_rack_polymer_thinfilm_steel_top2Precent_Module_Temp['Module Temperature(open_rack_polymer_thinfilm_steel)'].mean(axis = 0, skipna = True)         
            ##############################            
            average98Cell_22x_concentrator_tracker = _22x_concentrator_tracker_top2Precent_Cell_Temp['Cell Temperature(22x_concentrator_tracker)'].mean(axis = 0, skipna = True) 
            average98Module_22x_concentrator_tracker = _22x_concentrator_tracker_top2Precent_Module_Temp['Module Temperature(22x_concentrator_tracker)'].mean(axis = 0, skipna = True)         

            
            #Calculate the dew point yield for each location.  Find the sum of all hourly data for a yearly yield
            siteElevation = locationData.get(key = 'Site elevation (meters)')/1000 #Dew Yield function requires kilometers
            level_1_df['Dew Yield'] = energyCalcs.dewYield( siteElevation ,
                                                           level_1_df['Dew-point temperature'].values, 
                                                           level_1_df['Dry-bulb temperature'].values ,
                                                           level_1_df['Wind speed'].values ,
                                                           level_1_df['Total sky cover(okta)'].values)  
            #If the values from Dew Yield Calc are less than 0 replace with 0, "can not have negative dew yield"
            level_1_df['Dew Yield'].values[level_1_df['Dew Yield'].values < 0] = 0
            

            #get the sum of all the dew produced that year.  
            sumOfHourlyDew = level_1_df['Dew Yield'].sum(axis = 0, skipna = True)
            
            level_1_df['Water Vapor Pressure (kPa)'] = energyCalcs.waterVaporPressure( raw_df['Dew-point temperature'] )         
            avgWaterVaporPressure = level_1_df['Water Vapor Pressure (kPa)'].mean(skipna = True)         
            sumWaterVaporPressure = level_1_df['Water Vapor Pressure (kPa)'].sum(skipna = True)      
            #Calculate the sum of yearly GHI
            sumOfGHI = energyCalcs.whToGJ( level_1_df['Global horizontal irradiance'].sum(axis = 0, skipna = True) )
            #Calculate the sum of yearly DNI
            sumOfDNI = energyCalcs.whToGJ( level_1_df['Direct normal irradiance'].sum(axis = 0, skipna = True) )
            #Calculate the sum of yearly DHI
            sumOfDHI = energyCalcs.whToGJ( level_1_df['Diffuse horizontal irradiance'].sum(axis = 0, skipna = True) )
            #Calculate the sum of yearly POA global in Giga Joules
            sumOfPOA_Global = energyCalcs.whToGJ( totalIrradiance_df['poa_global'].sum(axis = 0, skipna = True) )
            #Calculate the sum of yearly POA Direct in Giga Jouls
            sumOfPOA_Direct = energyCalcs.whToGJ( totalIrradiance_df['poa_direct'].sum(axis = 0, skipna = True) )
            #Calculate the sum of yearly POA Diffuse
            sumOfPOA_Diffuse = energyCalcs.whToGJ( totalIrradiance_df['poa_diffuse'].sum(axis = 0, skipna = True) )
            #Calculate the sum of yearly POA Sky Diffuse
            sumOfPOA_SkyDiffuse = energyCalcs.whToGJ( totalIrradiance_df['poa_sky_diffuse'].sum(axis = 0, skipna = True) )
            #Calculate the sum of yearly POA Ground Diffuse
            sumOfPOA_GroundDiffuse = energyCalcs.whToGJ( totalIrradiance_df['poa_ground_diffuse'].sum(axis = 0, skipna = True) )
            #Calculate the Global UV Dose, 5% of the annual GHI
            global_UV_Dose = energyCalcs.gJtoMJ( sumOfGHI * .05 )
            #Calculate the annual UV Dose at Latitude Tilt, 5% of the annual GHI
            #Estimate as 5% of global plane of irradiance
            sumOfPOA_Global = energyCalcs.gJtoMJ( energyCalcs.whToGJ(level_1_df['POA Global'].sum(axis = 0, skipna = True) ) )
            uV_Dose_atLatitude_Tilt = sumOfPOA_Global * .05
            #Calculate the annual minimum ambient temperature
            minimum_Ambient_Temperature = level_1_df['Dry-bulb temperature'].min()
            #Calculate the annual average ambient temperature
            average_Ambient_Temperature = level_1_df['Dry-bulb temperature'].mean()
            #Calculate the annual maximum ambient temperature
            maximum_Ambient_Temperature = level_1_df['Dry-bulb temperature'].max()
            #Calculate the annual range ambient temperature
            ambient_Temperature_Range = maximum_Ambient_Temperature - minimum_Ambient_Temperature                                                    
            hoursRHabove85 = energyCalcs.hoursRH_Above85( level_1_df['Relative humidity'] )
            
            # Relative Power calculations 
            level_1_df['Power'] = energyCalcs.power(level_1_df['Cell Temperature(open_rack_cell_glassback)'] , level_1_df['POA Global'])
            sumOfPower = level_1_df['Power'].sum(axis = 0, skipna = True)
            avgOfPower = level_1_df['Power'].mean()          

            #########
            #Solar Module fixture temperature summary stats
            ##############################
            #Calculate the annual minimum ambient temperature
            minimum_Module_Temp_open_rack_cell_glassback = level_1_df['Module Temperature(open_rack_cell_glassback)'].min()
            #Calculate the annual average ambient temperature        
            average_Module_Temp_open_rack_cell_glassback = level_1_df['Module Temperature(open_rack_cell_glassback)'].mean()
            #Calculate the annual maximum ambient temperature        
            maximum_Module_Temp_open_rack_cell_glassback = level_1_df['Module Temperature(open_rack_cell_glassback)'].max()
            #Calculate the annual range ambient temperature        
            range_Module_Temp_open_rack_cell_glassback = maximum_Module_Temp_open_rack_cell_glassback - minimum_Module_Temp_open_rack_cell_glassback
            #Calculate the Solder Fatigue 
            solderFatigue_open_rack_cell_glassback = energyCalcs.solderFatigue(  level_1_df['Local Date Time'] ,  level_1_df['Cell Temperature(open_rack_cell_glassback)'] , 54.8)
            ##############################            
            #Calculate the annual minimum ambient temperature
            minimum_Module_Temp_roof_mount_cell_glassback = level_1_df['Module Temperature(roof_mount_cell_glassback)'].min()
            #Calculate the annual average ambient temperature        
            average_Module_Temp_roof_mount_cell_glassback = level_1_df['Module Temperature(roof_mount_cell_glassback)'].mean()
            #Calculate the annual maximum ambient temperature        
            maximum_Module_Temp_roof_mount_cell_glassback = level_1_df['Module Temperature(roof_mount_cell_glassback)'].max()
            #Calculate the annual range ambient temperature        
            range_Module_Temp_roof_mount_cell_glassback = maximum_Module_Temp_roof_mount_cell_glassback - minimum_Module_Temp_roof_mount_cell_glassback
            #Calculate the Solder Fatigue 
            solderFatigue_roof_mount_cell_glassback = energyCalcs.solderFatigue(  level_1_df['Local Date Time'] ,  level_1_df['Cell Temperature(roof_mount_cell_glassback)'] , 54.8)            
            ##############################            
            #Calculate the annual minimum ambient temperature
            minimum_Module_Temp_open_rack_cell_polymerback = level_1_df['Module Temperature(open_rack_cell_polymerback)'].min()
            #Calculate the annual average ambient temperature        
            average_Module_Temp_open_rack_cell_polymerback = level_1_df['Module Temperature(open_rack_cell_polymerback)'].mean()
            #Calculate the annual maximum ambient temperature        
            maximum_Module_Temp_open_rack_cell_polymerback = level_1_df['Module Temperature(open_rack_cell_polymerback)'].max()
            #Calculate the annual range ambient temperature        
            range_Module_Temp_open_rack_cell_polymerback = maximum_Module_Temp_open_rack_cell_polymerback - minimum_Module_Temp_open_rack_cell_polymerback
            #Calculate the Solder Fatigue 
            solderFatigue_open_rack_cell_polymerback = energyCalcs.solderFatigue(  level_1_df['Local Date Time'] ,  level_1_df['Cell Temperature(open_rack_cell_polymerback)'] , 54.8)            
            ##############################                    
            #Calculate the annual minimum ambient temperature
            minimum_Module_Temp_insulated_back_polymerback = level_1_df['Module Temperature(insulated_back_polymerback)'].min()
            #Calculate the annual average ambient temperature        
            average_Module_Temp_insulated_back_polymerback = level_1_df['Module Temperature(insulated_back_polymerback)'].mean()
            #Calculate the annual maximum ambient temperature        
            maximum_Module_Temp_insulated_back_polymerback = level_1_df['Module Temperature(insulated_back_polymerback)'].max()
            #Calculate the annual range ambient temperature        
            range_Module_Temp_insulated_back_polymerback = maximum_Module_Temp_insulated_back_polymerback - minimum_Module_Temp_insulated_back_polymerback
            #Calculate the Solder Fatigue 
            solderFatigue_insulated_back_polymerback = energyCalcs.solderFatigue(  level_1_df['Local Date Time'] ,  level_1_df['Cell Temperature(insulated_back_polymerback)'] , 54.8)            
            ##############################            
            #Calculate the annual minimum ambient temperature
            minimum_Module_Temp_open_rack_polymer_thinfilm_steel = level_1_df['Module Temperature(open_rack_polymer_thinfilm_steel)'].min()
            #Calculate the annual average ambient temperature        
            average_Module_Temp_open_rack_polymer_thinfilm_steel = level_1_df['Module Temperature(open_rack_polymer_thinfilm_steel)'].mean()
            #Calculate the annual maximum ambient temperature        
            maximum_Module_Temp_open_rack_polymer_thinfilm_steel = level_1_df['Module Temperature(open_rack_polymer_thinfilm_steel)'].max()
            #Calculate the annual range ambient temperature        
            range_Module_Temp_open_rack_polymer_thinfilm_steel = maximum_Module_Temp_open_rack_polymer_thinfilm_steel - minimum_Module_Temp_open_rack_polymer_thinfilm_steel
            #Calculate the Solder Fatigue 
            solderFatigue_open_rack_polymer_thinfilm_steel = energyCalcs.solderFatigue(  level_1_df['Local Date Time'] ,  level_1_df['Cell Temperature(open_rack_polymer_thinfilm_steel)'] , 54.8)            
            ##############################                    
            #Calculate the annual minimum ambient temperature
            minimum_Module_Temp_22x_concentrator_tracker = level_1_df['Module Temperature(22x_concentrator_tracker)'].min()
            #Calculate the annual average ambient temperature        
            average_Module_Temp_22x_concentrator_tracker = level_1_df['Module Temperature(22x_concentrator_tracker)'].mean()
            #Calculate the annual maximum ambient temperature        
            maximum_Module_Temp_22x_concentrator_tracker = level_1_df['Module Temperature(22x_concentrator_tracker)'].max()
            #Calculate the annual range ambient temperature        
            range_Module_Temp_22x_concentrator_tracker = maximum_Module_Temp_22x_concentrator_tracker - minimum_Module_Temp_22x_concentrator_tracker
            #Calculate the Solder Fatigue 
            solderFatigue_22x_concentrator_tracker = energyCalcs.solderFatigue(  level_1_df['Local Date Time'] ,  level_1_df['Cell Temperature(22x_concentrator_tracker)'] , 54.8)            

            # Add the data source to the location data description
            dataSource = pd.Series( utility.dataSource(fileNames[i]), index=['Data Source'])
            locationData = locationData.append( dataSource )

            level_1_df = level_1_df.reindex(columns = ['Local Date Time',
                                                       'Universal Date Time',
                                                       'Local Solar Time',
                                                       'Hourly Local Solar Time',
                                                       'Albedo',
                                                       'Corrected Albedo',
                                                       'Dry-bulb temperature',
                                                       'Dew-point temperature',
                                                       'Relative humidity',
                                                       'Station pressure',
                                                       'Wind direction',
                                                       'Wind speed',
                                                       'Total sky cover',
                                                       'Total sky cover(okta)',
                                                       'Dew Yield',
                                                       'Water Vapor Pressure (kPa)',
                                                       'Global horizontal irradiance',
                                                       'Direct normal irradiance',
                                                       'Diffuse horizontal irradiance',
                                                       'Solar Zenith',
                                                       'Solar Azimuth',
                                                       'Solar Elevation',
                                                       'Angle of incidence',
                                                       'POA Diffuse',
                                                       'POA Direct',
                                                       'POA Global',
                                                       'POA Ground Diffuse',
                                                       'POA Sky Diffuse',
                                                       'Power',
                                                       'Rate of Degradation',
                                                       'Cell Temperature(open_rack_cell_glassback)',
                                                       'Module Temperature(open_rack_cell_glassback)',
                                                       'Cell Temperature(roof_mount_cell_glassback)',
                                                       'Module Temperature(roof_mount_cell_glassback)', 
                                                       'Cell Temperature(open_rack_cell_polymerback)',
                                                       'Module Temperature(open_rack_cell_polymerback)',
                                                       'Cell Temperature(insulated_back_polymerback)',
                                                       'Module Temperature(insulated_back_polymerback)', 
                                                       'Cell Temperature(open_rack_polymer_thinfilm_steel)',
                                                       'Module Temperature(open_rack_polymer_thinfilm_steel)',
                                                       'Cell Temperature(22x_concentrator_tracker)',
                                                       'Module Temperature(22x_concentrator_tracker)'                                                       
                                                       ]) 
            #Put metrics in the final column names
            level_1_df.rename(columns = { 'Albedo' :'Albedo(ratio of reflected solar irradiance to GHI)', 
                                          'Corrected Albedo':'Corrected Albedo(ratio of reflected solar irradiance to GHI)', 
                                          'Dry-bulb temperature':'Dry-bulb temperature(C)',
                                          'Dew-point temperature':'Dew-point temperature(C)',
                                          'Relative humidity':'Relative humidity(%)',
                                          'Station pressure':'Station pressure(mbar)',
                                          'Wind direction':'Wind direction(degrees)',
                                          'Wind speed':'Wind speed(m/s)',
                                          'Total sky cover':'Total sky cover(tenths)',
                                          'Total sky cover(okta)':'Total sky cover(okta)',
                                          'Dew Yield' :'Dew Yield(mmd-1)', 
                                          'Global horizontal irradiance':'Global horizontal irradiance(W/m^2)', 
                                          'Direct normal irradiance':'Direct normal irradiance(W/m^2)',
                                          'Diffuse horizontal irradiance':'Diffuse horizontal irradiance(W/m^2)',
                                          'Solar Zenith':'Solar Zenith(degrees)',
                                          'Solar Azimuth':'Solar Azimuth(degrees)',
                                          'Solar Elevation':'Solar Elevation(degrees)',
                                          'Angle of incidence':'Angle of incidence(degrees)',
                                          'POA Diffuse':'POA Diffuse(W/m^2)',
                                          'POA Direct':'POA Direct(W/m^2)',                                          
                                          'POA Global' :'POA Global(W/m^2)', 
                                          'POA Ground Diffuse':'POA Ground Diffuse(W/m^2)', 
                                          'POA Sky Diffuse':'POA Sky Diffuse(W/m^2)',
                                          'Rate of Degradation':'Rate of Degradation',
                                          'Cell Temperature(open_rack_cell_glassback)':'Cell Temperature(open_rack_cell_glassback)(C)',
                                          'Module Temperature(open_rack_cell_glassback)':'Module Temperature(open_rack_cell_glassback)(C)',
                                          'Cell Temperature(roof_mount_cell_glassback)':'Cell Temperature(roof_mount_cell_glassback)(C)',
                                          'Module Temperature(roof_mount_cell_glassback)':'Module Temperature(roof_mount_cell_glassback)(C)',
                                          'Cell Temperature(open_rack_cell_polymerback)':'Cell Temperature(open_rack_cell_polymerback)(C)',
                                          'Module Temperature(open_rack_cell_polymerback)':'Module Temperature(open_rack_cell_polymerback)(C)',
                                          'Cell Temperature(insulated_back_polymerback)':'Cell Temperature(insulated_back_polymerback)(C)',
                                          'Module Temperature(insulated_back_polymerback)':'Module Temperature(insulated_back_polymerback)(C)',
                                          'Cell Temperature(open_rack_polymer_thinfilm_steel)':'Cell Temperature(open_rack_polymer_thinfilm_steel)(C)',                                          
                                          'Module Temperature(open_rack_polymer_thinfilm_steel)' :'Module Temperature(open_rack_polymer_thinfilm_steel)(C)', 
                                          'Cell Temperature(22x_concentrator_tracker)':'Cell Temperature(22x_concentrator_tracker)(C)', 
                                          'Module Temperature(22x_concentrator_tracker)':'Module Temperature(22x_concentrator_tracker)(C)'
                                          }, inplace = True)
    
            #Store the level 1 processed Data into a tuple as a pickle file
            level1_tuple = ( locationData , level_1_df )
            with open(currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_Level1\\' + fileNames[i], 'wb') as f:
                pickle.dump(level1_tuple, f)

            #########
            #LEVEL 1 SITE SPECIFC DATAFRAME COMPLETE
            #########
        
            # Create a summary frame of all locations
    
            finalSummary_df = finalSummary_df.append({'Site Identifier Code':  locationData.get(key = 'Site Identifier Code'), 
                                                      'FileName': locationData.get(key = 'FileName'),
                                                      'Station name': locationData.get(key = 'Station name'),  
                                                      'Station country or political unit': locationData.get(key = 'Station country or political unit'),
                                                      'Station State': locationData.get(key = 'Station State'),
                                                      'Data Source': locationData.get(key = 'Data Source'), 
                                                      'Site latitude': locationData.get(key = 'Site latitude'), 
                                                      'Site longitude': locationData.get(key = 'Site longitude'),
                                                      'Site time zone (Universal time + or -)': locationData.get(key = 'Site time zone (Universal time + or -)'),
                                                      'Site elevation (meters)': locationData.get(key = 'Site elevation (meters)'),
                                                      'Koppen-Geiger climate classification': locationData.get(key = 'Koppen-Geiger climate classification'),
                                                      
                                                      'Annual Global Horizontal Irradiance (GJ/m^-2)':sumOfGHI,
                                                      'Annual Direct Normal Irradiance (GJ/m^-2)':sumOfDNI,
                                                      'Annual Diffuse Horizontal Irradiance (GJ/m^-2)':sumOfDHI,
                                                      'Annual POA Global Irradiance (GJ/m^-2)':sumOfPOA_Global,
                                                      'Annual POA Direct Irradiance (GJ/m^-2)':sumOfPOA_Direct,
                                                      'Annual POA Diffuse Irradiance (GJ/m^-2)':sumOfPOA_Diffuse,
                                                      'Annual POA Sky Diffuse Irradiance (GJ/m^-2)':sumOfPOA_SkyDiffuse,
                                                      'Annual POA Ground Diffuse Irradiance (GJ/m^-2)':sumOfPOA_GroundDiffuse,
                                                      'Annual Global UV Dose (MJ/y^-1)':global_UV_Dose,
                                                      'Annual UV Dose at Latitude Tilt (MJ/y^-1)':uV_Dose_atLatitude_Tilt,
                                                      
                                                      'Sum of Relative Power':sumOfPower,
                                                      'Avg of Relative Power':avgOfPower,
                                                     
                                                      'Annual Minimum Ambient Temperature (C)':minimum_Ambient_Temperature,
                                                      'Annual Average Ambient Temperature (C)':average_Ambient_Temperature,
                                                      'Annual Maximum Ambient Temperature (C)':maximum_Ambient_Temperature,
                                                      'Annual Range Ambient Temperature (C)':ambient_Temperature_Range,
                                                      'Average of Yearly Water Vapor Pressure(kPa)':avgWaterVaporPressure,
                                                      'Sum of Yearly Water Vapor Pressure(kPa)':sumWaterVaporPressure,
                                                      "Annual number of Hours Relative Humidity > to 85%":hoursRHabove85,
                                                      'Sum of Yearly Dew(mmd-1)':sumOfHourlyDew,
    
                                                      'Annual Average (98th Percentile) Cell Temperature__open_rack_cell_glassback (C)':average98Cell_open_rack_cell_glassback, 
                                                      'Annual Average (98th Percentile) Module Temperature__open_rack_cell_glassback (C)':average98Module_open_rack_cell_glassback,
                                                      'Annual Minimum Module Temperature__open_rack_cell_glassback (C)':minimum_Module_Temp_open_rack_cell_glassback,
                                                      'Annual Average Module Temperature__open_rack_cell_glassback (C)':average_Module_Temp_open_rack_cell_glassback,
                                                      'Annual Maximum Module Temperature__open_rack_cell_glassback (C)':maximum_Module_Temp_open_rack_cell_glassback,
                                                      'Annual Range of Module Temperature__open_rack_cell_glassback (C)':range_Module_Temp_open_rack_cell_glassback,
                                                      'Solder Fatigue Damage__open_rack_cell_glassback':solderFatigue_open_rack_cell_glassback, 
                                                     
                                                      'Annual Average (98th Percentile) Cell Temperature__roof_mount_cell_glassback (C)':average98Cell_roof_mount_cell_glassback,
                                                      'Annual Average (98th Percentile) Module Temperature__roof_mount_cell_glassback (C)':average98Module_roof_mount_cell_glassback,
                                                      'Annual Minimum Module Temperature__roof_mount_cell_glassback (C)':minimum_Module_Temp_roof_mount_cell_glassback,
                                                      'Annual Average Module Temperature__roof_mount_cell_glassback (C)':average_Module_Temp_roof_mount_cell_glassback,
                                                      'Annual Maximum Module Temperature__roof_mount_cell_glassback (C)':maximum_Module_Temp_roof_mount_cell_glassback,
                                                      'Annual Range of Module Temperature__roof_mount_cell_glassback (C)':range_Module_Temp_roof_mount_cell_glassback,                                                         
                                                      'Solder Fatigue Damage__roof_mount_cell_glassback':solderFatigue_roof_mount_cell_glassback,                                                      
                                                        
                                                      'Annual Average (98th Percentile) Cell Temperature__open_rack_cell_polymerback (C)':average98CellTemp_open_rack_cell_polymerback,
                                                      'Annual Average (98th Percentile) Module Temperature__open_rack_cell_polymerback (C)':average98Module_open_rack_cell_polymerback,
                                                      'Annual Minimum Module Temperature__open_rack_cell_polymerback (C)':minimum_Module_Temp_open_rack_cell_polymerback,
                                                      'Annual Average Module Temperature__open_rack_cell_polymerback (C)':average_Module_Temp_open_rack_cell_polymerback,
                                                      'Annual Maximum Module Temperature__open_rack_cell_polymerback (C)':maximum_Module_Temp_open_rack_cell_polymerback,
                                                      'Annual Range of Module Temperature__open_rack_cell_polymerback (C)':range_Module_Temp_open_rack_cell_polymerback,                                                         
                                                      'Solder Fatigue Damage__open_rack_cell_polymerback':solderFatigue_open_rack_cell_polymerback,                                                      
                                                        
                                                      'Annual Average (98th Percentile) Cell Temperature__insulated_back_polymerback (C)':average98Cell_insulated_back_polymerback,
                                                      'Annual Average (98th Percentile) Module Temperature__insulated_back_polymerback (C)':average98Module_insulated_back_polymerback,
                                                      'Annual Minimum Module Temperature__insulated_back_polymerback (C)': minimum_Module_Temp_insulated_back_polymerback,
                                                      'Annual Average Module Temperature__insulated_back_polymerback (C)':average_Module_Temp_insulated_back_polymerback,
                                                      'Annual Maximum Module Temperature__insulated_back_polymerback (C)':maximum_Module_Temp_insulated_back_polymerback,
                                                      'Annual Range of Module Temperature__insulated_back_polymerback (C)':range_Module_Temp_insulated_back_polymerback,                                                         
                                                      'Solder Fatigue Damage__insulated_back_polymerback':solderFatigue_insulated_back_polymerback,                                                      
                                                        
                                                      'Annual Average (98th Percentile) Cell Temperature__open_rack_polymer_thinfilm_steel (C)':average98Cell_open_rack_polymer_thinfilm_steel,
                                                      'Annual Average (98th Percentile) Module Temperature__open_rack_polymer_thinfilm_steel (C)':average98Module_open_rack_polymer_thinfilm_steel,
                                                      'Annual Minimum Module Temperature__open_rack_polymer_thinfilm_steel (C)':minimum_Module_Temp_open_rack_polymer_thinfilm_steel,
                                                      'Annual Average Module Temperature__open_rack_polymer_thinfilm_steel (C)':average_Module_Temp_open_rack_polymer_thinfilm_steel,
                                                      'Annual Maximum Module Temperature__open_rack_polymer_thinfilm_steel (C)':maximum_Module_Temp_open_rack_polymer_thinfilm_steel ,
                                                      'Annual Range of Module Temperature__open_rack_polymer_thinfilm_steel (C)':range_Module_Temp_open_rack_polymer_thinfilm_steel,                                                         
                                                      'Solder Fatigue Damage__open_rack_polymer_thinfilm_steel':solderFatigue_open_rack_polymer_thinfilm_steel,                                                      
                                                        
                                                      'Annual Average (98th Percentile) Cell Temperature__22x_concentrator_tracker (C)':average98Cell_22x_concentrator_tracker,
                                                      'Annual Average (98th Percentile) Module Temperature__22x_concentrator_tracker (C)':average98Module_22x_concentrator_tracker, 
                                                      'Annual Minimum Module Temperature__22x_concentrator_tracker (C)':minimum_Module_Temp_22x_concentrator_tracker,
                                                      'Annual Average Module Temperature__22x_concentrator_tracker (C)':average_Module_Temp_22x_concentrator_tracker,
                                                      'Annual Maximum Module Temperature__22x_concentrator_tracker (C)':maximum_Module_Temp_22x_concentrator_tracker,
                                                      'Annual Range of Module Temperature__22x_concentrator_tracker (C)':range_Module_Temp_22x_concentrator_tracker,
                                                      'Solder Fatigue Damage__22x_concentrator_tracker':solderFatigue_22x_concentrator_tracker

                                                      }, 
                                                   ignore_index=True)             

            #Output to the user how many files have been complete
            wb.sheets[mySheet].range(67,4).value = i + 1
        # Save summary of all sites as a pickle    
        finalSummary_df.to_pickle( currentDirectory + '\Pandas_Pickle_DataFrames\Pickle_Level1_Summary\Pickle_Level1_Summary.pickle')


#currentDirectory = r'C:\Users\DHOLSAPP\Desktop\WorldMapProject\WorldMapProject'
#i = 4805
#level1Files = utility.filesNameList( currentDirectory , 'level_1_data' )
