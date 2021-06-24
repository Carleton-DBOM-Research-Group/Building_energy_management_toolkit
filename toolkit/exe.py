#Import modules
import tkinter as tk
from tkinter import ttk

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
tk.Button(tab3, text='Occupancy',command=lambda *args:which_occ_data(1),height=5,width=20).place(x=260,y=30)
tk.Button(tab3, text='Complaints analytics',command=lambda *args:complaintsAnalytics.execute_function(),height=5,width=20).place(x=260,y=120)

#Define buttons to show results
tk.Button(tab4, text='AHU Anomaly',command=lambda *args:generate_report.ahuAnomaly(),height=2,width=20).place(x=105,y=30)
tk.Button(tab4, text='Zone Anomaly',command=lambda *args:generate_report.zoneAnomaly(),height=2,width=20).place(x=105,y=75)
tk.Button(tab4, text='End-use Disaggregation',command=lambda *args:generate_report.endUseDisaggregation(),height=2,width=20).place(x=260,y=30)
tk.Button(tab4, text='Baseline Energy',command=lambda *args:generate_report.energyBaseline(),height=2,width=20).place(x=105,y=120)
tk.Button(tab4, text='Occupancy',command=lambda *args:which_occ_data(2),height=2,width=20).place(x=260,y=75)
tk.Button(tab4, text='Complaints Analytics',command=lambda *args:generate_report.complaints(),height=2,width=20).place(x=260,y=120)

#Define message window for user to indicate which occupancy data they have
def which_occ_data(x):
    if x == 1:
        window = tk.Toplevel(main) #Create main window
        window.title('Select the type of occupancy data you have.') #Title of main window
        window.geometry('400x150') #Define size of main window
        window.resizable(0, 0) # fix window

        w2 = tk.Label(window, 
              justify=tk.CENTER,
              padx = 10, 
              text='Please select the type of occupancy data you would like to analyze.').pack()

        tk.Button(window,text='Wi-Fi device count',command=lambda *args:occupancy.execute_function(1),height=5,width=20).place(x=40,y=40)
        tk.Button(window,text='Motion-detection',command=lambda *args:occupancy.execute_function(2),height=5,width=20).place(x=210,y=40)
    
    else:
        window = tk.Toplevel(main) #Create main window
        window.title('Select the type of occupancy data you have.') #Title of main window
        window.geometry('500x150') #Define size of main window
        window.resizable(0, 0) # fix window

        w2 = tk.Label(window, 
              justify=tk.CENTER,
              padx = 10, 
              text='Please select the type of occupancy data with which you would like to generate report.').pack()

        tk.Button(window,text='Wi-Fi device count',command=lambda *args:generate_report.occupancy(1),height=5,width=20).place(x=80,y=40)
        tk.Button(window,text='Motion-detection',command=lambda *args:generate_report.occupancy(2),height=5,width=20).place(x=270,y=40)


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