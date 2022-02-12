import os
import sys
import numpy as np
import pandas as pd
import time
import shutil
from GUI_AutoCAD import *

start_time = 0

def main():
    output_file, attribute_file = FileLocator()
    
    global start_time
    start_time = time.time()

    FileCheck(output_file, attribute_file)

    Status("Importing data.")
    output_data = pd.read_csv(output_file, delimiter=",", comment = None, low_memory=False)
    attribute_data = pd.read_csv(attribute_file, delimiter="\t", comment = None, low_memory=False)

    VersionCheck(output_data)
    MoveFiles('DATA', ['.csv', '.txt'])

    BlockCheck(attribute_data)
    
    mismatches = MismatchCheck(attribute_data, output_data)

    Status("Updating AutoCAD attribute file with WindMil data.")
    attribute_data = PopulateData(attribute_data, output_data)

    if len(mismatches) > 0:
        Status("Updating AutoCAD attribute file with mismatch warnings.")
        attribute_data = PopulateMismatch(attribute_data, mismatches)

    np.savetxt("OUTPUT ATTRIBUTES.txt", attribute_data, fmt='%s', delimiter='\t')
    Status("Complete. Use 'OUTPUT ATTRIBUTES.txt' for AutoCAD ATTIN command.")

    print('\n')
    input("Press Enter to complete.")


def PopulateData(attribute_data, output_data):

    df = attribute_data.merge(output_data, how='inner', left_on='DEVICE', right_on='Names')
    df[['LINE1','LINE2','LINE3','MAX','MIN','VOLTS','DROP','DIFF','DIST']] = "<>"
    
    for i in range(0, len(df)):
        if df.iloc[i, df.columns.get_loc('BLOCKNAME')] == 'Fault_Currents':
            df.iloc[i, df.columns.get_loc('MAX')] = int(df.iloc[i, df.columns.get_loc('Max(Flt).1')])
            df.iloc[i, df.columns.get_loc('MIN')] = int(df.iloc[i, df.columns.get_loc('Min(Flt).1')])

        if df.iloc[i, df.columns.get_loc('BLOCKNAME')] == 'Voltage_Box':
            exst_volt = round(df.iloc[i, df.columns.get_loc('Voltage')], 1)
            exst_drop = round(df.iloc[i, df.columns.get_loc('Acc Drop')], 1)
            prop_drop = round(df.iloc[i, df.columns.get_loc('Acc Drop.1')], 1)
            exst_mile = round(df.iloc[i, df.columns.get_loc('Miles')], 1)

            if np.isnan(exst_volt):
                df.iloc[i, df.columns.get_loc('VOLTS')] = "-"
            else:
                df.iloc[i, df.columns.get_loc('VOLTS')] = exst_volt
                
            if np.isnan(exst_drop):
                df.iloc[i, df.columns.get_loc('DROP')] = "-"
            else:
                df.iloc[i, df.columns.get_loc('DROP')] = exst_drop

            if np.isnan(prop_drop):
                df.iloc[i, df.columns.get_loc('DIFF')] = "-"
            else:
                df.iloc[i, df.columns.get_loc('DIFF')] = prop_drop

            if np.isnan(exst_mile):
                df.iloc[i, df.columns.get_loc('DIST')] = "-"
            else:
                df.iloc[i, df.columns.get_loc('DIST')] = exst_mile

        if df.iloc[i, df.columns.get_loc('BLOCKNAME')] == 'Load_Currents':
            a_current = df.iloc[i, df.columns.get_loc('I AØ')]
            b_current = df.iloc[i, df.columns.get_loc('I BØ')]
            c_current = df.iloc[i, df.columns.get_loc('I CØ')]

            if a_current != 0 and not(np.isnan(a_current)):
                df.iloc[i, df.columns.get_loc('LINE1')] = "A" + str(a_current)

            if b_current != 0 and not(np.isnan(b_current)):
                if df.iloc[i, df.columns.get_loc('LINE1')] == "<>":
                    df.iloc[i, df.columns.get_loc('LINE1')] = "B" + str(b_current)
                elif df.iloc[i, df.columns.get_loc('LINE1')] != "<>":
                    df.iloc[i, df.columns.get_loc('LINE2')] = "B" + str(b_current)

            if c_current != 0 and not(np.isnan(c_current)):
                if df.iloc[i, df.columns.get_loc('LINE1')] == "<>":
                    df.iloc[i, df.columns.get_loc('LINE1')] = "C" + str(c_current)
                elif df.iloc[i, df.columns.get_loc('LINE2')] == "<>":
                    df.iloc[i, df.columns.get_loc('LINE2')] = "C" + str(c_current)
                else:
                    df.iloc[i, df.columns.get_loc('LINE3')] = "C" + str(c_current)

            # case when existing current all 0 or all null
            if df.iloc[i, df.columns.get_loc('LINE1')] == "<>" \
            and df.iloc[i, df.columns.get_loc('LINE2')] == "<>" \
            and df.iloc[i, df.columns.get_loc('LINE3')] == "<>":
                df.iloc[i, df.columns.get_loc('LINE1')] = "0.0"

    # slice attribute data, remove output data columns
    df = df.iloc[:,0:14]
    return df


def PopulateMismatch(df, mismatches):
    for i in range(0, len(df)):
        if df.iloc[i, df.columns.get_loc('DEVICE')] in mismatches:

            if df.iloc[i, df.columns.get_loc('BLOCKNAME')] == 'Fault_Currents':
                df.iloc[i, df.columns.get_loc('MAX')] = "DEVICE"
                df.iloc[i, df.columns.get_loc('MIN')] = "MISMATCH"

            if df.iloc[i, df.columns.get_loc('BLOCKNAME')] == 'Voltage_Box':
                df.iloc[i, df.columns.get_loc('VOLTS')] = "DEVICE"
                df.iloc[i, df.columns.get_loc('DROP')]  = "MISMATCH"
                df.iloc[i, df.columns.get_loc('DIFF')]  = "CHECK"
                df.iloc[i, df.columns.get_loc('DIST')]  = "LINK"

            if df.iloc[i, df.columns.get_loc('BLOCKNAME')] == 'Load_Currents':
                df.iloc[i, df.columns.get_loc('LINE1')] = "DEVICE"
                df.iloc[i, df.columns.get_loc('LINE2')] = "MISMATCH"
                df.iloc[i, df.columns.get_loc('LINE3')] = "CHECK"
    return df


def VersionCheck(df):
    version = df.iloc[0,22]

    if version != "WindMil Data 1.2":
        Status("ERROR - OUTPUT_DATA.csv not valid. Please use WindMil Data version 1.2")
        input("Press Enter to exit.")
        quit()
    else:
        pass


def FileCheck(output_file, attribute_file):
    if output_file == None or attribute_file == None:
        Status("ERROR - One or more files not selected.")
        input("Press Enter to exit.")
        quit()
    else:
        pass


def BlockCheck(attribute_data):
    block_types = attribute_data['BLOCKNAME'].unique()
    valid_block_types = ['Load_Currents', 'Fault_Currents', 'Voltage_Box']
    invalid_block_types = list(set(block_types) - set(valid_block_types))

    for i in block_types:
        if i not in valid_block_types:
            Status("ERROR - One or more block types invalid. Check LISP routine." + \
                   "\n\t\t\t\tInvalid block types used in map:")
            for i in invalid_block_types:
                print("\t\t\t\t\t" + i)
            input("Press Enter to exit.")
            quit()
        else:
            pass 
    Status("Valid 'BLOCKNAME' was used for each attribute block.") 


def MismatchCheck(attribute_data, output_data):
    attribute_file_device_list = attribute_data['DEVICE']
    mismatches = []

    matched = attribute_data.merge(output_data, how='inner', left_on='DEVICE', right_on='Names')
    matched_device_list = matched['DEVICE']

    qty_total = attribute_data.shape[0]
    qty_matched = matched.shape[0]
    qty_mismatch = qty_total - qty_matched

    if qty_mismatch == 0:
        Status("All 'DEVICE' links were matched to WindMil data.")
    else:
        mismatches = list(set(attribute_file_device_list) - set(matched_device_list))
        Status(str(qty_mismatch) + " attribute block(s) were not linked to WindMil data. See file: OUTPUT WARNING - MISMATCH")
        np.savetxt("OUTPUT WARNING - MISMATCH.txt", mismatches, fmt='%s', delimiter='\t')

    return mismatches


def Status(text):
    global start_time
    current_time = "{:.2f}".format(round(time.time() - start_time, 2))
    sys.stdout.write(str(current_time))
    sys.stdout.write('\t')
    sys.stdout.write('s:  ')
    sys.stdout.write(text)
    sys.stdout.write('\n')


def MoveFiles(new_dir, extensions):
    '''
    Creates new directory 'new_dir'
    Moves all files in working directory to new directory that
    have extension types in the 'extensions' list.
    '''
    dir_path = os.getcwd()
    new_path = os.path.join(dir_path, new_dir)

    # create new directory if it doesn't already exist
    if new_dir not in os.listdir(dir_path):
        os.mkdir(new_path)

    # relocate files with specified extensions to /EXPORT
    for i in extensions:
        files = os.listdir(dir_path)
        for file in files:
            if file.endswith(i):
                shutil.move(os.path.join(dir_path, file), os.path.join(new_path, file))


main()
