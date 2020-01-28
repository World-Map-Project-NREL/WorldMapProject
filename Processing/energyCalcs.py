"""
Contains energy algorithms for processing.

@author: Derek Holsapple
"""

import numpy as np
from numba import jit             
import math
#import pandas as pd


class energyCalcs:

    

    def power( cellTemp , globalPOA ):
        '''
        HELPER FUNCTION
        
        Find the power produced from a solar module.
    
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
        @param refTemp             -float, reference temperature (C)
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
    
    
    
    def vantHoffDeg( x , Ichamber , globalPOA , moduleTemp , Tf , refTemp):    
        '''
        Vant Hoff Irradiance Degradation 
        
        Find the rate of degradation kenetics of a simulated chamber. 
        
        (ADD IEEE reference)
    
        @param globalPOA             -series, Global Plane of Array Irradiance W/m^2
        @param x                     -series, Solar Module Temperature (C)
    
        @return  sumOfDegEnv         -float, Summation of Degradation Environment 
        @return  avgOfDegEnv         -float, Average rate of Degradation Environment
        @return  rateOfDegChamber    -float, Rate of Degradation from Simulated Chamber
        @return  accelerationFactor  -float, Degradation acceleration factor
        '''  
        rateOfDegEnv = energyCalcs.rateOfDegEnv(globalPOA,
                                                        x , 
                                                        moduleTemp ,
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
        return( math.exp(( 3.257532E-13 * dewPtTemp**6 ) - 
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
  
    

    
    
    
    
    