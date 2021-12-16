#Import required libraries
import os
import pandas as pd
import numpy as np
from geneticalgorithm import geneticalgorithm as ga
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math

def execute_function(input_path, output_path):

  try:
    #Open text file containing variables for NECB baseline htg model
    file = open(os.path.join(input_path,'necb_parameters.txt'))
    content = file.readlines()
    numberOfFloors = int(content[0])
    wwr = float(content[1])
    floorArea = float(content[2])

    try:
      exteriorFacadeArea = float(content[3])
    except:
      exteriorFacadeArea = floorArea * 0.4
    
    file.close()

    ua = exteriorFacadeArea*(1-wwr)*0.25 + exteriorFacadeArea*wwr*1.9 + floorArea/numberOfFloors*0.2 #Define UA value without infiltration
    ua = (ua + 0.3*(exteriorFacadeArea + floorArea/numberOfFloors))/1000 #Define UA with infiltration(0.25 L/s-m2; air density 1.2 kg/m3 & air specific heat 1 kJ/kgdegC)
    uVen = 0.6*floorArea/1000 #0.5 L/s-m2 ashrae 62.1 office ventilation rates for default office occupancy rates
  
  except:
    print('Insufficient information provided - NECB compliant heating energy use rates will not be modeled...')

  #Read energy data file
  print('Reading energy meter data...')
  energy_files = os.listdir(os.path.join(input_path,'energy'))
  energy = pd.read_csv(os.path.join(input_path, 'energy',energy_files[0]))

  #Read AMY weather data
  print('Reading weather data...')
  weather_files = os.listdir(os.path.join(input_path,'weather'))
  weather = pd.read_csv(os.path.join(input_path, 'weather',weather_files[0]),usecols=[1],skiprows=1,encoding='unicode escape')

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
    
    sch = ((htg_df.index.hour > x[6]) & (htg_df.index.hour < x[7]) & (htg_df.index.dayofweek >=0 ) & (htg_df.index.dayofweek < 5)) | ((htg_df.index.hour> x[8]) & (htg_df.index.hour < x[9]) & ( (htg_df.index.dayofweek==6) | (htg_df.index.dayofweek == 5)))
    
    yp = (np.logical_and(htg_df['tOa'] < x[2], sch == 1)) * ((x[2] - htg_df['tOa']) * x[0] + x[3]) + (np.logical_and(htg_df['tOa'] >= x[2], sch == 1)) * (x[3]) + (np.logical_and(htg_df['tOa'] < x[4], sch == 0)) * ((x[4] - htg_df['tOa']) * x[1] + x[5]) + (np.logical_and(htg_df['tOa'] >= x[4], sch == 0))*(x[5])

    rmse = np.sqrt(((yp - htg_df['heating']) ** 2).mean())

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
    
    sch = ((clg_df.index.hour > x[6]) & (clg_df.index.hour < x[7]) & (clg_df.index.dayofweek >=0 ) & (clg_df.index.dayofweek < 5)) | ((clg_df.index.hour> x[8]) & (clg_df.index.hour < x[9]) & ( (clg_df.index.dayofweek==6) | (clg_df.index.dayofweek == 5)))

    yp = (np.logical_and(clg_df['tOa'] > x[2], sch == 1)) * ((-x[2] + clg_df['tOa']) * x[0] + x[3]) + (np.logical_and(clg_df['tOa'] <= x[2], sch == 1))*(x[3]) + (np.logical_and(clg_df['tOa'] > x[4], sch == 0)) * ((-x[4] + clg_df['tOa']) * x[1] + x[5]) + (np.logical_and(clg_df['tOa'] <= x[4], sch == 0))*(x[5])

    rmse = np.sqrt(((yp - clg_df['cooling']) ** 2).mean())
  
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
    
    sch = ((elec_df.index.hour > x[6]) & (elec_df.index.hour < x[7]) & (elec_df.index.dayofweek >=0 ) & (elec_df.index.dayofweek < 5)) | ((elec_df.index.hour> x[8]) & (elec_df.index.hour < x[9]) & ( (elec_df.index.dayofweek==6) | (elec_df.index.dayofweek == 5)))

    yp = (np.logical_and(elec_df['tOa'] > x[2], sch == 1)) * ((-x[2] + elec_df['tOa']) * x[0] + x[3]) + (np.logical_and(elec_df['tOa'] <= x[2], sch == 1))*(x[3]) + (np.logical_and(elec_df['tOa'] > x[4], sch == 0)) * ((-x[4] + elec_df['tOa']) * x[1] + x[5]) + (np.logical_and(elec_df['tOa'] <= x[4], sch == 0))*(x[5])

    rmse = np.sqrt(((yp - elec_df['electricity']) ** 2).mean())

    return rmse

  #Create one dataframe to store all relevant data
  htg_df = pd.DataFrame()
  htg_df['heating'] = energy[energy.columns[1]]
  htg_df['tOa'] = weather[weather.columns[0]]
  htg_df.index = energy[energy.columns[0]]
  htg_df.index = pd.to_datetime(htg_df.index)
  htg_df['timeOfDay'] = htg_df.index.hour
  htg_df['dayOfWeek'] = htg_df.index.dayofweek
  htg_df = htg_df.dropna()

  clg_df = pd.DataFrame()
  clg_df['cooling'] = energy[energy.columns[2]]
  clg_df['tOa'] = weather[weather.columns[0]]
  clg_df.index = energy[energy.columns[0]]
  clg_df.index = pd.to_datetime(clg_df.index)
  clg_df['timeOfDay'] = clg_df.index.hour
  clg_df['dayOfWeek'] = clg_df.index.dayofweek
  clg_df = clg_df.dropna()

  if os.path.isfile(os.path.join(input_path, 'elec_true')):
    print('Electricity use comparison enabled!')
    try:
      elec_df = pd.DataFrame()
      elec_df['electricity'] = energy[energy.columns[3]]
      elec_df['tOa'] = weather[weather.columns[0]]
      elec_df.index = energy[energy.columns[0]]
      elec_df.index = pd.to_datetime(elec_df.index)
      elec_df['timeOfDay'] = elec_df.index.hour
      elec_df['dayOfWeek'] = elec_df.index.dayofweek
      elec_df = elec_df.dropna()
      is_elec_clg = True
    except:
      print('Cannot read electricity data. Electricity use comparison will be disabled.')
      is_elec_clg = False
  else:
    print('Electricity use comparison disabled!')
    is_elec_clg = False
  
  # extract start and end time from htg_df
  f = open(os.path.join(output_path, "period.txt"),"w+")
  f.write(str(min(htg_df.index)) + " to " + str(max(htg_df.index)))
  f.close()

  varbound = np.array([[0, max(htg_df['heating'])/10],[0,max(htg_df['heating'])/10],[0,20],[0,max(htg_df['heating'])],[0,20],[0,max(htg_df['heating'])],[0,8],[16,23],[0,12],[12,23]])

  algorithm_param = {'max_num_iteration': 10,\
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

  print('Estimating heating energy use change points using GA...', flush=True)
  model_Htg_GA.run() #Run GA
  x = model_Htg_GA.best_variable #Extract estimated changepoints

  sch = ((htg_df.index.hour > x[6]) & (htg_df.index.hour < x[7]) & (htg_df.index.dayofweek >=0 ) & (htg_df.index.dayofweek < 5)) | ((htg_df.index.hour> x[8]) & (htg_df.index.hour < x[9]) & ( (htg_df.index.dayofweek==6) | (htg_df.index.dayofweek == 5)))
  yp = (np.logical_and(htg_df['tOa'] < x[2],sch == 1)) * ((x[2] - htg_df['tOa']) * x[0] + x[3]) + (np.logical_and(htg_df['tOa'] >= x[2],sch == 1)) * (x[3]) + (np.logical_and(htg_df['tOa'] < x[4],sch == 0)) * ((x[4] - htg_df['tOa']) * x[1] + x[5]) + (np.logical_and(htg_df['tOa'] >= x[4],sch == 0))*(x[5])

  residuals = htg_df['heating'] - yp
  timeOfDay_handle = htg_df.index.hour
  mdl_heating_prmtr = x

  a=[]
  b=[]

  for i in range(0,24):
    a.append(residuals[(timeOfDay_handle == i) & ((htg_df.index.dayofweek >= 0) & (htg_df.index.dayofweek < 5)) & (htg_df['tOa'] < x[2])].mean())
    b.append(residuals[(timeOfDay_handle == i) & ((htg_df.index.dayofweek >= 0) & (htg_df.index.dayofweek < 5)) & (htg_df['tOa'] >= x[2])].mean())

  mdl_heating_residual= pd.DataFrame(a,columns=['residual1'])
  mdl_heating_residual['residual2'] = b

  # This analysis is duplicated intentionally - once to determine the ylim of both plots, once to plot predicted loads
  timeOfDay_handle = list(range(0,24))
  sch_handle =((timeOfDay_handle > x[6]) & (timeOfDay_handle < x[7]))
  max_yp = [0,0]
  for i in [-20,-10,0]:
    tOa_handle = i*(np.ones(len(timeOfDay_handle)))
    yp = (np.logical_and(tOa_handle < x[2],sch_handle == 1)) * ((x[2] - tOa_handle) * x[0] + x[3]) + (np.logical_and(tOa_handle >= x[2],sch_handle == 1))*(x[3]) + (np.logical_and(tOa_handle < x[4],sch_handle == 0)) * ((x[4] - tOa_handle) * x[1] + x[5]) + (np.logical_and(tOa_handle >= x[4],sch_handle == 0))*x[5]
    if i < x[2]:
      yp = np.maximum(yp + mdl_heating_residual['residual1'].values,0)
    else:
      yp = np.maximum(yp + mdl_heating_residual['residual2'].values,0)
    if max(yp)>max(max_yp):
      max_yp = yp

  plt.figure(figsize=(10,5))
  plt.subplot(121)
  plt.scatter(htg_df['tOa'], htg_df['heating'], alpha=0.1, c='darkred',label='Measured')
  plt.xlabel(r'Outdoor air temperature '+r'$(^{0}C)$',fontsize = 18)
  plt.ylabel("Heating load (kWh)", fontsize= 18)
  plt.xticks(fontsize=12)
  plt.yticks(fontsize=12)
  plt.xlim(-25,25)
  plt.ylim(0 ,max(math.ceil(max(htg_df['heating'])/100)*100,math.ceil(max(max_yp)/100)*100))

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
    print('Insufficent information provided - No NECB compliant model will be generated...')

  plt.legend(ncol=1,handlelength=3,fontsize=12)

  print('Modeling predicted heating energy use rates...')
  plt.subplot(122)
  plt.xlim(0,23)
  plt.ylim(0 ,max(math.ceil(max(htg_df['heating'])/100)*100,math.ceil(max(max_yp)/100)*100))
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
  plt.savefig(os.path.join(output_path,'energyBase_heating.png'),dpi=600)
  print('Heating energy use analysis completed!', flush=True)

  varbound = np.array([[0, max(clg_df['cooling'])/10],[0,max(clg_df['cooling'])/10],[0,20],[0,max(clg_df['cooling'])],[0,20],[0,max(clg_df['cooling'])],[0,8],[16,23],[0,12],[12,23]])

  model_Clg_GA = ga(function=rmse_coolingChangePoint,
                    dimension=10, 
                    variable_type='real', 
                    variable_boundaries = varbound,
                    algorithm_parameters=algorithm_param,
                    convergence_curve = False) #Use the same parameters as previous ga

  print('Estimating cooling energy use change points using GA...', flush=True)
  model_Clg_GA.run() #Run GA for cooling
  x = model_Clg_GA.best_variable #Extract estimated changepoints from GA

  sch = ((clg_df.index.hour > x[6]) & (clg_df.index.hour < x[7]) & (clg_df.index.dayofweek >=0 ) & (clg_df.index.dayofweek < 5)) | ((clg_df.index.hour> x[8]) & (clg_df.index.hour < x[9]) & ( (clg_df.index.dayofweek==6) | (clg_df.index.dayofweek == 5)))
  yp = (np.logical_and(clg_df['tOa'] > x[2],sch == 1)) * ((-x[2] + clg_df['tOa']) * x[0] + x[3]) + (np.logical_and(clg_df['tOa'] <= x[2],sch == 1)) * (x[3]) + (np.logical_and(clg_df['tOa'] > x[4],sch == 0)) * ((-x[4] + clg_df['tOa']) * x[1] + x[5]) + (np.logical_and(clg_df['tOa'] <= x[4],sch == 0))*(x[5])

  residuals = clg_df['cooling'] - yp
  timeOfDay_handle = clg_df.index.hour
  mdl_cooling_prmtr = x

  a=[]
  b=[]

  for i in range(0,24):
    a.append(residuals[(timeOfDay_handle == i) & ((clg_df.index.dayofweek >= 0) & (clg_df.index.dayofweek < 5)) & (clg_df['tOa'] < x[2])].mean())
    b.append(residuals[(timeOfDay_handle == i) & ((clg_df.index.dayofweek >= 0) & (clg_df.index.dayofweek < 5)) & (clg_df['tOa'] >= x[2])].mean())

  mdl_cooling_residual= pd.DataFrame(a,columns=['residual1'])
  mdl_cooling_residual['residual2'] = b

  # This analysis is duplicated intentionally - once to determine the ylim of both plots, once to plot predicted loads
  timeOfDay_handle = list(range(0,24))
  sch_handle =((timeOfDay_handle > x[6]) & (timeOfDay_handle < x[7] ))
  max_yp = [0,0]
  for i in [15,25,35]:
    tOa_handle = i*(np.ones(len(timeOfDay_handle)))
    yp = (np.logical_and(tOa_handle > x[2],sch_handle == 1)) * ((-x[2] + tOa_handle) * x[0] + x[3]) + (np.logical_and(tOa_handle <= x[2],sch_handle == 1))*(x[3]) + (np.logical_and(tOa_handle > x[4],sch_handle == 0)) * ((-x[4] + tOa_handle) * x[1] + x[5]) + (np.logical_and(tOa_handle <= x[4],sch_handle == 0))*x[5]
    if i < x[2]:
      yp = np.maximum(yp + mdl_cooling_residual['residual1'].values,0)
    else:
      yp = np.maximum(yp + mdl_cooling_residual['residual2'].values,0)
    if max(yp)>max(max_yp):
      max_yp = yp

  plt.figure(figsize=(10,5))
  plt.subplot(121)
  plt.scatter(clg_df['tOa'], clg_df['cooling'], alpha=0.1,label='Measured')
  plt.xlabel(r'Outdoor air temperature '+r'$(^{0}C)$',fontsize = 18)
  plt.ylabel("Cooling load (kWh)", fontsize= 18)
  plt.xticks(fontsize=12)
  plt.yticks(fontsize=12)
  plt.xlim(-5,35)
  plt.ylim(0 ,max(math.ceil(max(clg_df['cooling'])/100)*100,math.ceil(max(max_yp)/100)*100))

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
  plt.ylim(0 ,max(math.ceil(max(clg_df['cooling'])/100)*100,math.ceil(max(max_yp)/100)*100))
  plt.xticks(np.arange(0,24 ,step=2), fontsize=12)
  plt.yticks(fontsize=12)
  plt.xlabel('Time of day (h)',fontsize = 18)
  plt.ylabel("Predicted cooling load (kWh)", fontsize= 18)
  timeOfDay_handle = list(range(0,24))
  sch_handle =((timeOfDay_handle > x[6]) & (timeOfDay_handle < x[7]))

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
  plt.savefig(os.path.join(output_path,'energyBase_cooling.png'),dpi=600)
  print('Cooling energy use analysis completed!',flush=True)

  if is_elec_clg:
    varbound = np.array([[0, max(elec_df['electricity'])/10],[0,max(elec_df['electricity'])/10],[0,20],[0,max(elec_df['electricity'])],[0,20],[0,max(elec_df['electricity'])],[0,8],[16,23],[0,12],[12,23]])

    model_Elec_GA = ga(function=rmse_electricityChangePoint,
                        dimension=10, 
                        variable_type='real', 
                        variable_boundaries = varbound,
                        algorithm_parameters=algorithm_param,
                        convergence_curve = False) #Use the same parameters as previous ga

    print('Estimating electricity use change points using GA...', flush=True)
    model_Elec_GA.run() #Run GA for electricity
    x = model_Elec_GA.best_variable #Extract changepoints from GA

    sch = ((elec_df.index.hour > x[4]) & (elec_df.index.hour < x[5]) & (elec_df.index.dayofweek >=0 ) & (elec_df.index.dayofweek < 5)) | ((elec_df.index.hour> x[6]) & (elec_df.index.hour < x[7]) & ( (elec_df.index.dayofweek==6) | (elec_df.index.dayofweek == 5)))
    yp = (np.logical_and(elec_df['tOa'] >= x[2],sch == 1)) * ((elec_df['tOa'] - x[2]) * x[0] + x[3]) + (np.logical_and(elec_df['tOa'] >= x[2],sch == 0 ))*((elec_df['tOa'] - x[2]) * x[1] + x[3]) + (elec_df['tOa'] < x[2])*x[3]

    residuals = elec_df['electricity'] - yp
    timeOfDay_handle = elec_df.index.hour
    mdl_electricity_prmtr = x

    a=[]
    b=[]

    for i in range(0,24):
      a.append(residuals[(timeOfDay_handle == i) & ((elec_df.index.dayofweek >= 0) & (elec_df.index.dayofweek < 5)) & (elec_df['tOa'] < x[2])].mean())
      b.append(residuals[(timeOfDay_handle == i) & ((elec_df.index.dayofweek >= 0) & (elec_df.index.dayofweek < 5)) & (elec_df['tOa'] >= x[2])].mean())

    mdl_electricity_residual= pd.DataFrame(a,columns=['residual1'])
    mdl_electricity_residual['residual2'] = b

    # This analysis is duplicated intentionally - once to determine the ylim of both plots, once to plot predicted loads
    timeOfDay_handle = list(range(0,24))
    sch_handle =((timeOfDay_handle > x[6]) & (timeOfDay_handle < x[7]))
    max_yp = [0,0]
    for i in [-5,15,35]:
      tOa_handle = i*(np.ones(len(timeOfDay_handle)))
      yp = (np.logical_and(tOa_handle >= x[2],sch_handle == 1 )) * ((tOa_handle - x[2]) * x[0] + x[3]) + (np.logical_and(tOa_handle >= x[2],sch_handle == 0 ))*((tOa_handle - x[2]) * x[1] + x[3]) + (tOa_handle < x[2])*x[3]
      if i < x[2]:
        yp = np.maximum(yp + mdl_electricity_residual['residual1'].values,0)
      else:
        yp = np.maximum(yp + mdl_electricity_residual['residual2'].values,0)
      if max(yp)>max(max_yp):
        max_yp = yp

    plt.figure(figsize=(10,5))
    plt.subplot(121)
    plt.scatter(elec_df['tOa'], elec_df['electricity'], alpha=0.1, c='gray',label='Measured')
    plt.xlabel(r'Outdoor air temperature '+r'$(^{0}C)$',fontsize = 18)
    plt.ylabel("Electricity load (kWh)", fontsize= 18)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlim(-5,35)
    plt.ylim(0 ,max(math.ceil(max(elec_df['electricity'])/100)*100,math.ceil(max(max_yp)/100)*100))

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
    plt.ylim(0 ,max(math.ceil(max(elec_df['electricity'])/100)*100,math.ceil(max(max_yp)/100)*100))
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
    plt.savefig(os.path.join(output_path,'energyBase_electricity.png'),dpi=600)
    print('Electricity use analysis completed!', flush=True)

  print('Generating KPIs...')
  kpi_scheduleEffectiveness_heating = 1-(mdl_heating_prmtr[1]/mdl_heating_prmtr[0])
  kpi_scheduleEffectiveness_cooling = 1-(mdl_cooling_prmtr[1]/mdl_cooling_prmtr[0])
  x = mdl_heating_prmtr
  sch = ((htg_df.index.hour > x[6]) & (htg_df.index.hour < x[7]) & (htg_df.index.dayofweek >=0 ) & (htg_df.index.dayofweek < 5)) | ((htg_df.index.hour> x[8]) & (htg_df.index.hour < x[9]) & ( (htg_df.index.dayofweek==6) | (htg_df.index.dayofweek == 5)))
  kpi_afterHoursEnergyFraction_heating = 1 - (htg_df['heating'][sch]).sum()/htg_df['heating'].sum()
      
  x = mdl_cooling_prmtr
  sch = ((clg_df.index.hour > x[6]) & (clg_df.index.hour < x[7]) & (clg_df.index.dayofweek >=0 ) & (clg_df.index.dayofweek < 5)) | ((clg_df.index.hour> x[8]) & (clg_df.index.hour < x[9]) & ( (clg_df.index.dayofweek==6) | (clg_df.index.dayofweek == 5)))

  kpi_afterHoursEnergyFraction_cooling = 1 - sum(clg_df['cooling'][sch])/sum(clg_df['cooling'])

  if is_elec_clg:
    kpi_scheduleEffectiveness_electricity = 1-(mdl_electricity_prmtr[1]/mdl_electricity_prmtr[0])
    x = mdl_electricity_prmtr
    sch = ((elec_df.index.hour > x[6]) & (elec_df.index.hour < x[7]) & (elec_df.index.dayofweek >=0 ) & (elec_df.index.dayofweek < 5)) | ((elec_df.index.hour> x[8]) & (elec_df.index.hour < x[9]) & ( (elec_df.index.dayofweek==6) | (elec_df.index.dayofweek == 5)))
    kpi_afterHoursEnergyFraction_electricity = 1 - sum(elec_df['electricity'][sch])/sum(elec_df['electricity'])

  #Output an excel table with KPIs
  print('Formatting KPIs...')

  try:
    d = {'Utility': ['Heating', 'Cooling','Electricity'],
        'Schedule Effectiveness': [kpi_scheduleEffectiveness_heating, kpi_scheduleEffectiveness_cooling,kpi_scheduleEffectiveness_electricity],
        'After-hours energy use ratio':[kpi_afterHoursEnergyFraction_heating,kpi_afterHoursEnergyFraction_cooling,kpi_afterHoursEnergyFraction_electricity]}
  
  except:
    d = {'Utility': ['Heating', 'Cooling'],
        'Schedule Effectiveness': [kpi_scheduleEffectiveness_heating, kpi_scheduleEffectiveness_cooling],
        'After-hours energy use ratio':[kpi_afterHoursEnergyFraction_heating,kpi_afterHoursEnergyFraction_cooling]}

  kpi_df = pd.DataFrame(data=d)

  writer = pd.ExcelWriter(os.path.join(output_path,'energyBase_summary.xlsx'), engine='xlsxwriter')# pylint: disable=abstract-class-instantiated
  kpi_df.to_excel(writer, sheet_name='KPIs')
  writer.save()
  writer.close()

  return

