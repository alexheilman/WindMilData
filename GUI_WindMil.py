import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import os
import os.path
from os import path

# global variables
e_rsl_file = None
e_std_file = None
p_rsl_file = None
p_std_file = None

def FileLocator():
    # mainloop settings
    root = tk.Tk()
    root.title('WindMil Data 1.2')
    root.geometry("700x222")
    root.grid_columnconfigure(0, weight = 1)
    root.grid_columnconfigure(1, weight=10000) # put weight in column 2, to make column 1 as small as possible
    style = ttk.Style(root)
    style.theme_use("clam")

    # string variables to be updated with file string
    string_e_rsl = tk.StringVar()
    string_e_rsl.set('No file selected.')
    string_p_rsl = tk.StringVar()
    string_p_rsl.set('No file selected.')
    string_e_std = tk.StringVar()
    string_e_std.set('No file selected.')
    string_p_std = tk.StringVar()
    string_p_std.set('No file selected.')

    def select_E_RSL():
        global e_rsl_file
        file_string = filedialog.askopenfilenames(
            parent=root,
            initialdir= os.getcwd(),
            initialfile='',
            filetypes=[("RSL", "*.rsl")])
        try:
            e_rsl_file = file_string[0]
            string_e_rsl.set(file_string[0])
        except IndexError:
            return

    def select_E_STD():
        global e_std_file
        file_string = filedialog.askopenfilenames(
            parent=root,
            initialdir= os.getcwd(),
            initialfile='',
            filetypes=[("STD", "*.std")])
        try:
            e_std_file = file_string[0]
            string_e_std.set(file_string[0])
        except IndexError:
            return

    def select_P_RSL():
        global p_rsl_file
        file_string = filedialog.askopenfilenames(
            parent=root,
            initialdir= os.getcwd(),
            initialfile='',
            filetypes=[("RSL", "*.rsl")])
        try:
            p_rsl_file = file_string[0]
            string_p_rsl.set(file_string[0])
        except IndexError:
            return

    def select_P_STD():
        global p_std_file
        file_string = filedialog.askopenfilenames(
            parent=root,
            initialdir= os.getcwd(),
            initialfile='',
            filetypes=[("STD", "*.std")])
        try:
            p_std_file = file_string[0]
            string_p_std.set(file_string[0])
        except IndexError:
            return

    ttk.Label(text="Select the exported RSL and STD WindMil files. If there is no proposed model, select the existing files for both").grid(row=1, columnspan = 2, padx=4, pady=4, sticky='ew')

    ttk.Button(root, text="Existing RSL file", command=select_E_RSL).grid(row=2, column=0, padx=4, pady=4, sticky='ew')
    ttk.Label(textvariable= string_e_rsl).grid(row=2, column=1, padx=4, pady=4, sticky='ew')

    ttk.Button(root, text="Existing STD file", command=select_E_STD).grid(row=3, column=0, padx=4, pady=4, sticky='ew')
    ttk.Label(textvariable=string_e_std).grid(row=3, column=1, padx=4, pady=4, sticky='ew')

    ttk.Button(root, text="Proposed RSL file", command=select_P_RSL).grid(row=4, column=0, padx=4, pady=4, sticky='ew')
    ttk.Label(textvariable= string_p_rsl).grid(row=4, column=1, padx=4, pady=4, sticky='ew')

    ttk.Button(root, text="Proposed STD file", command=select_P_STD).grid(row=5, column=0, padx=4, pady=4, sticky='ew')
    ttk.Label(textvariable=string_p_std).grid(row=5, column=1, padx=4, pady=4, sticky='ew')

    ttk.Button(root, text="Done", command= root.quit).grid(row=6, column=0, padx=4, pady=4, sticky='ew')

    root.mainloop()
    root.withdraw()
    return e_rsl_file, e_std_file, p_rsl_file, p_std_file
