#Import modules
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from tkinter.ttk import Progressbar
import tkinter.font as tkFont
from PIL import ImageTk, Image
import os
import numpy as np

#Import BEM toolkit functions
import metadata
import energyBaseline
import ahuAnomaly
import zoneAnomaly
import endUseDisaggregation
import occupancy
import complaintsAnalytics
import generate_report
    
#Create GUI    
main = tk.Tk() #Create main window
main.title('BEM Toolkit (IN DEVELOPMENT - NOT INDICATIVE OF FINAL)') #Title of main window
main.geometry('500x280') #Define size of main window
main.resizable(0, 0) # fix window

tab_parent = ttk.Notebook(main)

tab0 = ttk.Frame(tab_parent)
tab1 = ttk.Frame(tab_parent)
tab2 = ttk.Frame(tab_parent)
tab3 = ttk.Frame(tab_parent)
tab4 = ttk.Frame(tab_parent)

tab_parent.add(tab0, text='General')
tab_parent.add(tab1, text='Metadata')
tab_parent.add(tab2, text='Faults & Anomalies')
tab_parent.add(tab3, text='Monitor')
tab_parent.add(tab4, text='Report')

tab_parent.pack(expand=1,fill='both')

# Create general info text
S = tk.Scrollbar(tab0)
T = tk.Text(tab0, height=4, width=80)
S.pack(side=tk.RIGHT, fill=tk.Y)
T.pack(side=tk.LEFT, fill=tk.Y)
S.config(command=T.yview)
T.config(yscrollcommand=S.set)
quote = "Hi! This is the Building Energy mangement toolkit, an open-sourced, data-driven set of functions to help interpret metadata labels, identify common hard and soft faults, and monitor building operations. Upon selecting a function from the 'Metadata','Faults', or 'Monitor' tab, you will be prompted to select the required data files (or folder containing data files). Resulting visualizations and KPIs can be viewed using the 'Visuals and KPIs' tab."
T.insert(tk.END, quote)

# Create text for metadata tab
tk.Label(tab1, text = "Select the metadata function to begin the metadata analysis").pack()

#Define function buttons
tk.Button(tab1,text='Metadata',command=lambda *args:metadata.execute_function(),height=5,width=20).place(x=170,y=65)
tk.Button(tab2, text='AHU Anomaly',command=lambda *args:ahuAnomaly.execute_function(),height=5,width=20).place(x=95,y=65)
tk.Button(tab2, text='Zone Anomaly',command=lambda *args:zoneAnomaly.execute_function(),height=5,width=20).place(x=270,y=65)
tk.Button(tab3, text='End-use disaggregation',command=lambda *args:endUseDisaggregation.execute_function(),height=5,width=20).place(x=105,y=30)
tk.Button(tab3, text='Baseline Energy',command=lambda *args:energyBaseline.execute_function(),height=5,width=20).place(x=105,y=120)
tk.Button(tab3, text='Occupancy',command=lambda *args:occupancy.execute_function(),height=5,width=20).place(x=260,y=30)
tk.Button(tab3, text='Complaints analytics',command=lambda *args:complaintsAnalytics.execute_function(),height=5,width=20).place(x=260,y=120)

#Define buttons to show results
tk.Button(tab4, text='AHU Anomaly',command=lambda *args:generate_report.ahuAnomaly(),height=2,width=20).place(x=105,y=30)
tk.Button(tab4, text='Zone Anomaly',command=lambda *args:generate_report.zoneAnomaly(),height=2,width=20).place(x=105,y=75)
tk.Button(tab4, text='End-use Disaggregation',command=lambda *args:generate_report.endUseDisaggregation(),height=2,width=20).place(x=260,y=30)
tk.Button(tab4, text='Baseline Energy',command=lambda *args:generate_report.energyBaseline(),height=2,width=20).place(x=105,y=120)
tk.Button(tab4, text='Occupancy',command=lambda *args:generate_report.occupancy(),height=2,width=20).place(x=260,y=75)
tk.Button(tab4, text='Complaints Analytics',command=lambda *args:generate_report.complaints(),height=2,width=20).place(x=260,y=120)

#Define Help button
def help_box():
    tk.messagebox.showinfo(title='Help',message='Help.')

tk.Button(main, text = "Help", command = help_box).place(x=0,y=255)

#Define Exit button
def exit_application():
    MsgBox = tk.messagebox.askquestion('Exit Application','Done already? :(',icon = 'warning')
    if MsgBox == 'yes':
       main.destroy()

tk.Button(main, text = "Exit", command = exit_application).place(x=470,y=255)

main.mainloop()