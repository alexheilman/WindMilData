import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import time


summer_file = None
winter_file = None

def FileLocator():
    # mainloop settings
    root = tk.Tk()
    root.title('Model Stitch 1.2')
    root.geometry("700x185")

    string_summer = tk.StringVar(root, value='No file selected.')
    string_winter = tk.StringVar(root, value='No file selected.')

    
    # button functions - pick file path and display on GUI
    def select_summer():
        global summer_file
        file_string = filedialog.askopenfilenames(
            parent=root,
            initialdir= os.getcwd(),
            initialfile='',
            filetypes=[("CSV", "*.csv")])
        try:
            summer_file = file_string[0]
            string_summer.set(file_string[0])
        except IndexError:
            return

    def select_winter():
        global winter_file
        file_string = filedialog.askopenfilenames(
            parent=root,
            initialdir= os.getcwd(),
            initialfile='',
            filetypes=[("CSV", "*.csv")])
        try:
            winter_file = file_string[0]
            string_winter.set(file_string[0])
        except IndexError:
            return

    def settings():
        set_window.update()
        set_window.deiconify()

    # main window buttons and labels
    lbl_1 = tk.Label(root, text="Select the summer and winter OUTPUT DATA.csv exported from the WindMil Data 1.2 program.")
    lbl_1.place(x=10, y=5)

    lbl_2 = tk.Label(root, text="Prefix 'S_' required for element names of all summer peaking substations. Example: S_Summer Sub")
    lbl_2.place(x=10, y=25)

    lbl_3 = tk.Label(root, text="Prefix 'W_' required for element names of all winter peaking substations.   Example: W_Winter Sub")
    lbl_3.place(x=10, y=45)

    btn_summer = tk.Button(root, text="Summer OUTPUT DATA.csv", command=select_summer, height=1, width=22).place(x=10, y=75)
    lbl_summer = tk.Label(root, textvariable= string_summer).place(x=180, y=77)

    btn_winter = tk.Button(root, text="Winter OUTPUT DATA.csv", command=select_winter, height=1, width=22).place(x=10, y=110)
    lbl_winter = tk.Label(root, textvariable= string_winter).place(x=180, y=112)

    btn_done = tk.Button(root, text="Run", command=root.quit, height=1, width=12).place(x=10, y=145)

    # main window menu bar
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)

    filemenu.add_command(label = "Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu = menubar)


    root.mainloop()
    root.withdraw()

    return summer_file, winter_file
