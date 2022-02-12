import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import time

# global variables
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

output_file = None
attribute_file = None

def FileLocator():
    # mainloop settings
    root = tk.Tk()
    root.title('AutoCAD Data 1.2')
    root.geometry("700x145")

    string_output = tk.StringVar(root, value='No file selected.')
    string_attribute = tk.StringVar(root, value='No file selected.')

    # settings window
    '''
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
    '''



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
    '''
    filemenu.add_command(label = "Settings", command=settings)
    '''
    filemenu.add_command(label = "Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu = menubar)


    root.mainloop()
    root.withdraw()

    return output_file, attribute_file

