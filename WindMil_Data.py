import os
import sys
import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import shutil
import time

E_RSL_file = 'null'
E_STD_file = 'null'
P_RSL_file = 'null'
P_STD_file = 'null'
start_time = 0
data_types = 0

# initialize voltage drop dictionaries globally (used across functions)
a_dict = {} # a-phase dictionary
b_dict = {} # b-phase dictionary
c_dict = {} # c-phase dictionary

def main():
    E_RSL_file, E_STD_file, P_RSL_file, P_STD_file = FileLocator()

    global start_time
    start_time = time.time()

    if E_RSL_file == 'null' or E_STD_file == 'null' or P_RSL_file == 'null' or P_STD_file == 'null':
        Status("ERROR - One or more files not selected.")
        input("PROGRAM TERMINATED")
        quit()

    else:
        Status("Importing data.")
        e_data = ImportData(E_RSL_file)
        p_data = ImportData(P_RSL_file)

        Status("Calculating maximum available fault.")
        e_data = MaxFault(e_data)
        p_data = MaxFault(p_data)

        Status("Calculating minimum voltage.")
        e_data = MinVoltage(e_data)
        p_data = MinVoltage(p_data)

        Status("Matching in STD file data.")
        e_data = STDFileData(e_data, E_STD_file)
        p_data = STDFileData(p_data, P_STD_file)

        #np.savetxt("Output30.csv", e_data, fmt='%s', delimiter=',')

        Status("Bypassing regulators.")
        e_data = RegulatorFinder(e_data)
        p_data = RegulatorFinder(p_data)

        Status("Calculating existing accumulated voltage drop.")
        e_data = DropAccumulator(e_data)
        Status("Calculating proposed accumulated voltage drop.")
        p_data = DropAccumulator(p_data)

        Status("Translating regulator voltages to source-side voltage.")
        e_data = RegulatorVoltageCorrection(e_data)
        p_data = RegulatorVoltageCorrection(p_data)

        Status("Merging data arrays.")
        data = DataMerge(e_data, p_data)

        Status("Formatting data array.")
        data = Finishing(data)


        Status("Complete.")

        print('\n')
        input("Press Enter to complete.")

def FileLocator():
    # mainloop settings
    root = tk.Tk()
    root.title('WindMil Data 1.1')
    root.geometry("700x222")
    root.grid_columnconfigure(0, weight = 1)
    root.grid_columnconfigure(1, weight=10000) # put weight in column 2, to make column 1 as small as possible
    style = ttk.Style(root)
    style.theme_use("clam")

    # string variables to be updated with file string
    string_E_RSL = tk.StringVar()
    string_E_RSL.set('No file selected.')
    string_P_RSL = tk.StringVar()
    string_P_RSL.set('No file selected.')
    string_E_STD = tk.StringVar()
    string_E_STD.set('No file selected.')
    string_P_STD = tk.StringVar()
    string_P_STD.set('No file selected.')

    def select_E_RSL():
        global E_RSL_file
        file_string = filedialog.askopenfilenames(
            parent=root,
            initialdir= os.getcwd(),
            initialfile='',
            filetypes=[("RSL", "*.rsl")])
        try:
            E_RSL_file = file_string[0]
            string_E_RSL.set(file_string[0])
        except IndexError:
            return

    def select_E_STD():
        global E_STD_file
        file_string = filedialog.askopenfilenames(
            parent=root,
            initialdir= os.getcwd(),
            initialfile='',
            filetypes=[("STD", "*.std")])
        try:
            E_STD_file = file_string[0]
            string_E_STD.set(file_string[0])
        except IndexError:
            return

    def select_P_RSL():
        global P_RSL_file
        file_string = filedialog.askopenfilenames(
            parent=root,
            initialdir= os.getcwd(),
            initialfile='',
            filetypes=[("RSL", "*.rsl")])
        try:
            P_RSL_file = file_string[0]
            string_P_RSL.set(file_string[0])
        except IndexError:
            return

    def select_P_STD():
        global P_STD_file
        file_string = filedialog.askopenfilenames(
            parent=root,
            initialdir= os.getcwd(),
            initialfile='',
            filetypes=[("STD", "*.std")])
        try:
            P_STD_file = file_string[0]
            string_P_STD.set(file_string[0])
        except IndexError:
            return

    ttk.Label(text="Select the exported RSL and STD WindMil files. If there is no proposed model, select the existing files for both").grid(row=1, columnspan = 2, padx=4, pady=4, sticky='ew')

    ttk.Button(root, text="Existing RSL file", command=select_E_RSL).grid(row=2, column=0, padx=4, pady=4, sticky='ew')
    ttk.Label(textvariable= string_E_RSL).grid(row=2, column=1, padx=4, pady=4, sticky='ew')

    ttk.Button(root, text="Existing STD file", command=select_E_STD).grid(row=3, column=0, padx=4, pady=4, sticky='ew')
    ttk.Label(textvariable=string_E_STD).grid(row=3, column=1, padx=4, pady=4, sticky='ew')

    ttk.Button(root, text="Proposed RSL file", command=select_P_RSL).grid(row=4, column=0, padx=4, pady=4, sticky='ew')
    ttk.Label(textvariable= string_P_RSL).grid(row=4, column=1, padx=4, pady=4, sticky='ew')

    ttk.Button(root, text="Proposed STD file", command=select_P_STD).grid(row=5, column=0, padx=4, pady=4, sticky='ew')
    ttk.Label(textvariable=string_P_STD).grid(row=5, column=1, padx=4, pady=4, sticky='ew')

    ttk.Button(root, text="Done", command= root.quit).grid(row=6, column=0, padx=4, pady=4, sticky='ew')

    root.mainloop()
    root.withdraw()
    return E_RSL_file, E_STD_file, P_RSL_file, P_STD_file

def ImportData(FileName):
    global data_types
    ThisFileRSL = FileName
    ThisFileCSV = FileName[:-4] + ".csv"


    shutil.copyfile(ThisFileRSL, ThisFileCSV)  # Copy RSL as a CSV

    columns = (0,1,2,5,11,12,13,15,16,17,23,24,25,62,63,64,65,66,48)
    data = np.loadtxt(ThisFileCSV, dtype='U25', delimiter=",", comments=None, skiprows=1, usecols = columns)  # Read in RSL from CSV copy
    os.remove(ThisFileCSV)  # Delete the temporary CSV copy, leaving the RSL

    # size string data type to length of max string length (for iteration speed)
    string_length = 0
    for i in range(1,len(data)):
        if len(data[i,0]) > string_length:
            string_length = len(data[i,0])
    string_dtype = 'U' + str(string_length)

    # (Column number in RSL file, (Record array label, Data type))
    name = (0, ('name', string_dtype))  # Section/Element Names
    parent = (1, ('parent', string_dtype))
    phasing = (2, ('phasing', 'U6'))
    miles = (3, ('miles', 'float32'))  # Total miles from source
    volta = (4, ('volta', 'float32'))  # Phase A element voltage on 120V basis
    voltb = (5, ('voltb', 'float32'))  # Phase B element voltage on 120V basis
    voltc = (6, ('voltc', 'float32'))  # Phase B element voltage on 120V basis
    sdropa = (7, ('sdropa', 'float32'))
    sdropb = (8, ('sdropb', 'float32'))
    sdropc = (9, ('sdropc', 'float32'))
    ampsa = (10, ('ampsa', 'float32'))
    ampsb = (11, ('ampsb', 'float32'))
    ampsc = (12, ('ampsc', 'float32'))
    minlg = (13, ('minlg', 'float32'))
    maxlg = (14, ('maxlg', 'float32'))
    maxll = (15, ('maxll', 'float32'))
    maxllg = (16, ('maxllg', 'float32'))
    maxlllg = (17, ('maxlllg', 'float32'))
    parenta = (1, ('parenta', string_dtype))   #section kvar(A) not needed - used for dummy column
    parentb = (1, ('parentb', string_dtype))   #section kvar(A) not needed - used for dummy column
    parentc = (1, ('parentc', string_dtype))   #section kvar(A) not needed - used for dummy column
    drop = (18, ('drop', 'float32'))            #section kvar(A) not needed - used for dummy column
    device = (18, ('device', '<i8'))            #section kvar(A) not needed - used for dummy column
    voltage = (18, ('voltage', 'float32'))      #section kvar(A) not needed - used for dummy column
    maxfault = (18, ('maxfault', 'float32'))    #section kvar(A) not needed - used for dummy column
    row = (18, ('row', 'float32'))              #section kvar(A) not needed - used for dummy column

    # Create array of tuples - name and data type
    data_types = [name[1], parent[1], phasing[1], miles[1], volta[1], voltb[1], voltc[1], \
                  sdropa[1], sdropb[1], sdropc[1], ampsa[1], ampsb[1], ampsc[1], minlg[1], maxlg[1], \
                  maxll[1], maxllg[1], maxlllg[1], parenta[1], parentb[1], parentc[1], drop[1], \
                  device[1], voltage[1], maxfault[1], row[1]]

    # Create array of data - skip first row header (1:) and specified column
    data = np.rec.array([data[:, name[0]],      data[:, parent[0]],    data[:, phasing[0]],   \
                        data[:, miles[0]],      data[:, volta[0]],     data[:, voltb[0]],     \
                        data[:, voltc[0]],      data[:, sdropa[0]],    data[:, sdropb[0]],    \
                        data[:, sdropc[0]],     data[:, ampsa[0]],     data[:, ampsb[0]],     \
                        data[:, ampsc[0]],      data[:, minlg[0]],     data[:, maxlg[0]],     \
                        data[:, maxll[0]],      data[:, maxllg[0]],    data[:, maxlllg[0]],   \
                        data[:, parenta[0]],    data[:, parentb[0]],   data[:, parentc[0]],   \
                        data[:, drop[0]],       data[:, device[0]],    data[:, voltage[0]],   \
                        data[:, maxfault[0]],   data[:, row[0]]],      dtype=data_types)

    # wipe out contents of dummy columns
    data.drop = 0
    data.device = 0
    data.voltage = 0
    data.maxfault = 0

    # preserve initial rank
    for i in range(0,len(data)):
        data.row[i] = i

    return data

def MaxFault(data):
    for i in range(0, len(data)):
        data.maxfault[i] = max(data.maxlg[i], data.maxll[i], data.maxllg[i], data.maxlllg[i])

    return data

def MinVoltage(data):
    # set zero voltages to 999 (A phase element will have 0 volts for B,C phases)
    for i in range(0,len(data)):
        if data.volta[i] == 0:
            data.volta[i] = 999
        if data.voltb[i] == 0:
            data.voltb[i] = 999
        if data.voltc[i] == 0:
            data.voltc[i] = 999

        # set voltage to the minimum of non zero voltages
        data.voltage[i] = min(data.volta[i], data.voltb[i], data.voltc[i])

        if data.voltage[i] == 999:
            data.voltage[i] = None

    return data

def STDFileData(data, FileName):
    ThisFileSTD = FileName
    ThisFileCSV = FileName[:-4] + ".csv"
    shutil.copyfile(ThisFileSTD, ThisFileCSV)

    # Read in STD from CSV copy - np.loadtxt has issues with varying columns by row, so only columns = 0,1 read in
    std = np.loadtxt(ThisFileCSV, dtype='U25', delimiter=",", comments=None, skiprows=1, usecols = (0,1))

    # Create array of data - specified columns
    std = np.rec.array([std[:, 0], std[:, 1]], dtype= [('name', 'U25'),('device', "<i8")])

    # STD file has varying columns which loadtxt cannot handle. Only read in columns 27,28,29 of STD
    # which are the multi-parents for nodes (device = 8)
    for i in range(0,len(data)):
        # find every node's phase-specific parents
        if std.device[i] == 8:
            temp = np.loadtxt(ThisFileCSV, dtype='U25', delimiter=",", comments=None, \
                              usecols=(0, 1, 27, 28, 29), skiprows=i+1, max_rows=1) # only read one row
            data.parenta[i] = temp[2] # node's A parent
            data.parentb[i] = temp[3] # node's B parent
            data.parentc[i] = temp[4] # node's C parent

        # store device type inside the array
        if data.name[i] == std.name[i]:
            data.device[i] = std.device[i]

    os.remove(ThisFileCSV)  # Delete the temporary CSV copy, leaving the STD

    # double check that all devices matched in - should be no 0 device codes
    # this error can occur if an existing RSL is paired with a proposed STD
    for i in range(0,len(data)):
        if data.device[i] == 0:
            Status('ERROR - One or more device codes not matched in. Verify STD and RSL files exported from model simultaneously.')
            input('PROGRAM TERMINATED')
            quit()

    return data

def RegulatorFinder(data):
    # Milsoft uses a negative section voltage drop for regulators - set to 0 for accumulated voltage calc
    for i in range(0,len(data)):
        if data.device[i] == 4:  # in std file, "4" represents voltage regulators
            data.sdropa[i] = 0
            data.sdropb[i] = 0
            data.sdropc[i] = 0
    return data

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

def DropAccumulator(data):
    # handle all nodes first with raw section voltage drops
    # the next sequence overwrites these values for the accumulated voltage drop
    node_time = time.time()
    node_count = 0
    for i in range(0,len(data)):
        if data.device[i] == 8: # Nodes == 8, look for node parent of each phase and add drop separately
            Counter(i, len(data))
            sys.stdout.write('\t')
            sys.stdout.write('*NODE* - Time intensive nodes calculated first.')
            node_count = node_count + 1
            NodeDropAccumulator(data, i)

    if node_count > 0:
        print('\r','          ', node_count, 'nodes added', "{:.2f}".format(round(time.time() - node_time, 2)),\
              'seconds to duration.                                                             ')

    for i in range(0,len(data)):
        if data.device[i] != 8: # For all other devices, parent's section drop for all phases valid
            Counter(i, len(data))

            if data.parent[i] in a_dict:
                data.sdropa[i] = data.sdropa[i] + a_dict[data.parent[i]]      
            if data.parent[i] in b_dict:
                data.sdropb[i] = data.sdropb[i] + b_dict[data.parent[i]]    
            if data.parent[i] in c_dict:
                data.sdropc[i] = data.sdropc[i] + c_dict[data.parent[i]]
                
            a_dict[data.name[i]] = data.sdropa[i]   # store a-phase voltage drop for current element in dictionary
            b_dict[data.name[i]] = data.sdropb[i]   # store b-phase voltage drop for current element in dictionary
            c_dict[data.name[i]] = data.sdropc[i]   # store c-phase voltage drop for current element in dictionary            

    # pick one drop value using element phasing
    print('\n','           Identifying maximum phase drop per element.')
    for i in range(0,len(data)):
        if data.phasing[i] == "ABC":
            data.drop[i] = max(data.sdropa[i],data.sdropb[i],data.sdropc[i])
        if data.phasing[i] == "AB":
            data.drop[i] = max(data.sdropa[i], data.sdropb[i])
        if data.phasing[i] == "AC":
            data.drop[i] = max(data.sdropa[i], data.sdropc[i])
        if data.phasing[i] == "BC":
            data.drop[i] = max(data.sdropb[i], data.sdropc[i])
        if data.phasing[i] == "A":
            data.drop[i] = data.sdropa[i]
        if data.phasing[i] == "B":
            data.drop[i] = data.sdropb[i]
        if data.phasing[i] == "C":
            data.drop[i] = data.sdropc[i]
    return data

def NodeDropAccumulator(data, x):
    # starting at node, iterates its parent-child relationship all the way up to the source on a
    # per-phase basis. This is because there could be a different number of upline elements for each phase

    # A-Phase --------------------------------------------------------------------------------------------------------
    chain_name_a = [data.name[x], data.parenta[x]]                          # initial parent-child relationship
    chain_drop_a = [data.sdropa[x]]                                         # section drop of current element
    while True:
        # count down from element (up the array from the element)
        found = 0                                                           # found indicator -skip next loop if needed
        for i in reversed(range(0,x)):                                      # from current row x towards 0
            if data.name[i] == chain_name_a[-1]:                            # match last element of chain to data array
                chain_name_a = np.append(chain_name_a, data.parenta[i])     # append parent's name
                chain_drop_a = np.append(chain_drop_a, data.sdropa[i])      # append section drop
                found = 1                                                   # parent found - skip the next for-loop
                break                                                       # quit iterating if found

        # node parent can exist below the node - if parent not found above,
        # then start at element row and look below
        if found == 0:                                                      # don't start if already found
            for i in range(x,len(data)):                                    # from current row x towards end of array
                if data.name[i] == chain_name_a[-1]:                        # match last element of chain to data array
                    chain_name_a = np.append(chain_name_a, data.parenta[i]) # append parent's name
                    chain_drop_a = np.append(chain_drop_a, data.sdropa[i])  # append section drop
                    break                                                   # quit iterating if found

        # quit if no phase parent exists (2-Phase nodes have a '' parent)
        if chain_name_a[-1] == '':
            chain_drop_a = [0,0]
            break

        # quit once root is hit
        if chain_name_a[-1] == 'ROOT':                                      # checks last entry to see if ROOT
            break

    # B-Phase --------------------------------------------------------------------------------------------------------
    chain_name_b = [data.name[x], data.parentb[x]]  # initial parent-child relationship
    chain_drop_b = [data.sdropb[x]]  # section drop of current element
    while True:
        # count down from element (up the array from the element)
        found = 0                                                           # found indicator -skip next loop if needed
        for i in reversed(range(0, x)):                                     # from current row x towards 0
            if data.name[i] == chain_name_b[-1]:                            # match last element of chain to data array
                chain_name_b = np.append(chain_name_b, data.parentb[i])     # append parent's name
                chain_drop_b = np.append(chain_drop_b, data.sdropb[i])      # append section drop
                found = 1                                                   # parent found - skip the next for-loop
                break                                                       # quit iterating if found

        # node parent can exist below the node - if parent not found above,
        # then start at element row and look below
        if found == 0:                                                      # don't start if already found
            for i in range(x, len(data)):                                   # from current row x towards end of array
                if data.name[i] == chain_name_b[-1]:                        # match last element of chain to data array
                    chain_name_b = np.append(chain_name_b, data.parentb[i]) # append parent's name
                    chain_drop_b = np.append(chain_drop_b, data.sdropb[i])  # append section drop
                    break                                                   # quit iterating if found

        # quit if no phase parent exists (2-Phase nodes have a '' parent)
        if chain_name_b[-1] == '':
            chain_drop_b = [0,0]
            break

        # quit once root is hit
        if chain_name_b[-1] == 'ROOT':                                      # checks last entry to see if ROOT
            break

    # C-Phase --------------------------------------------------------------------------------------------------------
    chain_name_c = [data.name[x], data.parentc[x]]  # initial parent-child relationship
    chain_drop_c = [data.sdropc[x]]  # section drop of current element
    while True:
        # count down from element (up the array from the element)
        found = 0                                                           # found indicator -skip next loop if needed
        for i in reversed(range(0, x)):                                     # from current row x towards 0
            if data.name[i] == chain_name_c[-1]:                            # match last element of chain to data array
                chain_name_c = np.append(chain_name_c, data.parentc[i])     # append parent's name
                chain_drop_c = np.append(chain_drop_c, data.sdropc[i])      # append section drop
                found = 1                                                   # parent found - skip the next for-loop
                break                                                       # quit iterating if found

        # node parent can exist below the node - if parent not found above,
        # then start at element row and look below
        if found == 0:                                                      # don't start if already found
            for i in range(x, len(data)):                                   # from current row x towards end of array
                if data.name[i] == chain_name_c[-1]:                        # match last element of chain to data array
                    chain_name_c = np.append(chain_name_c, data.parentc[i]) # append parent's name
                    chain_drop_c = np.append(chain_drop_c, data.sdropc[i])  # append section drop
                    break                                                   # quit iterating if found

        # quit if no phase parent exists (2-Phase nodes have a '' parent)
        if chain_name_c[-1] == '':
            chain_drop_c = [0,0]
            break

        # quit once root is hit
        if chain_name_c[-1] == 'ROOT':                                      # checks last entry to see if ROOT
            break

    # sum drop from source to element for accumulated voltage drop
    data.sdropa[x] = sum(chain_drop_a)         
    data.sdropb[x] = sum(chain_drop_b)
    data.sdropc[x] = sum(chain_drop_c)

    # store the results for nodes in global dictionaries
    a_dict[data.name[x]] = data.sdropa[x]   # a-phase voltage drop
    b_dict[data.name[x]] = data.sdropb[x]   # b-phase voltage drop
    c_dict[data.name[x]] = data.sdropc[x]   # c-phase voltage drop         

    return

def RegulatorVoltageCorrection(data):
    # Milsoft sets regulator voltage to 126V per phase. Set to parent's voltage
    for i in range(0,len(data)):
        if data.device[i] == 4:  # in std file, "4" represents voltage regulators
            for j in reversed(range(0,i)): # start at i and count downwards (up the matrix) to find parent (parent always above)
                if data.parent[i] == data.name[j]:
                    data.voltage[i] = data.voltage[j] ## Set regulator voltage to parent's voltage
                    break
    return data

def DataMerge(e_data, p_data):
    # For cases where existing data does not exist in proposed data = remove these elements and place in new array
    deletions = np.setdiff1d(np.array(e_data.name), np.array(p_data.name))
    remove_rows = []
    e_data_deletions = np.recarray((len(deletions),1), dtype = data_types) # initialize blank
    for i in range(0,len(deletions)):
        for j in range(0,len(e_data)):
            if deletions[i] == e_data.name[j]:
                e_data_deletions[i] = np.take(e_data, j, 0)  # extract row to separate matrix
                remove_rows.append(j) # row number for later removal
    e_data = np.delete(e_data, remove_rows, 0) # delete row from e_data containing entry
    print('           ', len(deletions), 'existing elements deleted.')

    # For cases where proposed data was not present in existing data = remove these elements and place in new array
    additions = np.setdiff1d(np.array(p_data.name), np.array(e_data.name))
    remove_rows = []
    p_data_additions = np.recarray((len(additions),1), dtype = data_types) # initialize blank
    for i in range(0,len(additions)):
        for j in range(0,len(p_data)):
            if additions[i] == p_data.name[j]:
                p_data_additions[i] = np.take(p_data, j, 0)  # extract row to separate matrix
                remove_rows.append(j) # row number for later removal
    p_data = np.delete(p_data, remove_rows, 0) # delete row from p_data containing entry
    print('           ', len(additions), 'proposed elements added.')

    # Create array containing elements in BOTH existing and proposed
    e_data = e_data[e_data.name.argsort()] # sort by name
    p_data = p_data[p_data.name.argsort()] # sort by name
    combined_dtypes = [('name', 'U32'), \
                       ('e_voltage', 'float32'), ('e_drop', 'float32'), ('e_miles', 'float32'), ('e_ampsa', 'float32'),\
                       ('e_ampsb', 'float32'), ('e_ampsc', 'float32'), ('e_minlg', 'float32'), ('e_maxfault', 'float32'),\
                       ('p_voltage', 'float32'), ('p_drop', 'float32'), ('p_miles', 'float32'), ('p_ampsa', 'float32'),\
                       ('p_ampsb', 'float32'), ('p_ampsc', 'float32'), ('p_minlg', 'float32'), ('p_maxfault', 'float32')]
    combined_data = np.rec.array([e_data.name, e_data.voltage, e_data.drop, e_data.miles, e_data.ampsa, e_data.ampsb,\
                                  e_data.ampsc, e_data.minlg, e_data.maxfault, p_data.voltage, p_data.drop,\
                                  p_data.miles, p_data.ampsa, p_data.ampsb, p_data.ampsc, p_data.minlg,\
                                  p_data.maxfault], dtype = combined_dtypes)

    # Sloppy creation of deletion row to append to matrix
    deleted_data = np.rec.array([e_data_deletions.name,\
                                 e_data_deletions.voltage, e_data_deletions.drop, e_data_deletions.miles, e_data_deletions.ampsa,\
                                 e_data_deletions.ampsb, e_data_deletions.ampsc, e_data_deletions.minlg, e_data_deletions.maxfault, \
                                 e_data_deletions.maxfault, e_data_deletions.maxfault, e_data_deletions.maxfault, e_data_deletions.maxfault,\
                                 e_data_deletions.maxfault, e_data_deletions.maxfault, e_data_deletions.maxfault, e_data_deletions.maxfault],\
                                 dtype = combined_dtypes)
    deleted_data.p_voltage = None
    deleted_data.p_drop = None
    deleted_data.p_miles = None
    deleted_data.p_ampsa = None
    deleted_data.p_ampsb = None
    deleted_data.p_ampsc = None
    deleted_data.p_minlg = None
    deleted_data.p_maxfault = None

    added_data = np.rec.array([p_data_additions.name, \
                               p_data_additions.maxfault, p_data_additions.maxfault, p_data_additions.maxfault, p_data_additions.maxfault,\
                               p_data_additions.maxfault, p_data_additions.maxfault, p_data_additions.maxfault, p_data_additions.maxfault,\
                               p_data_additions.voltage, p_data_additions.drop, p_data_additions.miles, p_data_additions.ampsa,\
                               p_data_additions.ampsb, p_data_additions.ampsc, p_data_additions.minlg, p_data_additions.maxfault],\
                               dtype=combined_dtypes)
    added_data.e_voltage = None
    added_data.e_drop = None
    added_data.e_miles = None
    added_data.e_ampsa = None
    added_data.e_ampsb = None
    added_data.e_ampsc = None
    added_data.e_minlg = None
    added_data.e_maxfault = None

    combined_data = np.append(combined_data, deleted_data)
    combined_data = np.append(combined_data, added_data)
    combined_data = np.rec.array(combined_data, dtype = combined_dtypes)
    return combined_data

def Finishing(data):

    for i in range(0,len(data)):
        data.e_voltage[i] = round(data.e_voltage[i], 1)
        data.e_drop[i] = round(data.e_drop[i], 1)
        data.e_miles[i] = round(data.e_miles[i], 1)
        data.e_ampsa[i] = round(data.e_ampsa[i], 1)
        data.e_ampsb[i] = round(data.e_ampsb[i], 1)
        data.e_ampsc[i] = round(data.e_ampsc[i], 1)
        data.p_voltage[i] = round(data.p_voltage[i], 1)
        data.p_drop[i] = round(data.p_drop[i], 1)
        data.p_miles[i] = round(data.p_miles[i], 1)
        data.p_ampsa[i] = round(data.p_ampsa[i], 1)
        data.p_ampsb[i] = round(data.p_ampsb[i], 1)
        data.p_ampsc[i] = round(data.p_ampsc[i], 1)

    header_formatting = '{0:^5s}\n\n{1:^5s}'
    header_line1 = ',Existing,,,,,,,,Proposed,,,,,,,,'
    header_line3 = 'Voltage,Acc Drop,Miles,I AØ,I BØ,I CØ,Min(Flt),Max(Flt),'
    output_header = header_formatting.format(header_line1, 'Names,' + header_line3 + header_line3)

    np.savetxt("OUTPUT DATA.csv", data, fmt='%s', delimiter=',', header=output_header)

    return data

main()

