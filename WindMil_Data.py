import os
import os.path
from os import path
import sys
import numpy as np
import pandas as pd
import shutil
import time
from GUI_WindMil import *

# initialize global data
start_time = 0
a_dict = {} # a-phase dictionary
b_dict = {} # b-phase dictionary
c_dict = {} # c-phase dictionary

def main():

    e_rsl_file, e_std_file, p_rsl_file, p_std_file = FileLocator()

    global start_time
    start_time = time.time()

    if e_rsl_file == None or e_std_file == None or p_rsl_file == None or p_std_file == None:
        Status("ERROR - One or more files not selected.")
        input("PROGRAM TERMINATED")
        quit()

    else:

        Status("Importing data.")
        e_data = ImportRSL(e_rsl_file)
        p_data = ImportRSL(p_rsl_file)

        Status("Matching in STD file data.")
        e_data = ImportSTD(e_data, e_std_file)
        p_data = ImportSTD(p_data, p_std_file)

        Status("Calculating maximum available fault.")
        e_data['maxfault'] = e_data[['maxlg','maxll','maxllg','maxlllg']].max(axis=1)
        p_data['maxfault'] = p_data[['maxlg','maxll','maxllg','maxlllg']].max(axis=1)
        e_data = e_data.drop(columns=['maxlg','maxll','maxllg','maxlllg'])
        p_data = p_data.drop(columns=['maxlg','maxll','maxllg','maxlllg'])

        Status("Calculating minimum voltage.")
        e_data = MinVoltage(e_data)
        p_data = MinVoltage(p_data)
        e_data = e_data.drop(columns=['volta','voltb','voltc'])
        p_data = p_data.drop(columns=['volta','voltb','voltc'])

        Status("Exporting summary files.")
        SummaryFiles(e_data, p_data)
        e_data = e_data.drop(columns=['kW','PF','feeder'])
        p_data = p_data.drop(columns=['kW','PF','feeder'])

        Status("Bypassing regulators.")
        e_data = RegulatorBypass(e_data)
        p_data = RegulatorBypass(p_data)

        Status("Calculating existing accumulated voltage drop.")
        e_data = DropAccumulator(e_data)

        Status("Calculating proposed accumulated voltage drop.")
        p_data = DropAccumulator(p_data)

        Status("Translating regulator voltages to source-side voltage.")
        e_data = RegulatorVoltageCorrection(e_data)
        p_data = RegulatorVoltageCorrection(p_data)
        e_data = e_data.drop(columns=['parent','phasing','sdropa','sdropb','sdropc','device','parenta','parentb','parentc'])
        p_data = p_data.drop(columns=['parent','phasing','sdropa','sdropb','sdropc','device','parenta','parentb','parentc'])

        Status("Exporting output data.")
        OutputData(e_data, p_data)

        Declutter()

        Status("Complete.")

        print('\n')
        input("Press Enter to complete.")

def Declutter():
    dir_path = os.getcwd()
    new_path = os.path.join(dir_path, "EXPORT")

    # create "EXPORT" directory if it doesn't already exist
    if 'EXPORT' not in os.listdir(dir_path):
        os.mkdir(new_path)

    # relocate files with specified extensions to /EXPORT
    extensions = ['.std', '.rsl', '.mpt', '.wmprefs', '.swg']
    for i in extensions:
        files = os.listdir(dir_path)
        for file in files:
            if file.endswith(i):
                shutil.move(os.path.join(dir_path, file), os.path.join(new_path, file))

def SummaryFiles(e_df, p_df):
    # reduce to sources and feeders 
    e_sources_feeders = e_df["feeder"]
    e_sources_feeders = e_sources_feeders.drop_duplicates()
    e_df2 = e_df[e_df['name'].isin(e_sources_feeders)]

    p_sources_feeders = p_df["feeder"]
    p_sources_feeders = p_sources_feeders.drop_duplicates()
    p_df2 = p_df[p_df['name'].isin(p_sources_feeders)]

    # reduce to needed columns
    e_df2 = e_df2[['name','sub','ampsa','ampsb','ampsc','kW','PF','maxfault']]
    p_df2 = p_df2[['name','sub','ampsa','ampsb','ampsc','kW','PF','maxfault']]

    # round phase currents
    e_df2.ampsa = e_df2.ampsa.round()
    e_df2.ampsb = e_df2.ampsb.round()
    e_df2.ampsc = e_df2.ampsc.round()
    p_df2.ampsa = p_df2.ampsa.round()
    p_df2.ampsb = p_df2.ampsb.round()
    p_df2.ampsc = p_df2.ampsc.round()

    # merge
    df2 = e_df2.merge(p_df2, how='outer', on='name', suffixes=('_e','_p'))
    df2.insert(1, "existing", "  |") 
    df2.insert(9, "proposed", "  |") 

    df2_subs = df2[(df2['sub_e'] == 'ROOT')|(df2['sub_p'] == 'ROOT')]
    df2_fdrs = df2[(df2['sub_e'] != 'ROOT')&(df2['sub_p'] != 'ROOT')]

    # create "DATA" directory if it doesn't already exist
    new_dir = 'DATA'
    dir_path = os.getcwd()
    if new_dir not in os.listdir(dir_path):
        new_path = os.path.join(dir_path, new_dir)
        os.mkdir(new_path)

    df2_subs.to_csv(new_dir + '/SUMMARY - SUBSTATIONS.csv', index = False)
    df2_fdrs.to_csv(new_dir + '/SUMMARY - FEEDERS.csv', index = False)


def ImportRSL(file_name):
    # create a .csv copy of the file
    file_csv = file_name[:-4] + ".csv"
    shutil.copyfile(file_name, file_csv)  

    columns = (0,1,2,5,11,12,13,15,16,17,23,24,25,62,63,64,65,66,71,34,42,72)
    hdrs=  {'Section Name':'name',          ' Parent Name':'parent',\
            ' Phasing':'phasing',           ' Miles From Source':'miles',\
            ' Base Volts (A)':'volta',      ' Base Volts (B)':'voltb',\
            ' Base Volts (C)':'voltc',      ' Section Drop (A)':'sdropa',\
            ' Section Drop (B)':'sdropb',   ' Section Drop (C)':'sdropc',\
            ' Through Amps (A)':'ampsa',    ' Through Amps (B)':'ampsb',\
            ' Through Amps (C)':'ampsc',    ' Min Phase-Ground':'minlg',\
            ' Max Fault - LG':'maxlg',      ' Max Fault - LL':'maxll',\
            ' Max Fault - LLG':'maxllg',    ' Max Fault - LLLG':'maxlllg',\
            ' Source Name':'sub',           ' Through kW (Bal)':'kW',\
            ' % PF (Bal)':'PF',             ' Feeder Name':'feeder'}

    df = pd.read_csv(file_csv, delimiter=",", comment = None, usecols = columns)
    df = df.rename(columns=hdrs)

    os.remove(file_csv)

    return df

def ImportSTD(data, file_name):
    # create a .csv copy of the file
    file_csv = file_name[:-4] + ".csv"
    shutil.copyfile(file_name, file_csv)

    df = pd.read_csv(file_csv, delimiter=",", comment = None, skiprows = 1, usecols = (0,1), names = ('name','device'))
    df = pd.merge(data, df, on='name', how='left')

    # check for empty cells in matched column. if one exists, then flag an error
    if len(np.where(pd.isnull(df.device))[0]) > 0:
        Status("ERROR - RSL and STD files do not match. Ensure files were exported from model simultaneously.")
        input("PROGRAM TERMINATED")
        quit()

    # initialize phase-specific parent as the element's parent
    df['parenta'] = df['parent']
    df['parentb'] = df['parent']
    df['parentc'] = df['parent']

    # for nodes (device=8) read in columns 27,28,29 (phase-specific parents) of std file
    # overwrite a,b,c parents for all nodes using std file data
    for i in np.where(df['device'] == 8)[0]:
        temp = np.loadtxt(file_csv, dtype='U25', delimiter=",", comments=None, \
                          usecols=(0, 1, 27, 28, 29), skiprows=i+1, max_rows=1) # only read one row
        df.iloc[i, df.columns.get_loc('parenta')] = temp[2] # node's A parent
        df.iloc[i, df.columns.get_loc('parentb')] = temp[3] # node's B parent
        df.iloc[i, df.columns.get_loc('parentc')] = temp[4] # node's C parent

    os.remove(file_csv)
    return df

def RegulatorBypass(df):
    # WindMil uses a negative section voltage drop for regulators.
    # set regulator (device=4) section drop to 0 for accumulated voltage calc
    for i in np.where(df['device'] == 4)[0]:
        df.iloc[i, df.columns.get_loc('sdropa')] = 0
        df.iloc[i, df.columns.get_loc('sdropb')] = 0
        df.iloc[i, df.columns.get_loc('sdropc')] = 0
    return df

def Status(text):
    global start_time
    current_time = "{:.2f}".format(round(time.time() - start_time, 2))
    sys.stdout.write(str(current_time))
    sys.stdout.write('\t')
    sys.stdout.write('s:  ')
    sys.stdout.write(text)
    sys.stdout.write('\n')

def Counter(i, n):
    sys.stdout.write('\r')
    sys.stdout.write('            ')
    sys.stdout.write(str(i + 1))
    sys.stdout.write(' / ')
    sys.stdout.write(str(n))
    sys.stdout.write(' elements')

def MinVoltage(df):
    df2 = df[df[['volta','voltb','voltc']] != 0]
    df2 = df2[['volta','voltb','voltc']]

    df['voltage'] = df2.min(axis=1)
    return df

def DropAccumulator(df):
    # handle all nodes first with raw section voltage drops
    # the next sequence overwrites these values for the accumulated voltage drop
    node_time = time.time()
    node_count = len(np.where(df['device'] == 8)[0])

    for i in np.where(df['device'] == 8)[0]:
        Counter(i, len(df))
        sys.stdout.write('\t')
        sys.stdout.write('*NODE* - Time intensive nodes calculated first.')

        NodeDropAccumulator(df, i)

    if node_count > 0:
        print('\r','          ', node_count, 'nodes added', "{:.2f}".format(round(time.time() - node_time, 2)),\
              'seconds to duration.                                                             ')

    df['accdrop'] = 0
    for i in range(0,len(df)):
        if df.iloc[i, df.columns.get_loc('device')] != 8: # For all other devices, parent's section drop for all phases valid
            Counter(i, len(df))

            if df.iloc[i, df.columns.get_loc('parent')] in a_dict:
                df.iloc[i, df.columns.get_loc('sdropa')] = df.iloc[i, df.columns.get_loc('sdropa')] + a_dict[df.iloc[i, df.columns.get_loc('parent')]]      
            if df.iloc[i, df.columns.get_loc('parent')] in b_dict:
                df.iloc[i, df.columns.get_loc('sdropb')] = df.iloc[i, df.columns.get_loc('sdropb')] + b_dict[df.iloc[i, df.columns.get_loc('parent')]]   
            if df.iloc[i, df.columns.get_loc('parent')] in c_dict:
                df.iloc[i, df.columns.get_loc('sdropc')] = df.iloc[i, df.columns.get_loc('sdropc')] + c_dict[df.iloc[i, df.columns.get_loc('parent')]]  
            
            # store each phase voltage drop for current element in dictionary
            a_dict[df.iloc[i, df.columns.get_loc('name')]] = df.iloc[i, df.columns.get_loc('sdropa')]   
            b_dict[df.iloc[i, df.columns.get_loc('name')]] = df.iloc[i, df.columns.get_loc('sdropb')]   
            c_dict[df.iloc[i, df.columns.get_loc('name')]] = df.iloc[i, df.columns.get_loc('sdropc')]              

        if df.iloc[i, df.columns.get_loc('phasing')] in ["ABC","ACB","BAC","BCA","CAB","CBA"]:
            df.iloc[i, df.columns.get_loc('accdrop')] = max(df.iloc[i, df.columns.get_loc('sdropa')],\
                df.iloc[i, df.columns.get_loc('sdropb')],df.iloc[i, df.columns.get_loc('sdropc')])
        if df.iloc[i, df.columns.get_loc('phasing')] in ["AB","BA"]:
            df.iloc[i, df.columns.get_loc('accdrop')] = max(df.iloc[i, df.columns.get_loc('sdropa')], df.iloc[i, df.columns.get_loc('sdropb')])
        if df.iloc[i, df.columns.get_loc('phasing')] in ["AC","CA"]:
            df.iloc[i, df.columns.get_loc('accdrop')] = max(df.iloc[i, df.columns.get_loc('sdropa')], df.iloc[i, df.columns.get_loc('sdropc')])
        if df.iloc[i, df.columns.get_loc('phasing')] in ["BC","CB"]:
            df.iloc[i, df.columns.get_loc('accdrop')] = max(df.iloc[i, df.columns.get_loc('sdropb')], df.iloc[i, df.columns.get_loc('sdropc')])
        if df.iloc[i, df.columns.get_loc('phasing')] == "A":
            df.iloc[i, df.columns.get_loc('accdrop')] = df.iloc[i, df.columns.get_loc('sdropa')]
        if df.iloc[i, df.columns.get_loc('phasing')] == "B":
            df.iloc[i, df.columns.get_loc('accdrop')] = df.iloc[i, df.columns.get_loc('sdropb')]
        if df.iloc[i, df.columns.get_loc('phasing')] == "C":
            df.iloc[i, df.columns.get_loc('accdrop')] = df.iloc[i, df.columns.get_loc('sdropc')]
    
    sys.stdout.write('\n')
    return df

def NodeDropAccumulator(df, x):
    # starting at node, iterates its parent-child relationship all the way up to the source on a
    # per-phase basis. This is because there could be a different number of upline elements for each phase

    # A-Phase --------------------------------------------------------------------------------------------------------
    # initial parent-child relationship
    chain_name_a = [df.iloc[x, df.columns.get_loc('name')], df.iloc[x, df.columns.get_loc('parenta')]]                          
    chain_drop_a = [df.iloc[x, df.columns.get_loc('sdropa')]]
    while True:
        # count down from element (up the array from the element)
        found = 0                                                           
        for i in reversed(range(0,x)): 
            if df.iloc[i, df.columns.get_loc('name')] == chain_name_a[-1]:
                chain_name_a = np.append(chain_name_a, df.iloc[i, df.columns.get_loc('parenta')])
                chain_drop_a = np.append(chain_drop_a, df.iloc[i, df.columns.get_loc('sdropa')]) 
                found = 1
                break

        # node parent can exist below the node - if parent not found above,
        # then start at element row and look below
        if found == 0:
            for i in range(x,len(df)):
                if df.iloc[i, df.columns.get_loc('name')] == chain_name_a[-1]:
                    chain_name_a = np.append(chain_name_a, df.iloc[i, df.columns.get_loc('parenta')])
                    chain_drop_a = np.append(chain_drop_a, df.iloc[i, df.columns.get_loc('sdropa')])
                    break

        # quit if no phase parent exists (2-Phase nodes have a '' parent)
        if chain_name_a[-1] == '':
            chain_drop_a = [0,0]
            break

        # quit once root is hit
        if chain_name_a[-1] == 'ROOT':
            break

    # B-Phase --------------------------------------------------------------------------------------------------------
    # initial parent-child relationship
    chain_name_b = [df.iloc[x, df.columns.get_loc('name')], df.iloc[x, df.columns.get_loc('parentb')]]                          
    chain_drop_b = [df.iloc[x, df.columns.get_loc('sdropb')]]
    while True:
        # count down from element (up the array from the element)
        found = 0                                                           
        for i in reversed(range(0,x)): 
            if df.iloc[i, df.columns.get_loc('name')] == chain_name_b[-1]:
                chain_name_b = np.append(chain_name_b, df.iloc[i, df.columns.get_loc('parentb')])
                chain_drop_b = np.append(chain_drop_b, df.iloc[i, df.columns.get_loc('sdropb')]) 
                found = 1
                break

        # node parent can exist below the node - if parent not found above,
        # then start at element row and look below
        if found == 0:
            for i in range(x,len(df)):
                if df.iloc[i, df.columns.get_loc('name')] == chain_name_b[-1]:
                    chain_name_b = np.append(chain_name_b, df.iloc[i, df.columns.get_loc('parentb')])
                    chain_drop_b = np.append(chain_drop_b, df.iloc[i, df.columns.get_loc('sdropb')])
                    break

        # quit if no phase parent exists (2-Phase nodes have a '' parent)
        if chain_name_b[-1] == '':
            chain_drop_b = [0,0]
            break

        # quit once root is hit
        if chain_name_b[-1] == 'ROOT':
            break

    # C-Phase --------------------------------------------------------------------------------------------------------
    # initial parent-child relationship
    chain_name_c = [df.iloc[x, df.columns.get_loc('name')], df.iloc[x, df.columns.get_loc('parentc')]]                          
    chain_drop_c = [df.iloc[x, df.columns.get_loc('sdropc')]]
    while True:
        # count down from element (up the array from the element)
        found = 0                                                           
        for i in reversed(range(0,x)): 
            if df.iloc[i, df.columns.get_loc('name')] == chain_name_c[-1]:
                chain_name_c = np.append(chain_name_c, df.iloc[i, df.columns.get_loc('parentc')])
                chain_drop_c = np.append(chain_drop_c, df.iloc[i, df.columns.get_loc('sdropc')]) 
                found = 1
                break

        # node parent can exist below the node - if parent not found above,
        # then start at element row and look below
        if found == 0:
            for i in range(x,len(df)):
                if df.iloc[i, df.columns.get_loc('name')] == chain_name_c[-1]:
                    chain_name_c = np.append(chain_name_c, df.iloc[i, df.columns.get_loc('parentc')])
                    chain_drop_c = np.append(chain_drop_c, df.iloc[i, df.columns.get_loc('sdropc')])
                    break

        # quit if no phase parent exists (2-Phase nodes have a '' parent)
        if chain_name_c[-1] == '':
            chain_drop_c = [0,0]
            break

        # quit once root is hit
        if chain_name_c[-1] == 'ROOT':
            break


    # sum drop from source to element for accumulated voltage drop
    df.iloc[x, df.columns.get_loc('sdropa')] = sum(chain_drop_a)         
    df.iloc[x, df.columns.get_loc('sdropb')] = sum(chain_drop_b)
    df.iloc[x, df.columns.get_loc('sdropc')] = sum(chain_drop_c)

    # store the results for nodes in global dictionaries
    a_dict[df.iloc[x, df.columns.get_loc('name')]] = df.iloc[x, df.columns.get_loc('sdropa')]   # a-phase voltage drop
    b_dict[df.iloc[x, df.columns.get_loc('name')]] = df.iloc[x, df.columns.get_loc('sdropb')]   # b-phase voltage drop
    c_dict[df.iloc[x, df.columns.get_loc('name')]] = df.iloc[x, df.columns.get_loc('sdropc')]   # c-phase voltage drop    

    return

def RegulatorVoltageCorrection(df):
    # Milsoft sets regulator voltage to 126V per phase. Set to parent's voltage
    for i in range(0, len(df)):
        if df.iloc[i, df.columns.get_loc('device')] == 4:  # in std file, "4" represents voltage regulators
            for j in reversed(range(0,i)): # start at i and count downwards (up the matrix) to find parent (parent always above)
                if df.iloc[i, df.columns.get_loc('parent')] == df.iloc[j, df.columns.get_loc('name')]:
                    df.iloc[i, df.columns.get_loc('voltage')] = df.iloc[j, df.columns.get_loc('voltage')]  # Set regulator voltage to parent's voltage
                    break
    return df

def OutputData(e_df, p_df):
    # rearrange and round
    e_df = e_df[['name','sub','voltage','accdrop','miles','ampsa','ampsb','ampsc','minlg','maxfault']]
    e_df = e_df.round({'miles':1, 'ampsa':1, 'ampsb':1, 'ampsc':1, 'accdrop':1, 'drop':1, 'voltage':1})

    p_df = p_df[['name','sub','voltage','accdrop','miles','ampsa','ampsb','ampsc','minlg','maxfault']]
    p_df = p_df.round({'miles':1, 'ampsa':1, 'ampsb':1, 'ampsc':1, 'accdrop':1, 'drop':1, 'voltage':1})

    data = e_df.merge(p_df, how='outer', on='name', suffixes=('_e','_p'))

    # insert blank columns for separation and readibility
    data.insert(1, "Existing", "  |") 
    data.insert(11, "Proposed", "  |") 
    data.insert(21, "Version", "") 
    data.insert(21, "", "") 

    headers = ['Names','Existing','Source','Voltage','Acc Drop','Miles','I AØ','I BØ','I CØ','Min(Flt)','Max(Flt)',\
                       'Proposed','Source','Voltage','Acc Drop','Miles','I AØ','I BØ','I CØ','Min(Flt)','Max(Flt)', '','Version']

    data.iloc[0, data.columns.get_loc('Version')] = "WindMil Data 1.2"

    data.to_csv('OUTPUT DATA.csv', index = False, header=headers, encoding='utf-8-sig')

main()

