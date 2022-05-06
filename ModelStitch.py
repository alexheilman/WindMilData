import os
import sys
import numpy as np
import pandas as pd
import time
import shutil
from GUI_ModelStitch import *

start_time = 0

def main():
    summer_file, winter_file = FileLocator()
    
    global start_time
    start_time = time.time()

    FileCheck(summer_file, winter_file)

    Status("Importing data.")
    summer_data = pd.read_csv(summer_file, delimiter=",", comment = None, low_memory=False)
    winter_data = pd.read_csv(winter_file, delimiter=",", comment = None, low_memory=False)

    Status("Verifying output data version and substation prefixes.")
    VersionCheck(summer_data, winter_data)

    summer_subs, winter_subs = PrefixQC(summer_data, winter_data)

    Stitch(summer_data, winter_data, summer_subs, winter_subs)

    print("")
    Status("Complete. Use 'OUTPUT DATA_STITCHED.csv'.")

    print('\n')
    input("Press Enter to complete.")


def VersionCheck(summer, winter):
    # extract summer version
    if summer.shape[1] > 20:
        sum_version = summer.iloc[0,22]
    else:
        sum_version = 'WindMil Data 1.1'

    # extract winter version
    if winter.shape[1] > 20:
        win_version = winter.iloc[0,22]
    else:
        win_version = 'WindMil Data 1.1'

    # check version
    if sum_version != "WindMil Data 1.2" or win_version != "WindMil Data 1.2":
        Status("ERROR - One or more OUTPUT_DATA.csv files not valid. Please use WindMil Data version 1.2")
        input("Press Enter to exit.")
        quit()
    else:
        pass


def Stitch(sum_data, win_data, sum_subs, win_subs):
    sum_elements        = sum_data[  sum_data['Source'  ].isin(sum_subs)]
    sum_substations     = sum_data[ (sum_data['Source'  ] == 'ROOT') & \
                                    (sum_data['Names'   ].str[:2] == 'S_')]
    sum_subs_prop       = sum_data[(~sum_data['Source'  ].notnull()) & \
                                    (sum_data['Source.1'] == 'ROOT') & \
                                    (sum_data['Names'   ].str[:2] == 'S_')]
    sum_elements_prop   = sum_data[(~sum_data['Source'  ].notnull()) & \
                                    (sum_data['Source.1'].str[:2] == 'S_')]

    win_elements        = win_data[  win_data['Source'  ].isin(win_subs)]
    win_substations     = win_data[ (win_data['Source'  ] == 'ROOT') & \
                                    (win_data['Names'   ].str[:2] == 'W_')]
    win_subs_prop       = win_data[(~win_data['Source'  ].notnull()) & \
                                    (win_data['Source.1'] == 'ROOT') & \
                                    (win_data['Names'   ].str[:2] == 'W_')]
    win_elements_prop   = win_data[(~win_data['Source'  ].notnull()) & \
                                    (win_data['Source.1'].str[:2] == 'W_')]

    dis_elements        = sum_data[ (sum_data['Source'  ] == 'ROOT') & \
                                    (sum_data['Names'   ].str[:2] != 'S_') & \
                                    (sum_data['Names'   ].str[:2] != 'W_')]

    print("\n\t\t\tTotal elements:\t\t", len(sum_data))
    print("\t\t\tDisconnected:\t\t", len(dis_elements)) 

    print("\n\t\t\tExisting elements")
    print("\t\t\t", "summer substations:",  len(sum_substations))
    print("\t\t\t", "summer elements:\t",   len(sum_elements))
    print("\t\t\t", "winter substations:",  len(win_substations))
    print("\t\t\t", "winter elements:\t",   len(win_elements))
    
    print("\n\t\t\tProposed elements")
    print("\t\t\t", "summer substations:",  len(sum_subs_prop))
    print("\t\t\t", "summer elements:\t",   len(sum_elements_prop))    
    print("\t\t\t", "winter substations:",  len(win_subs_prop))
    print("\t\t\t", "winter elements:\t",   len(win_elements_prop))  

    df = pd.concat([sum_substations, sum_elements, win_substations, win_elements, \
                    sum_subs_prop, sum_elements_prop, win_subs_prop, win_elements_prop, dis_elements])

    headers = ['Names','Existing','Source','Voltage','Acc Drop','Miles','I AØ','I BØ','I CØ','Min(Flt)','Max(Flt)',\
                       'Proposed','Source','Voltage','Acc Drop','Miles','I AØ','I BØ','I CØ','Min(Flt)','Max(Flt)', '','Version']

    df.iloc[0, df.columns.get_loc('Version')] = "WindMil Data 1.2"

    df.to_csv('OUTPUT DATA_STITCHED.csv', index = False, header=headers, encoding='utf-8-sig') 


def PrefixQC(summer_data, winter_data):
    data   = pd.concat([summer_data, winter_data])
    subs_e = list(data['Source'  ].unique())    # existing substation sources
    subs_p = list(data['Source.1'].unique())  # proposed substation sources
    subs   = list(set(subs_e + subs_p))       # unique list

    error_subs  = []
    winter_subs = []
    summer_subs = []

    # categorize substation list into summer, winter, error
    for sub in subs:
        sub = str(sub)
        if   sub[:2] == 'S_': 
            summer_subs.append(sub)
        elif sub[:2] == 'W_':
            winter_subs.append(sub)
        elif sub == 'nan' or sub == 'ROOT':
            pass
        else:
            error_subs.append(sub)

    # warn user of invalid element names and terminate program
    if len(error_subs) > 0:
        Status("ERROR - One or more substation element names are invalid." + \
               "\n\t\t\t\tInvalid substation element names:")
        for i in error_subs:
            print("\t\t\t\t\t" + i)
        input("Press Enter to exit.")
        quit()
    else:
        pass 

    return summer_subs, winter_subs

def FileCheck(summer_file, winter_file):
    if summer_file == None or winter_file == None:
        Status("ERROR - One or more files not selected.")
        input("Press Enter to exit.")
        quit()
    else:
        pass


def Status(text):
    global start_time
    current_time = "{:.2f}".format(round(time.time() - start_time, 2))
    sys.stdout.write(str(current_time))
    sys.stdout.write('\t')
    sys.stdout.write('s:  ')
    sys.stdout.write(text)
    sys.stdout.write('\n')


main()
