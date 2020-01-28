"""
Class contains utility functions functions pertaining to raw data imports 

@author: Derek Holsapple
"""

import pandas as pd
import glob
import os 

class cleanRawOutput:   

    def dataSummaryFrame( path ):
        '''
        HELPER FUNCTION
        
        dataSummaryFrame()
        
        This will be a dataframe for a user reference table
        Clean the dataframe and change variables for readability
        
        @param path           -String, path to current working directory
        
        @retrun formatted_df  -Dataframe, summarized dataframe for user 
                                            reference table
        '''
        #import the pickle dataframe for the summary report
        formatted_df = pd.read_pickle( path + \
          '\\Pandas_Pickle_DataFrames\\Pickle_FirstRows\\' + \
          'firstRowSummary_Of_CSV_Files.pickle')
        return formatted_df
    
        

    def filesNameList( path ):
        '''
        HELPER FUNCTION
        
        filesNameList()
        
        get a list of file names from the pickle raw data
        
        @param path       -String, path to the folder with the pickle files
        
        @retrun allFiles  -String List, filenames without the file path
        
        '''        
        #list of strings of all the files
        allFiles = glob.glob(path + "/Pandas_Pickle_DataFrames/Pickle_RawData/*")
        #for loop to go through the lists of strings and to remove irrelavant data
        for i in range( 0, len( allFiles ) ):
            # Delete the path and pull out only the file name 
            temp = os.path.basename(allFiles[i])
            allFiles[i] = temp
        return allFiles
    
    

    def stringList_UniqueID_List( listOfStrings ):
        '''
        stringList_UniqueID_List()
        
        This method takes a lists of strings and searches for a unique sample 
        identifier. It then takes that unique identifier and creates a list. 
        If one of the strings does not have a unique identifier it will put 
        that original string back into the list
        
        Example List
        
        '690190TYA.pickle',
        'GRC_SOUDA(AP)_167460_IW2.pickle',
        'GRC_SOUDA-BAY-CRETE_167464_IW2.pickle',
        'Test']
        
        Return List
        
        '690190'
        '167460'
        '167464'
        'Test'
         
        @param listOfStrings   - List of Strings , list of strings containing 
                                                        unique identifier
        @return sampleList     - List of Strings, list of filtered strings with
                                                        unique identifiers
        '''
        sampleList = []
        for i in range(0, len(listOfStrings)):
            
            sampleList.append(cleanRawOutput.string_UniqueID( listOfStrings[ i ] ) )
              
        return sampleList         



    def string_UniqueID( fileName ):
        '''
        stringList_UniqueID_List()
        
        This method takes a strings and searches for a unique sample 
        identifier. It then takes that unique identifier and creates a list. 
        If one of the strings does not have a unique identifier it will put 
        that original string back into the list
        
        Example String
        
        '690190TYA.pickle',
        'GRC_SOUDA(AP)_167460_IW2.pickle',
        'GRC_SOUDA-BAY-CRETE_167464_IW2.pickle',
        'tmy_1.962_29.621_2005_2014.epw'
        'Test']
        
        Return String
        
        '690190'
        '167460'
        '167464'
        '962_29'
        'Test'
         
        @param fileName     - String, string containing unique identifier
        @return uniqueID    - String, filtered strings with unique identifiers
        '''
        ascii_list =[ord(c) for c in fileName]
        #Create a char list 
        char_list = list(fileName)
        count = 0 
        # j will be the index referencing the next ASCII character
        for j in range(0, len(ascii_list)):
            #Filter to find a unique combination of characters and ints 
            ###############
            # ASCII characters for numbers 0 - 10, or a Underscore '_'
            if (ascii_list[j] >= 48 and ascii_list[j] <= 57) or (ascii_list[j] == 95 and count >=1): 
                #If a number is encountered increase the counter
                count = count + 1
                # If the count is 6 "This is how many numbers in a row 
                    #the unique identifier will be"
                if count == 3:
                    # Create a string of the unique identifier
                    uniqueID = ( char_list[ j - 2 ] +
                                 char_list[ j - 1 ] + 
                                 char_list[ j ]     + 
                                 char_list[ j + 1 ] + 
                                 char_list[ j + 2 ] + 
                                 char_list[ j + 3 ] )
                    #If there is a '-' from satellite data Lat/Lon raw string
                    if "-" in uniqueID:
                        uniqueID = uniqueID.replace('-', char_list[ j + 4 ])
                    if "." in uniqueID:
                        uniqueID = uniqueID.replace('.', '0')
                    # Stop the search.  The identifier has been located
                    break
            # If the next ASCII character is not a number reset the counter       
            else:
                count = 0
        # If a unique identifier is not located insert string as placeholder
        # so that indexing is not corrupted
        if count == 0 and j == len(ascii_list) - 1 :        
           uniqueID = fileName  
        return uniqueID 

