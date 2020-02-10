# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 10:05:30 2019

This code was developed to calculate the solar time of a given location.

There are three needed location parameters
    1) Longitude 
    2) Local time 
    3) Current Date

The method will take the longitude, Local time and 
Current date as a pandas datetime object

*References
From https://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-time

@author: Derek Holsapple
"""
import pandas as pd
import numpy as np
from numba import jit       


class solarTime:
   
    
    
    def toDaysOfYear( datetime_object ):
        '''
        HELPER FUNCTION
        
        toDaysOfYear()
        
        take a datetime object and convert it into the number of days in a year 
        
        @param datetime_object   -datetime, of Date and Time
        
        @return dayOftheYear      -int, return the day number in the year
        
        '''        
        return datetime_object.timetuple().tm_yday
    
    

    # Numba Machine Language Level ( Fast Processing )
    @jit(nopython=True , error_model = 'python') 
    def angle_B( dayNumberInAYear ):
        '''
        HELPER FUNCTION
        
        angle_B()
         
        ##########################
        Angle for Equation of Time
        
        The equation of time (EoT) (in minutes) is an empirical equation that 
        corrects for the eccentricity of the Earth's orbit and the Earth's axial 
        tilt. An approximation 2 accurate to within ½ minute is:
        
        B is in degrees and d is the number of days since the start of the year. 
        The time correction EoT is plotted in the figure below.
        
        B=360/365(d−81)
        
        EoT=9.87sin(2B)−7.53cos(B)−1.5sin(B)
        ##########################
        
        @param dayNumberInAYear   -int, of Date and Time
        
        @return datetime_object  -float, angle
        
        '''        
        #Make sure to return in radians for later sin/cos calcualtions with numpy
        B = np.deg2rad((360/365) * ( dayNumberInAYear - 81 ))
        
        return B
    
    
    # Numba Machine Language Level ( Fast Processing )
    @jit(nopython=True , error_model = 'python') 
    def eoT( angle_B ):
        '''
        HELPER FUNCTION
        
        eoT()
         
        ##########################
        Angle for Equation of Time
        
        The equation of time (EoT) (in minutes) is an empirical equation that 
        corrects for the eccentricity of the Earth's orbit and the Earth's 
        axial tilt. An approximation 2 accurate to within ½ minute is:
        
        B is in degrees and d is the number of days since the start of the year. 
        
        B=360/365(d−81)
        
        EoT=9.87sin(2B)−7.53cos(B)−1.5sin(B)
        ##########################
        
        
        @param angle_B   -float, degrees from local time days
        
        @return eoT  -float, Equation of Time
        
        '''        
        return 9.87*np.sin(2*angle_B) - 7.53*np.cos(angle_B) - 1.5*np.sin(angle_B)
    
    

    @jit(nopython=True , error_model = 'python') # Numba Machine Language Level ( Fast Processing )
    def timeCorrection(eoT , lon , lSTM ):
        '''
        HELPER FUNCTION
        
        timeCorrection()
         
        ##########################
        Time Correction Factor (TC)
        
        The net Time Correction Factor (in minutes) accounts for the variation of 
        the Local Solar Time (LST) within a given time zone due to the longitude 
        variations within the time zone and also incorporates the EoT above.
        
        The factor of 4 minutes comes from the fact that the Earth rotates 1° every 4 minutes.
        
        TC = 4(Longitude - LSTM) + EOT
        ##########################
        
        
        @param eoT              -float, Equation of Time, other helper method
        @param lon              -float, longitude of the current site
        @param lSTM             -float, Local Standard Time Meridian
        
        @return timeCorrection  -float, the amount of time to correct for solar time
        
        '''        
        return 4*( lon - lSTM ) + eoT
    
    

    def localSolarTime( localTime , timeCorrection ):
        '''
        HELPER FUNCTION
        
        my_to_datetime()
        
        take a datetime object and convert it corrected solar time.
        Solar time is 12:00pm when the sun is highest in the sky 
        
        @param datetime_object   -datetime object, of Date and Time (local time)
        @param timeCorrection    -float, time correction in minutes
        
        @return datetime_object  -datetime object, Corrected solar time
        
        '''                   
        LocalSolarTime = localTime + pd.Timedelta( minutes = timeCorrection)
        #LocalSolarTime = localTime + pd.Timedelta( minutes = timeCorrection/60)
        return LocalSolarTime
    


    def localTimeToSolarTime( longitude , timeZoneDif , localTime ):
        '''
        EXECUTION FUNCTION
        
        localTimeToSolarTime()
        
        take a datetime object and convert it corrected solar time.
        Solar time is 12:00pm when the sun is highest in the sky 
        
        @param longitude         -float, longitude of the current site
        @param timeZoneDif         -int, Number of decimal hours by which local standard 
                                        time is ahead or behind Universal Time 
                                        ( + if ahead, - if behind)
        @param localTime         -datetime object, of Date and Time (local time), includes the day of the year
                                                 EXAMPLE timestamp: 1998-01-01 01:00:00
        
        
        
        @return datetime_object  -datetime object, Location Solar Time
                                                 EXAMPLE timestamp: 1998-01-01 00:16:13.609301
        '''    
        lSTM = 15 * timeZoneDif
   
        daysInTheYear = solarTime.toDaysOfYear(localTime)
      
        angleB = solarTime.angle_B(daysInTheYear)
    
        equationOfTime = solarTime.eoT(angleB)
        
        timeCor = solarTime.timeCorrection(equationOfTime , longitude , lSTM )
    
        solarTimeOut = solarTime.localSolarTime( localTime, timeCor )
        
        return solarTimeOut
    





















