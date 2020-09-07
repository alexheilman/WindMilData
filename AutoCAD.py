import os
import sys
import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import time

output_file = 'null'
attribute_file = 'null'
start_time = 0
data_types = 0

atttxt_block = 'BLOCKNAME'
atttxt_name = 'DEVICE'
atttxt_max = 'MAX'
atttxt_min = 'MIN'
atttxt_i1 = 'LINE1'
atttxt_i2 = 'LINE2'
atttxt_i3 = 'LINE3'
atttxt_volt = 'VOLTS'
atttxt_edrop = 'DROP'
atttxt_pdrop = 'DIFF'
atttxt_miles = 'DIST'
Fault_Currents = "Fault_Currents"
Load_Currents = "Load_Currents"
Voltage_Box = "Voltage_Box"
Mismatch_Val = "mismatch"

def main():

    output_file, attribute_file = FileLocator()

    #temp
    #output_file = 'C:/Users/aheilman/Desktop/Programs/Example 3 - AR28/OUTPUT.csv'
    #attribute_file = 'C:/Users/aheilman/Desktop/Programs/Example 3 - AR28/AR28 - 2020 CWP.txt'

    global start_time
    start_time = time.time()

    if output_file == 'null' or attribute_file == 'null':
        Status("ERROR - One or more files not selected.")
        input("Press Enter to exit.")
        quit()

    else:
        Status("Importing data.")
        output_data = np.loadtxt(output_file, dtype='U25', delimiter=",", comments=None, skiprows=3)  # Read in RSL from CSV copy
        attribute_data = np.loadtxt(attribute_file, dtype='U25', delimiter="\t", comments=None, skiprows=0)  # Read in RSL from CSV copy

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

def FileLocator():
    # mainloop settings
    root = tk.Tk()
    root.title('AutoCAD Data 1.1')
    root.geometry("700x145")

    string_output = tk.StringVar(root, value='No file selected.')
    string_attribute = tk.StringVar(root, value='No file selected.')

    # settings window
    set_window = tk.Tk()
    set_window.title('Settings')
    set_window.geometry("390x410")
    set_window.withdraw()

    header_text = "Attribute .txt file headers. Update if headers have changed."
    lbl_header = tk.Label(set_window, justify='left', text=header_text).grid(columnspan=2, row=1)

    sv_atttxt_block = tk.StringVar(set_window, value='BLOCKNAME')
    lbl_atttxt_block = tk.Label(set_window, width=25, anchor = 'w', text="Header - AutoCAD Block Type").grid(column=0, row=2)
    ent_atttxt_block = tk.Entry(set_window, width=30, textvariable = sv_atttxt_block)
    ent_atttxt_block.grid(column=1, row=2)

    sv_atttxt_name = tk.StringVar(set_window, value='DEVICE')
    lbl_atttxt_name = tk.Label(set_window, width=25, anchor = 'w', text="Header - Element Names").grid(column=0, row=3)
    ent_atttxt_name = tk.Entry(set_window, width=30, textvariable = sv_atttxt_name)
    ent_atttxt_name.grid(column=1, row=3)

    sv_atttxt_max = tk.StringVar(set_window, value='MAX')
    lbl_atttxt_max = tk.Label(set_window, width=25, anchor = 'w', text="Header - Maximum Fault").grid(column=0, row=4)
    ent_atttxt_max = tk.Entry(set_window, width=30, textvariable = sv_atttxt_max)
    ent_atttxt_max.grid(column=1, row=4)

    sv_atttxt_min = tk.StringVar(set_window, value='MIN')
    lbl_atttxt_min = tk.Label(set_window, width=25, anchor = 'w', text="Header - Minimum Fault").grid(column=0, row=5)
    ent_atttxt_min = tk.Entry(set_window, width=30, textvariable = sv_atttxt_min)
    ent_atttxt_min.grid(column=1, row=5)

    sv_atttxt_i1 = tk.StringVar(set_window, value='LINE1')
    lbl_atttxt_i1 = tk.Label(set_window, width=25, anchor = 'w', text="Header - Top Phase Current").grid(column=0, row=6)
    ent_atttxt_i1 = tk.Entry(set_window, width=30, textvariable = sv_atttxt_i1)
    ent_atttxt_i1.grid(column=1, row=6)

    sv_atttxt_i2 = tk.StringVar(set_window, value='LINE2')
    lbl_atttxt_i2 = tk.Label(set_window, width=25, anchor = 'w', text="Header - Middle Phase Current").grid(column=0, row=7)
    ent_atttxt_i2 = tk.Entry(set_window, width=30, textvariable = sv_atttxt_i2)
    ent_atttxt_i2.grid(column=1, row=7)

    sv_atttxt_i3 = tk.StringVar(set_window, value='LINE3')
    lbl_atttxt_i3 = tk.Label(set_window, width=25, anchor = 'w', text="Header - Bottom Phase Current").grid(column=0, row=8)
    ent_atttxt_i3 = tk.Entry(set_window, width=30, textvariable = sv_atttxt_i3)
    ent_atttxt_i3.grid(column=1, row=8)

    sv_atttxt_volt = tk.StringVar(set_window, value='VOLTS')
    lbl_atttxt_volt = tk.Label(set_window, width=25, anchor = 'w', text="Header - Voltage").grid(column=0, row=9)
    ent_atttxt_volt = tk.Entry(set_window, width=30, textvariable = sv_atttxt_volt)
    ent_atttxt_volt.grid(column=1, row=9)

    sv_atttxt_edrop = tk.StringVar(set_window, value='DROP')
    lbl_atttxt_edrop = tk.Label(set_window, width=25, anchor = 'w', text="Header - Existing Voltage Drop").grid(column=0, row=10)
    ent_atttxt_edrop = tk.Entry(set_window, width=30, textvariable = sv_atttxt_edrop)
    ent_atttxt_edrop.grid(column=1, row=10)

    sv_atttxt_pdrop = tk.StringVar(set_window, value='DIFF')
    lbl_atttxt_pdrop = tk.Label(set_window, width=25, anchor = 'w', text="Header - Proposed Voltage Drop").grid(column=0, row=11)
    ent_atttxt_pdrop = tk.Entry(set_window, width=30, textvariable = sv_atttxt_pdrop)
    ent_atttxt_pdrop.grid(column=1, row=11)

    sv_atttxt_miles = tk.StringVar(set_window, value='DIST')
    lbl_atttxt_miles = tk.Label(set_window, width=25, anchor = 'w', text="Header - Miles From Substation").grid(column=0, row=12)
    ent_atttxt_miles = tk.Entry(set_window, width=30, textvariable = sv_atttxt_miles)
    ent_atttxt_miles.grid(column=1, row=12)

    lbl_blank = tk.Label(set_window, justify='left', text="").grid(columnspan=2, row=13)
    second_text = "AutoCAD attribute block names. Update if names have changed."
    lbl_second = tk.Label(set_window, justify='left', text=second_text).grid(columnspan=2, row=14)

    sv_Fault_Currents = tk.StringVar(set_window, value="Fault_Currents")
    lbl_Fault_Currents = tk.Label(set_window, width=25, anchor = 'w', text="Block Name - Fault Current").grid(column=0, row=15)
    ent_Fault_Currents = tk.Entry(set_window, width=30, textvariable = sv_Fault_Currents)
    ent_Fault_Currents.grid(column=1, row=15)

    sv_Load_Currents = tk.StringVar(set_window, value="Load_Currents")
    lbl_Load_Currents = tk.Label(set_window, width=25, anchor = 'w', text="Block Name - Phase Current").grid(column=0, row=16)
    ent_Load_Currents = tk.Entry(set_window, width=30, textvariable = sv_Load_Currents)
    ent_Load_Currents.grid(column=1, row=16)

    sv_Voltage_Box = tk.StringVar(set_window, value="Voltage_Box")
    lbl_Voltage_Box = tk.Label(set_window, width=25, anchor = 'w', text="Block Name - Voltage Box").grid(column=0, row=17)
    ent_Voltage_Box = tk.Entry(set_window, width=30, textvariable = sv_Voltage_Box)
    ent_Voltage_Box.grid(column=1, row=17)

    sv_Mismatch_Val = tk.StringVar(set_window, value="mismatch")
    lbl_Mismatch_Val = tk.Label(set_window, width=25, anchor = 'w', text="Value If Mismatched").grid(column=0, row=18)
    ent_Mismatch_Val = tk.Entry(set_window, width=30, textvariable = sv_Mismatch_Val)
    ent_Mismatch_Val.grid(column=1, row=18)

    def set_done():
        set_window.withdraw()
        global atttxt_block
        global atttxt_name
        global atttxt_max
        global atttxt_min
        global atttxt_i1
        global atttxt_i2
        global atttxt_i3
        global atttxt_volt
        global atttxt_edrop
        global atttxt_pdrop
        global atttxt_miles
        global Fault_Currents
        global Load_Currents
        global Voltage_Box
        global Mismatch_Val
        atttxt_block = ent_atttxt_block.get()
        atttxt_name = ent_atttxt_name.get()
        atttxt_max = ent_atttxt_max.get()
        atttxt_min = ent_atttxt_min.get()
        atttxt_i1 = ent_atttxt_i1.get()
        atttxt_i2 = ent_atttxt_i2.get()
        atttxt_i3 = ent_atttxt_i3.get()
        atttxt_volt = ent_atttxt_volt.get()
        atttxt_edrop = ent_atttxt_edrop.get()
        atttxt_pdrop = ent_atttxt_pdrop.get()
        atttxt_miles = ent_atttxt_miles.get()
        Fault_Currents = ent_Fault_Currents.get()
        Load_Currents = ent_Load_Currents.get()
        Voltage_Box = ent_Voltage_Box.get()
        Mismatch_Val = ent_Mismatch_Val.get()



    bt_set_done = tk.Button(set_window, text="Done", justify = 'left', command=set_done).grid(column=0, row=19)



    # button functions - pick file path and display on GUI
    def select_output():
        global output_file
        file_string = filedialog.askopenfilenames(
            parent=root,
            initialdir= os.getcwd(),
            initialfile='',
            filetypes=[("CSV", "*.csv")])
        try:
            output_file = file_string[0]
            string_output.set(file_string[0])
        except IndexError:
            return

    def select_attribute():
        global attribute_file
        file_string = filedialog.askopenfilenames(
            parent=root,
            initialdir= os.getcwd(),
            initialfile='',
            filetypes=[("TXT", "*.txt")])
        try:
            attribute_file = file_string[0]
            string_attribute.set(file_string[0])
        except IndexError:
            return

    def settings():
        set_window.update()
        set_window.deiconify()

    # main window buttons and labels
    lbl_description = tk.Label(root, text="Select the OUTPUT DATA.csv from WindMil Data program and attribute text file exported from AutoCAD.")
    lbl_description.place(x=10, y=5)
    btn_output = tk.Button(root, text="Output Data", command=select_output, height=1, width=12).place(x=10, y=35)
    lbl_output = tk.Label(root, textvariable= string_output).place(x=110, y=37)
    btn_attribute = tk.Button(root, text="Attribute File", command=select_attribute, height=1, width=12).place(x=10, y=70)
    lbl_attribute = tk.Label(root, textvariable= string_attribute).place(x=110, y=70)
    btn_done = tk.Button(root, text="Run", command=root.quit, height=1, width=12).place(x=10, y=105)

    # main window menu bar
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label = "Settings", command=settings)
    filemenu.add_command(label = "Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu = menubar)


    root.mainloop()
    root.withdraw()

    return output_file, attribute_file

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


main()
