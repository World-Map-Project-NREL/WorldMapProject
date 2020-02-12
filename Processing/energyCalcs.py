"""
Contains energy algorithms for processing.

@author: Derek Holsapple
"""

import numpy as np
from numba import jit 
import pandas as pd   
from scipy.constants import convert_temperature         
#import math
#import pandas as pd


class energyCalcs:

    
    def avgDailyTempChange( localTime , cell_Temp ):
        '''
        HELPER FUNCTION
        
        Get the average of a year for the daily maximum temperature change.
        
        For every 24hrs this function will find the delta between the maximum
        temperature and minimun temperature.  It will then take the deltas for 
        every day of the year and return the average delta. 
    
        
        @param localTime           -timestamp series, Local time of specific site by the hour
                                                year-month-day hr:min:sec
                                                (Example) 2002-01-01 01:00:00
        @param cell_Temp           -float series, Photovoltaic module cell 
                                               temperature(Celsius) for every hour of a year
                                               
        @return avgDailyTempChange -float , Average Daily Temerature Change for 1-year (Celsius)
        @return avgMaxCellTemp     -float , Average of Daily Maximum Temperature for 1-year (Celsius)
        '''    
        #Setup frame for vector processing
        timeAndTemp_df = pd.DataFrame( columns = ['Cell Temperature'])
        timeAndTemp_df['Cell Temperature'] = cell_Temp
        timeAndTemp_df.index = localTime
        timeAndTemp_df['month'] = timeAndTemp_df.index.month
        timeAndTemp_df['day'] = timeAndTemp_df.index.day
        
        #Group by month and day to determine the max and min cell Temperature (C) for each day
        dailyMaxCellTemp_series = timeAndTemp_df.groupby(['month','day'])['Cell Temperature'].max()
        dailyMinCellTemp_series = timeAndTemp_df.groupby(['month','day'])['Cell Temperature'].min()
        cellTempChange = pd.DataFrame({ 'Max': dailyMaxCellTemp_series, 'Min': dailyMinCellTemp_series})
        cellTempChange['TempChange'] = cellTempChange['Max'] - cellTempChange['Min']
        
        #Find the average temperature change for every day of one year (C) 
        avgDailyTempChange = cellTempChange['TempChange'].mean()
        #Find daily maximum cell temperature average
        avgMaxCellTemp  = dailyMaxCellTemp_series.mean()
            
        return avgDailyTempChange , avgMaxCellTemp 



    def timesOverReversalNumber( cell_Temp , reversalTemp):
        '''
        HELPER FUNCTION
        
        Get the number of times a temperature increases or decreases over a 
        specific temperature gradient.


        @param cell_Temp           -float series, Photovoltaic module cell 
                                               temperature(Celsius) 
        @param reversalTemp        -float, temperature threshold to cross above and below

        @param numChangesTempHist  -int , Number of times the temperature threshold is crossed                          
        '''
        #Find the number of times the temperature crosses over 54.8(C)
        
        
        temp_df = pd.DataFrame()
        temp_df['CellTemp'] = cell_Temp
        temp_df['COMPARE'] = cell_Temp
        temp_df['COMPARE'] = temp_df.COMPARE.shift(-1)
        
        #reversalTemp = 54.8
        
        temp_df['cross'] = (
            ((temp_df.CellTemp >= reversalTemp) & (temp_df.COMPARE < reversalTemp)) |
            ((temp_df.COMPARE > reversalTemp) & (temp_df.CellTemp <= reversalTemp)) |
            (temp_df.CellTemp == reversalTemp))
        
        numChangesTempHist = temp_df.cross.sum()
        
        return numChangesTempHist
        
        
    def solderFatigue( localTime , cell_Temp , reversalTemp):
        '''
        HELPER FUNCTION
        
        Get the Thermomechanical Fatigue of flat plate photovoltaic module solder joints.
        Damage will be returned as the rate of solder fatigue for one year
    
        Bosco, N., Silverman, T. and Kurtz, S. (2020). Climate specific thermomechanical 
        fatigue of flat plate photovoltaic module solder joints. [online] Available 
        at: https://www.sciencedirect.com/science/article/pii/S0026271416300609 
        [Accessed 12 Feb. 2020].
        
        @param localTime           -timestamp series, Local time of specific site by the hour
                                                year-month-day hr:min:sec
                                                (Example) 2002-01-01 01:00:00
        @param cell_Temp           -float series, Photovoltaic module cell 
                                               temperature(Celsius) for every hour of a year
        @param reversalTemp        -float, temperature threshold to cross above and below
        
        @return damage           - float series, Acceleration factor of solder 
                                                 fatigue for one year            
        ''' 
        
       # cell_Temp = convert_temperature( cell_Temp , 'Celsius', 'Kelvin')
       # reversalTemp = convert_temperature( reversalTemp , 'Celsius', 'Kelvin')
        
        
        # Get the 1) Average of the Daily Maximum Cell Temperature (C)
        #         2) Average of the Daily Maximum Temperature change avg(daily max - daily min)
        #         3) Number of times the temperaqture crosses above or below the reversal Temperature
        MeanDailyMaxCellTempChange , dailyMaxCellTemp_Average = energyCalcs.avgDailyTempChange( localTime , cell_Temp )
        dailyMaxCellTemp_Average = convert_temperature( dailyMaxCellTemp_Average , 'Celsius', 'Kelvin')
        numChangesTempHist = energyCalcs.timesOverReversalNumber( cell_Temp, reversalTemp )
              
        #k = Boltzmann's Constant
        damage = 405.6 * (MeanDailyMaxCellTempChange **1.9) * \
                         (numChangesTempHist**.33) * \
                         np.exp(-(.12/(.00008617333262145*dailyMaxCellTemp_Average)))
    
        return damage
    
    def power( cellTemp , globalPOA ):
        '''
        HELPER FUNCTION
        
        Find the relative power produced from a solar module.
    
        Model derived from Mike Kempe Calculation on paper
        (ADD IEEE reference)
        
        @param cellTemp           -float, Cell Temperature of a solar module (C)

        @return power produced from a module (NEED TO ADD METRIC)  
        '''           

        return ( globalPOA * ( 1 + ( 25 - cellTemp ) * .004 )  )
        
        
        
        
    def rateOfDegEnv( poa, x, cellTemp, refTemp, Tf):
        '''
        HELPER FUNCTION
        
        Find the rate of degradation kenetics using the Fischer model.  
        Degradation kentics model interpolated 50 coatings with respect to 
        color shift, cracking, gloss loss, fluorescense loss, 
        retroreflectance loss, adhesive transfer, and shrinkage.
        
        (ADD IEEE reference)
        
        @param poa                 -float, (Global) Plan of Array irradiance (W/m^2)
        @param x                   -float, fit parameter
        @param cellTemp            -float, solar module cell temperature (C)
        @param refTemp             -float, reference temperature (C) "Chamber Temperature"
        @param Tf                  -float, multiplier for the increase in degradation
                                          for every 10(C) temperature increase
        @return  degradation rate (NEED TO ADD METRIC)  
        '''        
        return poa**(x) * Tf ** ( (cellTemp - refTemp)/10 )



    def rateOfDegChamber( Ichamber , x ):
        '''
        HELPER FUNCTION
        
        Find the rate of degradation kenetics of a simulated chamber. Mike Kempe's 
        calculation of the rate of degradation inside a accelerated degradation chamber. 
        
        (ADD IEEE reference)

        @param Ichamber      -float, Irradiance of Controlled Condition W/m^2
        @param x             -float, fit parameter

        @return  degradation rate of chamber 
        '''        
        return Ichamber ** ( x )



    def timeOfDeg( rateOfDegChamber , rateOfDegEnv ):
        '''
        HELPER FUNCTION
        
        Find the acceleration factor for degradation kenetics of a simulated chamber compared 
        to environmental data for 1-year
        
        (ADD IEEE reference)

        @param rateOfDegChamber      -float, degradation rate of environment
        @param rateOfDegEnv         -float, degredation rate of chamber

        @return  degradation rate of chamber (NEED TO ADD METRIC)  
        '''        
        return ( rateOfDegChamber / rateOfDegEnv )
    
    
    
    def vantHoffDeg( x , Ichamber , globalPOA , cellTemp , Tf , refTemp):    
        '''
        Vant Hoff Irradiance Degradation 
        

        @param x                     -float, fit parameter
        @param Ichamber              -float, Irradiance of Controlled Condition W/m^2
        @param globalPOA             -float or series, Global Plane of Array Irradiance W/m^2
        @param cellTemp              -float or series, solar module cell temperature (C)
        @param Tf                    -float, multiplier for the increase in degradation
                                          for every 10(C) temperature increase
        @param refTemp               -float, reference temperature (C) "Chamber Temperature"                                          
                                          
        @return  sumOfDegEnv         -float or series, Summation of Degradation Environment 
        @return  avgOfDegEnv         -float or series, Average rate of Degradation Environment
        @return  rateOfDegChamber    -float or series, Rate of Degradation from Simulated Chamber
        @return  accelerationFactor  -float or series, Degradation acceleration factor
        '''  
        rateOfDegEnv = energyCalcs.rateOfDegEnv(globalPOA,
                                                        x , 
                                                        cellTemp ,
                                                        refTemp ,
                                                        Tf )        
        sumOfDegEnv = rateOfDegEnv.sum(axis = 0, skipna = True)
        avgOfDegEnv = rateOfDegEnv.mean()
            
        rateOfDegChamber = energyCalcs.rateOfDegChamber( Ichamber , x )
        
        accelerationFactor = energyCalcs.timeOfDeg( rateOfDegChamber , avgOfDegEnv)
        
        return  sumOfDegEnv, avgOfDegEnv, rateOfDegChamber, accelerationFactor
        



    # Numba Machine Language Level
    @jit(nopython=True , error_model = 'python')  
    def dewYield( h , tD , tA , windSpeed , n ):
        '''
        HELPER FUNCTION
        
        Find the dew yield in (mm·d−1).  Calculation taken from journal
        "Estimating dew yield worldwide from a few meteo data"
            -D. Beysens

        (ADD IEEE reference)
        
        @param h          -int, site elevation in kilometers
        @param tD         -float, Dewpoint temperature in Celsius
        @param tA         -float, air temperature "dry bulb temperature"
        @param windSpeed  -float, air or windspeed measure in m*s^-1  or m/s
        @param n          -float, Total sky cover(okta)
        @return  dewYield -float, amount of dew yield in (mm·d−1)  
        '''
        windSpeedCutOff = 4.4 
        dewYield = ( 1/12 ) * (.37 * ( 1 + ( 0.204323 * h ) - (0.0238893 * \
                    h**2 ) - ( 18.0132 - ( 1.04963 * h**2 ) + ( 0.21891 * \
                    h**2 ) ) * (10**( -3 ) * tD ) ) * ( ( ( ( tD + 273.15)/ \
                    285)**4)*(1 - (n/8))) + (0.06 * (tD - tA ) ) * ( 1 + 100 * \
                    ( 1 - np.exp( - ( windSpeed / windSpeedCutOff)**20 ) ) ) ) 

        return dewYield
    
    

    def waterVaporPressure( dewPtTemp ):
        '''
        HELPER FUNCTION
        
        waterVaporPressure()
        
        Find the average water vapor pressure (kPa) based on the Dew Point 
        Temperature model created from Mike Kempe on 10/07/19 from Miami,FL excel sheet.  
        
        @param dewPtTemp          -float, Dew Point Temperature
        @return                   -float, return water vapor pressur in kPa
        '''    
        return( np.exp(( 3.257532E-13 * dewPtTemp**6 ) - 
                ( 1.568073E-10 * dewPtTemp**6 ) + 
                ( 2.221304E-08 * dewPtTemp**4 ) + 
                ( 2.372077E-7 * dewPtTemp**3) - 
                ( 4.031696E-04 * dewPtTemp**2) + 
                ( 7.983632E-02 * dewPtTemp ) - 
                ( 5.698355E-1)))
    
   
    
    def rH_Above85( rH ):    
        '''
        HELPER FUNCTION
        
        rH_Above85()
        
        Determine if the relative humidity is above 85%.  
        
        @param rH          -float, Relative Humidity %
        @return                   -Boolean, True if the relative humidity is 
                                            above 85% or False if the relative 
                                            humidity is below 85%
        '''         
        if rH > 85:
            return( True )
        else:
            return ( False )
     
        
   
    def hoursRH_Above85( df ):      
        '''
        HELPER FUNCTION
        
        hoursRH_Above85()
        
        Count the number of hours relative humidity is above 85%.  
        
        @param    df     -dataFrame, dataframe containing Relative Humidity %
        @return          -int, number of hours relative humidity is above 85%
        
        '''         
        booleanDf = df.apply(lambda x: energyCalcs.rH_Above85( x ) )
        return( booleanDf.sum() )
        
  

    def whToGJ( wh ):
        '''
        HELPER FUNCTION
        
        whToGJ()
        
        Convert Wh/m^2 to GJ/m^-2 
        
        @param wh          -float, Wh/m^2
        @return                   -float, GJ/m^-2
        
        '''    
        return( 0.0000036 * wh )
    
    

    def gJtoMJ( gJ ):
        '''
        HELPER FUNCTION
        
        gJtoMJ()
        
        Convert GJ/m^-2 to MJ/y^-1
        
        @param gJ          -float, Wh/m^2
        @return            -float, GJ/m^-2
        
        '''    
        return( gJ * 1000 )
  
    

    
    
    
    
    