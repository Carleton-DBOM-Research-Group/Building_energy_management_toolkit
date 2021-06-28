#Import required libraries
import pandas as pd
import numpy as np
from datetime import datetime 
from geneticalgorithm import geneticalgorithm as ga
from scipy.optimize import  differential_evolution
import matplotlib.pyplot as plt
import math
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
from tkinter import simpledialog
import time

def execute_function():

  #Specify current directory and input/output paths
  path = os.getcwd() #Get current directory
  output_path = path + r'\toolkit\outputs\2-energyBaseline' #Specify output directory for KPIs and visualizations

  tk.messagebox.showinfo(title='Energy Baseline',message='Please select the file (must be in CSV format) containing the energy meter data.')
  energy_file_path = askopenfilename(title='Select energy meter data file (CSV)') #Ask user for energy data file
  energy_file_path = energy_file_path.replace('/','\\') #Replace backward slashes with forward slashes in energy data file path
  if bool(energy_file_path) == False:
    tk.messagebox.showerror(title='Energy Baseline',message='Error! Run will terminate.\n\n(No file containing energy meter data was selected.)')
    print('Run terminated! No energy file selected.')
    return

  tk.messagebox.showinfo(title='Energy Baseline',message='Please select the file (must be in CSV format) containing the weather data.')
  weather_file_path = askopenfilename(title='Select weather file (CSV)') #Ask user for weather data file
  weather_file_path = weather_file_path.replace('/','\\') #Replace backward slashes with forward slashes in energy data input directory
  if bool(weather_file_path) == False:
    tk.messagebox.showerror(title='Energy Baseline',message='Error! Run will terminate.\n\n(No file containing weather data was selected.)')
    print('Run terminated! No weather file selected.')
    return

  #Ask user user inputs (Exterior facade area, number of floors, WWR, and gross floor area)
  exteriorFacadeArea = simpledialog.askinteger("Input exterior facade area","Enter the exterior facade area of the building in square meters. If unknown, enter 0 or select Cancel.", minvalue=0)

  numberOfFloors = simpledialog.askinteger("Input number of floors","Enter the number of floors in the building.", minvalue=1,maxvalue=200)
  if bool(numberOfFloors) == False:
    tk.messagebox.showerror(title='Energy Baseline',message='Run terminated! No number of floors entered.')
    return
  wwr = simpledialog.askfloat("Input window-to-wall ratio","Input the ratio of windows to walls of exterior facade of building (Window-to-wall ratio). Must be between 0.1 and 1.0.", minvalue=0.1, maxvalue=1.0)
  if bool(wwr) == False:
    tk.messagebox.showerror(title='Energy Baseline',message='Run terminated! No window-to-wall ratio entered.')
    return
  floorArea = simpledialog.askinteger("Input floor area","Input gross floor area of building in square meters.",minvalue=100)
  if bool(floorArea) == False:
    tk.messagebox.showerror(title='Energy Baseline',message='Run terminated! No building floor area entered.')
    return
  
  tk.messagebox.showinfo(title='Energy Baseline',message='Baseline energy analysis will commence. This will take a while...')

  start_time = time.time() #Start timer
  #Estimate UA value accoridng to NECB 2017
  #U-value of (wall, window, roof) is (0.25, 1.9, 0.2)

  if (bool(exteriorFacadeArea) == False) or (exteriorFacadeArea == 0):
    exteriorFacadeArea = floorArea * 0.4

  try:
    ua = exteriorFacadeArea*(1-wwr)*0.25 + exteriorFacadeArea*wwr*1.9 + floorArea/numberOfFloors*0.2 #Define UA value without infiltration
    ua = (ua + 0.3*(exteriorFacadeArea + floorArea/numberOfFloors))/1000 #Define UA with infiltration(0.25 L/s-m2; air density 1.2 kg/m3 & air specific heat 1 kJ/kgdegC)
    uVen = 0.6*floorArea/1000 #0.5 L/s-m2 ashrae 62.1 office ventilation rates for default office occupancy rates
  except:
    print('Insufficient information provided - NECB compliant heating energy use rates will not be modeled...')

  #Read energy data files
  print('Reading energy meter data...')
  energy = pd.read_csv(energy_file_path)

  #Read AMY weather data
  print('Reading weather data...')
  weather = pd.read_csv(weather_file_path,usecols=[3],skiprows=18)

  #Define ga functions

  def rmse_heatingChangePoint(x): #Heating model
    # x[0] primary slope workhours
    # x[1] secondary slope afterhours
    # x[2] x-coordinate of change point for workhours
    # x[3] y-coordinate of change point for workhours
    # x[4] x-coordinate of change point for afterhours
    # x[5] y-coordinate of change point for afterhours
    # x[6] start time of day (for weekdays)
    # x[7] stop time of day (for weekdays)
    # x[8] start time of day (for weekends)
    # x[9] stop time of day (for weekends)
    
    sch = ((df.index.hour > x[6]) & (df.index.hour < x[7]) & (df.index.dayofweek >=0 ) & (df.index.dayofweek < 5)) | ((df.index.hour> x[8]) & (df.index.hour < x[9]) & ( (df.index.dayofweek==6) | (df.index.dayofweek == 5)))
    
    yp = (np.logical_and(tOa < x[2], sch == 1)) * ((x[2] - tOa) * x[0] + x[3]) + (np.logical_and(tOa >= x[2], sch == 1)) * (x[3]) + (np.logical_and(tOa < x[4], sch == 0)) * ((x[4] - tOa) * x[1] + x[5]) + (np.logical_and(tOa >= x[4], sch == 0))*(x[5])

    rmse = np.sqrt(((yp - qHtg) ** 2).mean())

    return rmse

  def rmse_coolingChangePoint(x): #Cooling model
    # x[0] primary slope workhours
    # x[1] secondary slope afterhours
    # x(3) x-coordinate of change point for workhours
    # x(4) y-coordinate of change point for workhours
    # x(5) x-coordinate of change point for afterhours
    # x(6) y-coordinate of change point for afterhours
    # x(7) start time of day (for weekdays)
    # x(8) stop time of day (for weekdays)
    # x(9) start time of day (for weekends)
    # x(10) stop time of day (for weekends)
    
    sch = ((df.index.hour > x[6]) & (df.index.hour < x[7]) & (df.index.dayofweek >=0 ) & (df.index.dayofweek < 5)) | ((df.index.hour> x[8]) & (df.index.hour < x[9]) & ( (df.index.dayofweek==6) | (df.index.dayofweek == 5)))

    yp = (np.logical_and(tOa > x[2], sch == 1)) * ((-x[2] + tOa) * x[0] + x[3]) + (np.logical_and(tOa <= x[2], sch == 1))*(x[3]) + (np.logical_and(tOa > x[4], sch == 0)) * ((-x[4] + tOa) * x[1] + x[5]) + (np.logical_and(tOa <= x[4], sch == 0))*(x[5])

    rmse = np.sqrt(((yp - qClg) ** 2).mean())
  
    return rmse

  def rmse_electricityChangePoint(x):#Electricity model
    # x[0] primary slope workhours
    # x[1] secondary slope afterhours
    # x(3) x-coordinate of change point for workhours
    # x(4) y-coordinate of change point for workhours
    # x(5) x-coordinate of change point for afterhours
    # x(6) y-coordinate of change point for afterhours
    # x(7) start time of day (for weekdays)
    # x(8) stop time of day (for weekdays)
    # x(9) start time of day (for weekends)
    # x(10) stop time of day (for weekends)
    
    sch = ((df.index.hour > x[6]) & (df.index.hour < x[7]) & (df.index.dayofweek >=0 ) & (df.index.dayofweek < 5)) | ((df.index.hour> x[8]) & (df.index.hour < x[9]) & ( (df.index.dayofweek==6) | (df.index.dayofweek == 5)))

    yp = (np.logical_and(tOa > x[2], sch == 1)) * ((-x[2] + tOa) * x[0] + x[3]) + (np.logical_and(tOa <= x[2], sch == 1))*(x[3]) + (np.logical_and(tOa > x[4], sch == 0)) * ((-x[4] + tOa) * x[1] + x[5]) + (np.logical_and(tOa <= x[4], sch == 0))*(x[5])

    rmse = np.sqrt(((yp - qElec) ** 2).mean())

    return rmse


  #Extract energy use and outdoor air temps from read files
  qHtg = energy[energy.columns[3]]
  qClg = energy[energy.columns[2]]
  qElec = energy[energy.columns[1]]
  tOa = weather[weather.columns[0]]

  #Create one dataframe to store all relevant data
  df = pd.DataFrame()
  df['heating'] = qHtg
  df['cooling'] = qClg
  df['electricity'] = qElec
  df.index = energy[energy.columns[0]]
  df.index = pd.to_datetime(df.index)
  df['timeOfDay'] = df.index.hour
  df['dayOfWeek'] = df.index.dayofweek

  varbound = np.array([[0, max(qHtg)/10],[0,max(qHtg)/10],[0,20],[0,max(qHtg)],[0,20],[0,max(qHtg)],[0,8],[16,23],[0,12],[12,23]])

  algorithm_param = {'max_num_iteration': 20,\
                    'population_size':5000,\
                    'mutation_probability':0.1,\
                    'elit_ratio': 0.01,\
                    'crossover_probability': 0.7,\
                    'parents_portion': 0.3,\
                    'crossover_type':'uniform',\
                    'max_iteration_without_improv':10}

  model_Htg_GA = ga(function = rmse_heatingChangePoint,
                    dimension = 10, 
                    variable_type = 'real', 
                    variable_boundaries = varbound,
                    algorithm_parameters = algorithm_param,
                    convergence_curve = False)

  print('Estimating heating energy use change points using GA...')
  model_Htg_GA.run() #Run GA
  x = model_Htg_GA.best_variable #Extract estimated changepoints

  sch = ((df.index.hour > x[6]) & (df.index.hour < x[7]) & (df.index.dayofweek >=0 ) & (df.index.dayofweek < 5)) | ((df.index.hour> x[8]) & (df.index.hour < x[9]) & ( (df.index.dayofweek==6) | (df.index.dayofweek == 5)))
  yp = (np.logical_and(tOa < x[2],sch == 1)) * ((x[2] - tOa) * x[0] + x[3]) + (np.logical_and(tOa >= x[2],sch == 1)) * (x[3]) + (np.logical_and(tOa < x[4],sch == 0)) * ((x[4] - tOa) * x[1] + x[5]) + (np.logical_and(tOa >= x[4],sch == 0))*(x[5])

  residuals = qHtg - yp
  timeOfDay_handle = df.index.hour
  mdl_heating_prmtr = x

  a=[]
  b=[]

  for i in range(0,24):
    a.append(residuals[(timeOfDay_handle == i) & ((df.index.dayofweek >= 0) & (df.index.dayofweek < 5)) & (tOa < x[2])].mean())
    b.append(residuals[(timeOfDay_handle == i) & ((df.index.dayofweek >= 0) & (df.index.dayofweek < 5)) & (tOa >= x[2])].mean())

  mdl_heating_residual= pd.DataFrame(a,columns=['residual1'])
  mdl_heating_residual['residual2'] = b

  plt.figure(figsize=(10,5))
  plt.subplot(121)
  plt.scatter(tOa, qHtg, alpha=0.1, c='darkred',label='Measured')
  plt.xlabel(r'Outdoor air temperature '+r'$(^{0}C)$',fontsize = 18)
  plt.ylabel("Heating load (kWh)", fontsize= 18)
  plt.xticks(fontsize=12)
  plt.yticks(fontsize=12)
  plt.xlim(-25,25)
  plt.ylim(bottom=0)

  print('Modeling operating and afterhours heating energy use rates...')
  #Modelled cold operating hours and afterhours
  tOa_handle = np.linspace(-30,25,100)
  ypOperating = (tOa_handle < x[2]) * ((x[2] - tOa_handle) * x[0] + x[3]) + (tOa_handle >= x[2]) * (x[3])
  ypAfterHours = (tOa_handle < x[4]) * ((x[4] - tOa_handle) * x[1] + x[5]) + (tOa_handle >= x[4]) * (x[5])
  plt.plot(tOa_handle,ypOperating, 'r',linewidth=4,label='Modelled operating')
  plt.plot(tOa_handle,ypAfterHours, 'r--',linewidth=4,label ='Modelled afterhours')

  try:
    #Code compliance cold operating hours and afterhours
    ypOperatingCode = (tOa_handle < x[2]) * ((x[2] - tOa_handle) * (ua + uVen) + x[3]) + (tOa_handle >= x[2]) * (x[3])
    ypAfterHoursCode = (tOa_handle < x[4]) * ((x[4] - tOa_handle) * (ua) + x[5]) + (tOa_handle >= x[4]) * (x[5])
    plt.plot(tOa_handle,ypOperatingCode, 'k',linewidth=4,label='NECB operating')
    plt.plot(tOa_handle,ypAfterHoursCode, 'k--',linewidth=4,label='NECB afterhours')
  except:
    print('Insufficent information provided - No NECB compliant models...')

  plt.legend(ncol=1,handlelength=3,fontsize=12)

  print('Modeling predicted heating energy use rates...')
  plt.subplot(122)
  plt.xlim(0,23)
  plt.ylim(0 ,math.ceil(max(qHtg)/100)*100)
  plt.xticks(np.arange(0, 24, step=2), fontsize=12)
  plt.yticks(fontsize=12)
  plt.xlabel('Time of day (h)',fontsize = 18)
  plt.ylabel("Predicted heating load (kWh)", fontsize= 18)
  timeOfDay_handle = list(range(0,24))
  sch_handle =((timeOfDay_handle > x[6]) & (timeOfDay_handle < x[7]))

  for i in [-20,-10,0]:
    tOa_handle = i*(np.ones(len(timeOfDay_handle)))
    yp = (np.logical_and(tOa_handle < x[2],sch_handle == 1)) * ((x[2] - tOa_handle) * x[0] + x[3]) + (np.logical_and(tOa_handle >= x[2],sch_handle == 1))*(x[3]) + (np.logical_and(tOa_handle < x[4],sch_handle == 0)) * ((x[4] - tOa_handle) * x[1] + x[5]) + (np.logical_and(tOa_handle >= x[4],sch_handle == 0))*x[5]
    if i < x[2]:
      yp = np.maximum(yp + mdl_heating_residual['residual1'].values,0)
    else:
      yp = np.maximum(yp + mdl_heating_residual['residual2'].values,0)

    plt.plot(timeOfDay_handle, yp, linewidth=4, markersize=16)
    plt.text(x=12,y=max(yp)+10,s=r'$T_{oa} =$' + str(i) + ' C', fontsize=15)

  plt.tight_layout()
  plt.savefig(output_path + r'\energyBase_heating.png',dpi=600)
  print('Heating energy use analysis completed!')

  varbound = np.array([[0, max(qClg)/10],[0,max(qClg)/10],[0,20],[0,max(qClg)],[0,20],[0,max(qClg)],[0,8],[16,23],[0,12],[12,23]])

  model_Clg_GA = ga(function=rmse_coolingChangePoint,
                    dimension=10, 
                    variable_type='real', 
                    variable_boundaries = varbound,
                    algorithm_parameters=algorithm_param,
                    convergence_curve = False) #Use the same parameters as previous ga

  print('Estimating cooling energy use change points using GA...')
  model_Clg_GA.run() #Run GA for cooling
  x = model_Clg_GA.best_variable #Extract estimated changepoints from GA

  sch = ((df.index.hour > x[6]) & (df.index.hour < x[7]) & (df.index.dayofweek >=0 ) & (df.index.dayofweek < 5)) | ((df.index.hour> x[8]) & (df.index.hour < x[9]) & ( (df.index.dayofweek==6) | (df.index.dayofweek == 5)))
  yp = (np.logical_and(tOa > x[2],sch == 1)) * ((-x[2] + tOa) * x[0] + x[3]) + (np.logical_and(tOa <= x[2],sch == 1)) * (x[3]) + (np.logical_and(tOa > x[4],sch == 0)) * ((-x[4] + tOa) * x[1] + x[5]) + (np.logical_and(tOa <= x[4],sch == 0))*(x[5])

  residuals = qClg - yp
  timeOfDay_handle = df.index.hour
  mdl_cooling_prmtr = x

  a=[]
  b=[]

  for i in range(0,24):
    a.append(residuals[(timeOfDay_handle == i) & ((df.index.dayofweek >= 0) & (df.index.dayofweek < 5)) & (tOa < x[2])].mean())
    b.append(residuals[(timeOfDay_handle == i) & ((df.index.dayofweek >= 0) & (df.index.dayofweek < 5)) & (tOa >= x[2])].mean())

  mdl_cooling_residual= pd.DataFrame(a,columns=['residual1'])
  mdl_cooling_residual['residual2'] = b

  plt.figure(figsize=(10,5))
  plt.subplot(121)
  plt.scatter(tOa, qClg, alpha=0.1,label='Measured')
  plt.xlabel(r'Outdoor air temperature '+r'$(^{0}C)$',fontsize = 18)
  plt.ylabel("Cooling load (kWh)", fontsize= 18)
  plt.xticks(fontsize=12)
  plt.yticks(fontsize=12)
  plt.xlim(-5,35)
  plt.ylim(bottom=0)

  #Modelled hot operating hours and afterhours
  print('Modeling operating and afterhours cooling energy use rates...')
  tOa_handle = np.linspace(-5,36,100)
  ypOperating = (tOa_handle > x[2]) * ((-x[2] + tOa_handle) * x[0] + x[3]) + (tOa_handle <= x[2]) * (x[3])
  ypAfterHours = (tOa_handle > x[4]) * ((-x[4] + tOa_handle) * x[1] + x[5]) + (tOa_handle <= x[4]) * (x[5])
  plt.plot(tOa_handle,ypOperating, 'b',linewidth=4,label='Modelled operating')
  plt.plot(tOa_handle,ypAfterHours, 'b--',linewidth=4,label ='Modelled afterhours')

  #Code compliance hot operating hours and afterhours
  #Due to unaccounted substancial loss of dehumidifying in the summer and
  #expected high levels of expected outdoor air use during economizer,
  #NECB comparison is not included.

  plt.legend(ncol=1,handlelength=3)

  print('Modeling predicted cooling energy use rates...')
  plt.subplot(122)
  plt.xlim(0,23)
  plt.ylim(0 ,math.ceil(max(qClg)/100)*100)
  plt.xticks(np.arange(0,24 ,step=2), fontsize=12)
  plt.yticks(fontsize=12)
  plt.xlabel('Time of day (h)',fontsize = 18)
  plt.ylabel("Predicted cooling load (kWh)", fontsize= 18)
  timeOfDay_handle = list(range(0,24))
  sch_handle =((timeOfDay_handle > x[6]) & (timeOfDay_handle < x[7] ))

  for i in [15,25,35]:
    tOa_handle = i*(np.ones(len(timeOfDay_handle)))
    yp = (np.logical_and(tOa_handle > x[2],sch_handle == 1)) * ((-x[2] + tOa_handle) * x[0] + x[3]) + (np.logical_and(tOa_handle <= x[2],sch_handle == 1))*(x[3]) + (np.logical_and(tOa_handle > x[4],sch_handle == 0)) * ((-x[4] + tOa_handle) * x[1] + x[5]) + (np.logical_and(tOa_handle <= x[4],sch_handle == 0))*x[5]
    if i < x[2]:
      yp = np.maximum(yp + mdl_cooling_residual['residual1'].values,0)
    else:
      yp = np.maximum(yp + mdl_cooling_residual['residual2'].values,0)
    
    plt.plot(timeOfDay_handle, yp, linewidth=4, markersize=16)
    plt.text(x=12, y=max(yp)+10, s=r'$t_{oa} =$' + str(i) + ' C', fontsize=15)

  plt.tight_layout()
  plt.savefig(output_path + r'\energyBase_cooling.png',dpi=600)
  print('Cooling energy use analysis completed!')

  varbound = np.array([[0, max(qElec)/10],[0,max(qElec)/10],[0,20],[0,max(qElec)],[0,20],[0,max(qElec)],[0,8],[16,23],[0,12],[12,23]])

  model_Elec_GA = ga(function=rmse_electricityChangePoint,
                      dimension=10, 
                      variable_type='real', 
                      variable_boundaries = varbound,
                      algorithm_parameters=algorithm_param,
                      convergence_curve = False) #Use the same parameters as previous ga

  print('Estimating electricity use change points using GA...')
  model_Elec_GA.run() #Run GA for electricity
  x = model_Elec_GA.best_variable #Extract changepoints from GA

  sch = ((df.index.hour > x[4]) & (df.index.hour < x[5]) & (df.index.dayofweek >=0 ) & (df.index.dayofweek < 5)) | ((df.index.hour> x[6]) & (df.index.hour < x[7]) & ( (df.index.dayofweek==6) | (df.index.dayofweek == 5)))
  yp = (np.logical_and(tOa >= x[2],sch == 1)) * ((tOa - x[2]) * x[0] + x[3]) + (np.logical_and(tOa >= x[2],sch == 0 ))*((tOa - x[2]) * x[1] + x[3]) + (tOa < x[2])*x[3]

  residuals = qElec - yp
  timeOfDay_handle = df.index.hour
  mdl_electricity_prmtr = x

  a=[]
  b=[]

  for i in range(0,24):
    a.append(residuals[(timeOfDay_handle == i) & ((df.index.dayofweek >= 0) & (df.index.dayofweek < 5)) & (tOa < x[2])].mean())
    b.append(residuals[(timeOfDay_handle == i) & ((df.index.dayofweek >= 0) & (df.index.dayofweek < 5)) & (tOa >= x[2])].mean())

  mdl_electricity_residual= pd.DataFrame(a,columns=['residual1'])
  mdl_electricity_residual['residual2'] = b

  plt.figure(figsize=(10,5))
  plt.subplot(121)
  plt.scatter(tOa, qElec, alpha=0.1, c='gray',label='Measured')
  plt.xlabel(r'Outdoor air temperature '+r'$(^{0}C)$',fontsize = 18)
  plt.ylabel("Electricity load (kWh)", fontsize= 18)
  plt.xticks(fontsize=12)
  plt.yticks(fontsize=12)
  plt.xlim(-5,35)
  plt.ylim(bottom=0)

  #Modelled hot operating hours and afterhours
  print('Modeling operating and afterhours electricity use...')
  tOa_handle = np.linspace(-5,35,100)
  ypOperating = (tOa_handle > x[2]) * ((-x[2] + tOa_handle) * x[0] + x[3]) + (tOa_handle <= x[2]) * (x[3])
  ypAfterHours = (tOa_handle > x[4]) * ((-x[4] + tOa_handle) * x[1] + x[5]) + (tOa_handle <= x[4]) * (x[5])
  plt.plot(tOa_handle,ypOperating, 'k',linewidth=4,label='Modelled operating')
  plt.plot(tOa_handle,ypAfterHours, 'k--',linewidth=4,label ='Modelled afterhours')

  plt.legend(ncol=1,handlelength=3)

  print('Modeling predicted electricity use...')
  plt.subplot(122)
  plt.xlim(0,23)
  plt.ylim(0 ,math.ceil(max(qElec)/100)*100)
  plt.xticks(np.arange(0,24 ,step=2), fontsize=12)
  plt.yticks(fontsize=12)
  plt.xlabel('Time of day (h)',fontsize = 18)
  plt.ylabel("Predicted electricity load (kWh)", fontsize= 18)
  timeOfDay_handle = list(range(0,24))
  sch_handle =((timeOfDay_handle > x[6]) & (timeOfDay_handle < x[7]))

  for i in [-5,15,35]:
    tOa_handle = i*(np.ones(len(timeOfDay_handle)))
    yp = (np.logical_and(tOa_handle >= x[2],sch_handle == 1 )) * ((tOa_handle - x[2]) * x[0] + x[3]) + (np.logical_and(tOa_handle >= x[2],sch_handle == 0 ))*((tOa_handle - x[2]) * x[1] + x[3]) + (tOa_handle < x[2])*x[3]
    if i < x[2]:
      yp = np.maximum(yp + mdl_electricity_residual['residual1'].values,0)
    else:
      yp = np.maximum(yp + mdl_electricity_residual['residual2'].values,0)
    
    plt.plot(timeOfDay_handle, yp, linewidth=4, markersize=16)
    plt.text(x=12, y=max(yp)+10, s=r'$t_{oa} =$' + str(i) + ' C', fontsize=15)

  plt.tight_layout()
  plt.savefig(output_path + r'\energyBase_electricity.png',dpi=600)
  print('Electricity use analysis completed!')

  print('Generating KPIs...')
  kpi_scheduleEffectiveness_heating = 1-(mdl_heating_prmtr[1]/mdl_heating_prmtr[0])
  kpi_scheduleEffectiveness_cooling = 1-(mdl_cooling_prmtr[1]/mdl_cooling_prmtr[0])
  kpi_scheduleEffectiveness_electricity = 1-(mdl_electricity_prmtr[1]/mdl_electricity_prmtr[0])
  x = mdl_heating_prmtr
  sch = ((df.index.hour > x[6]) & (df.index.hour < x[7]) & (df.index.dayofweek >=0 ) & (df.index.dayofweek < 5)) | ((df.index.hour> x[8]) & (df.index.hour < x[9]) & ( (df.index.dayofweek==6) | (df.index.dayofweek == 5)))
  kpi_afterHoursEnergyFraction_heating = 1 - (qHtg[sch]).sum()/qHtg.sum()
      
  x = mdl_cooling_prmtr
  sch = ((df.index.hour > x[6]) & (df.index.hour < x[7]) & (df.index.dayofweek >=0 ) & (df.index.dayofweek < 5)) | ((df.index.hour> x[8]) & (df.index.hour < x[9]) & ( (df.index.dayofweek==6) | (df.index.dayofweek == 5)))

  kpi_afterHoursEnergyFraction_cooling = 1 - sum(qClg[sch])/sum(qClg)
  x = mdl_electricity_prmtr
  sch = ((df.index.hour > x[6]) & (df.index.hour < x[7]) & (df.index.dayofweek >=0 ) & (df.index.dayofweek < 5)) | ((df.index.hour> x[8]) & (df.index.hour < x[9]) & ( (df.index.dayofweek==6) | (df.index.dayofweek == 5)))
  kpi_afterHoursEnergyFraction_electricity = 1 - sum(qElec[sch])/sum(qElec)

  #Output an excel table with KPIs
  print('Formatting KPIs...')
  d = {'Utility': ['Heating', 'Cooling','Electricity'],
      'Schedule Effectivness': [kpi_scheduleEffectiveness_heating, kpi_scheduleEffectiveness_cooling,kpi_scheduleEffectiveness_electricity],
      'After-hours energy use ratio':[kpi_afterHoursEnergyFraction_heating,kpi_afterHoursEnergyFraction_cooling,kpi_afterHoursEnergyFraction_electricity]}
  kpi_df = pd.DataFrame(data=d)

  writer = pd.ExcelWriter(output_path + r'\energyBase_summary.xlsx', engine='xlsxwriter')# pylint: disable=abstract-class-instantiated
  kpi_df.to_excel(writer, sheet_name='KPIs')
  writer.save()

  timer = (time.time() - start_time) #Stop timer

  print('Analysis completed! Time elapsed: ' + str(round(timer,3)) + ' seconds')
  tk.messagebox.showinfo(title='Baseline Energy',message='Run successful!\n\nTime elapsed: ' + str(round(timer)) + ' seconds')

