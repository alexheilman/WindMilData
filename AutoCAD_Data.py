import os
import sys
import numpy as np
import time
import shutil
from GUI_AutoCAD import *

start_time = 0

def main():
    #output_file, attribute_file = FileLocator()
    output_file = 'C:/Users/aheilman/Documents/GitHub/WindMilData/OUTPUT DATA.csv'
    attribute_file = 'C:/Users/aheilman/Documents/GitHub/WindMilData/MO23 Work Plan Map.txt'

    global start_time
    start_time = time.time()

    if output_file == None or attribute_file == None:
        Status("ERROR - One or more files not selected.")
        input("Press Enter to exit.")
        quit()

    else:
        Status("Importing data.")
        output_data = np.loadtxt(output_file, dtype='U25', delimiter=",", comments=None, skiprows=3)  # Read in RSL from CSV copy
        attribute_data = np.loadtxt(attribute_file, dtype='U25', delimiter="\t", comments=None, skiprows=0)  # Read in RSL from CSV copy
        
        MoveFiles('DATA', ['.csv', '.txt'])


        Status("Updating attribute file with model data.")
        attribute_data, mismatches, mismatch_names = SyncData(output_data, attribute_data)
        np.savetxt("OUTPUT ATTRIBUTES.txt", attribute_data, fmt='%s', delimiter='\t')
        print('')

        if mismatches == 0:
            Status("All attribute blocks were linked to model data.")
        else:
            Status(str(mismatches) + " attribute blocks were not linked to model data.  See OUTPUT WARNING - MISMATCH.txt")
            np.savetxt("OUTPUT WARNING - MISMATCH.txt", mismatch_names, fmt='%s', delimiter='\t')

        negative_count, negative_names = NegPhaseCurrents(attribute_data)
        if negative_count == 0:
            Status("No instances of negative phase current in attribute file.")
        else:
            Status(str(negative_count) + " instances of negative phase current in attribute file. See OUTPUT WARNING - NEGATIVE CURRENT.txt")
            np.savetxt("OUTPUT WARNING - NEGATIVE CURRENT.txt", negative_names, fmt='%s', delimiter='\t')


        Status("Complete.")

        print('\n')
        input("Press Enter to complete.")


def SyncData(output_data, attribute_data):
    mismatch_names = []

    # column order changes, assign column number by header
    columns = attribute_data[0,:]
    for i in range(0,len(columns)):
        if columns[i] == atttxt_block:
            attcol_block = i
        if columns[i] == atttxt_name:
            attcol_name = i
        if columns[i] == atttxt_max:
            attcol_max = i
        if columns[i] == atttxt_min:
            attcol_min = i
        if columns[i] == atttxt_i1:
            attcol_i1 = i
        if columns[i] == atttxt_i2:
            attcol_i2 = i
        if columns[i] == atttxt_i3:
            attcol_i3 = i
        if columns[i] == atttxt_volt:
            attcol_volt = i
        if columns[i] == atttxt_edrop:
            attcol_edrop = i
        if columns[i] == atttxt_pdrop:
            attcol_pdrop = i
        if columns[i] == atttxt_miles:
            attcol_miles = i

    # Standard
    outcol_name     = 0 #column 1
    outcol_volt     = 1 #column 2
    outcol_edrop    = 2 #column 3
    outcol_miles    = 3 #column 4
    outcol_ia       = 4 #column 5
    outcol_ib       = 5 #column 6
    outcol_ic       = 6 #column 7
    outcol_pdrop    = 10 #column 11
    outcol_min      = 15 #column 16
    outcol_max      = 16 #column 17

    mismatches = 0      # count how many elements were not found in model data

    for i in range(1, len(attribute_data)):
        match = 0       # match indicator new for each attribute
        Counter(i, len(attribute_data))
        for j in range(0, len(output_data)):

            if attribute_data[i, attcol_name] == output_data[j, outcol_name]:
                match = 1       # match indication when element found in model data

                # sync data for Fault_Currents blocks
                if attribute_data[i, attcol_block] == Fault_Currents:
                    # max fault current
                    if output_data[j, outcol_max] == "nan":
                        attribute_data[i, attcol_max] = "-"
                    else:
                        temp_max = output_data[j, outcol_max]
                        attribute_data[i, attcol_max] =  temp_max[:-2] #removes the ".0" from string

                    # min fault current
                    if output_data[j, outcol_min] == "nan":
                        attribute_data[i, attcol_min] = "-"
                    else:
                        temp_min = output_data[j, outcol_min]
                        attribute_data[i, attcol_min] =  temp_min[:-2] #removes the ".0" from string

                # sync data for Load_Currents blocks
                if attribute_data[i, attcol_block] == Load_Currents:
                    attribute_data[i, attcol_i1] = "" # clear existing data
                    attribute_data[i, attcol_i2] = "" # clear existing data
                    attribute_data[i, attcol_i3] = "" # clear existing data

                    if (output_data[j, outcol_ia] != "0.0" and output_data[j, outcol_ia] != "nan" and output_data[j, outcol_ia] != "-0.0" and output_data[j, outcol_ia] != "0"):
                        attribute_data[i, attcol_i1] = "A" + output_data[j, outcol_ia]
                    if (output_data[j, outcol_ib] != "0.0" and output_data[j, outcol_ib] != "nan" and output_data[j, outcol_ib] != "-0.0" and output_data[j, outcol_ib] != "0"):
                        if attribute_data[i, attcol_i1] == "":
                            attribute_data[i, attcol_i1] = "B" + output_data[j, outcol_ib]
                        else:
                            attribute_data[i, attcol_i2] = "B" + output_data[j, outcol_ib]
                    if (output_data[j, outcol_ic] != "0.0" and output_data[j, outcol_ic] != "nan" and output_data[j, outcol_ic] != "-0.0" and output_data[j, outcol_ic] != "0"):
                        if attribute_data[i, attcol_i1] == "":
                            attribute_data[i, attcol_i1] = "C" + output_data[j, outcol_ic]
                        else:
                            if attribute_data[i, attcol_i2] == "":
                                attribute_data[i, attcol_i2] = "C" + output_data[j, outcol_ic]
                            else:
                                attribute_data[i, attcol_i3] = "C" + output_data[j, outcol_ic]

                # sync data for Voltage_Box blocks
                if attribute_data[i, attcol_block] == Voltage_Box:
                    # voltage
                    if output_data[j, outcol_volt] == "nan":
                        attribute_data[i, attcol_volt] = "-"
                    else:
                        attribute_data[i, attcol_volt] = output_data[j, outcol_volt]

                    # existing voltage drop
                    if output_data[j, outcol_edrop] == "nan":
                        attribute_data[i, attcol_edrop] = "-"
                    else:
                        attribute_data[i, attcol_edrop] = output_data[j, outcol_edrop]

                    # proposed voltage drop
                    if output_data[j, outcol_pdrop] == "nan":
                        attribute_data[i, attcol_pdrop] = "-"
                    else:
                        attribute_data[i, attcol_pdrop] = output_data[j, outcol_pdrop]

                    # existing miles
                    if output_data[j, outcol_miles] == "nan":
                        attribute_data[i, attcol_miles] = "-"
                    else:
                        attribute_data[i, attcol_miles] = output_data[j, outcol_miles]

                break


        # assign mismatch to appropriate fields attribute not in model data (match == 0)
        if match == 0:
            mismatches = mismatches + 1
            if attribute_data[i, attcol_block] == Fault_Currents:
                attribute_data[i, attcol_max] = Mismatch_Val
                attribute_data[i, attcol_min] = Mismatch_Val
            if attribute_data[i, attcol_block] == Load_Currents:
                attribute_data[i, attcol_i1] = Mismatch_Val
                attribute_data[i, attcol_i2] = Mismatch_Val
                attribute_data[i, attcol_i3] = Mismatch_Val
            if attribute_data[i, attcol_block] == Voltage_Box:
                attribute_data[i, attcol_volt] = Mismatch_Val
                attribute_data[i, attcol_edrop] = Mismatch_Val
                attribute_data[i, attcol_pdrop] = Mismatch_Val
                attribute_data[i, attcol_miles] = Mismatch_Val

            mismatch_names.append(attribute_data[i, attcol_name])

    return attribute_data, mismatches, mismatch_names

def NegPhaseCurrents(attribute_data):
    negative_count = 0
    negative_names = []

    # find columns pertaining to phase currents
    columns = attribute_data[0,:]
    for i in range(0, len(columns)):
        if columns[i] == atttxt_name:
            attcol_name = i
        if columns[i] == atttxt_i1:
            attcol_i1 = i
        if columns[i] == atttxt_i2:
            attcol_i2 = i
        if columns[i] == atttxt_i3:
            attcol_i3 = i

    for i in range(0, len(attribute_data)):
        if '-' in attribute_data[i, attcol_i1]:
            negative_count = negative_count + 1
            negative_names.append(attribute_data[i, attcol_name])
        if '-' in attribute_data[i, attcol_i2]:
            negative_count = negative_count + 1
            negative_names.append(attribute_data[i, attcol_name])
        if '-' in attribute_data[i, attcol_i3]:
            negative_count = negative_count + 1
            negative_names.append(attribute_data[i, attcol_name])

    return negative_count, negative_names

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
    sys.stdout.write(' attribute blocks')

def MoveFiles(new_dir, extensions):
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
