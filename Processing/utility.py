# -*- coding: utf-8 -*-
"""
Utility class to store Helper Functions

@author: Derek Holsapple
"""

import os
import glob
import shutil


class utility:
    
    
    
    def range_inc(start, stop, step):
        '''
        HELPER FUNCTION
        
        range_inc()
        
        Get values between a start and stop point with specified increments.
        
        @param start          - float/int, start value to increment
        @param stop           - float/int, stop value to end incrementing
        @param step           - float/int, value to increment by
                                           
        @return i             - float, every value incremented             
        ''' 
        i = start
        # +.1 because float values are not exact
        while i <= stop + .1:
            yield i
            i += step    
            
            
    
    def deleteAllFiles( path ):
        '''
        HELPER FUNCTION
        
        deleteAllFiles()
        
        Delete all files from a directory
        
        @param path           - String, directory to delete all files
                                           
        @return void          - Deletes all files in the chosen directory             
        '''        
        for root, dirs, files in os.walk( path ):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))    
    

    
    
    def dirEmpty( path ):
        '''
        HELPER FUNCTION
        
        dirEmpty()
        
        Aggregate raw data (TMY3, CWEC, IWEC) into individual pickle files
        
        @param path            - String, directory to check if any files exist
                                           
        @return boolean        - True, if a no files exists in the directory
                               - False, if there is no file in the directory               
        '''
        if len(os.listdir( path ) ) == 0:
            return True
        else:    
            return False    
        
        
        
    def filesNameList( path , selector):
        '''
        HELPER FUNCTION
        
        filesNameList()
        
        Pull out the file paths and return a list of file names
        
        @param path       -String, path to the folder with the pickle files
        
        @return allFiles  -String List, filenames without the file path
        
        '''  
        
        if selector == 'rawData':
            dataPath = "/Pandas_Pickle_DataFrames/Pickle_RawData/*"
        elif selector == 'level_1_data':
            dataPath = "/Pandas_Pickle_DataFrames/Pickle_Level1/*"
        elif selector == 'optimizedTilt':
            dataPath = "/Pandas_Pickle_DataFrames/Pickle_Optimization/Pickle_Optimal_Tilt/*"
        
        #list of strings of all the files
        allFiles = glob.glob(path + dataPath)
        #for loop to go through the lists of strings and to remove irrelavant data
        for i in range( 0, len( allFiles ) ):
            # Delete the path and pull out only the file name 
            temp = os.path.basename(allFiles[i])
            allFiles[i] = temp
            
        return allFiles        
        
        
        
    def dataSource( filePath ):
        '''
        HELPER FUNCTION
        
        dataSource()
        
        From the raw file paths determine where the source of the data came from. 
        The current function finds data from IWEC (Global), CWEC (Canada) 
        and TMY3 (United States).  These are identified as 
        
        TYA = TMY3
        CWEC = CWEC
        IWEC = IW2    
        
        @param filePath          -string, file name of the raw data
        
        @return                  -string, return the type of data file
                                            (IWEC, CWEC, TMY3, or UNKNOWN)
        '''    
        #Create a list of ASCII characters from the string
        ascii_list =[ord(c) for c in filePath]
        char_list = list(filePath)
        #If the first string  does not pass the filter set the sample flag to 0
        #sampleFlag = 0 
        count = 0 
        # j will be the index referencing the next ASCII character
        for j in range(0, len(ascii_list)):
            #Locate first letter "capitalized" T, C, or I
            if ascii_list[j] == 84 or ascii_list[j] == 67 or \
                                      ascii_list[j] == 73: 
                if count == 0:
                    #If a letter is encountered increase the counter
                    count = count + 1
             # If one of the second letters is encountered Y, W 
            elif ascii_list[j] == 89 or ascii_list[j] == 87:
                if count == 1:
                    count = count + 1
                else:
                    count = 0
            # Detect A, E, or 2
            elif ascii_list[j] == 65 or ascii_list[j] == 69 or \
                                        ascii_list[j] == 50:
                if count == 2:
                    # Create a string of the unique identifier
                    rawDataSource =  char_list[ j - 2 ] + char_list[ j - 1 ]\
                                     + char_list[ j ]              
                    if rawDataSource == "TYA":
                        dataSource = "TMY3"
                        return dataSource
                    elif rawDataSource == "CWE": 
                        dataSource = "CWEC"
                        return dataSource
                    elif rawDataSource == "IW2":
                        dataSource = "IWEC"
                        return dataSource
                    else:
                        count = 0
                else:
                    count = 0
            # If the next ASCII character is not a number reset the counter to 0        
            else:
                count = 0 
            # If a unique identifier is not located insert string as placeholder
            #   so that indexing is not corrupted
            if j == len(ascii_list) - 1 :   
                dataSource = "UNKNOWN"              
        return dataSource           