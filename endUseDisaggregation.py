#Import required libraries
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from geneticalgorithm import geneticalgorithm as ga
import warnings
warnings.filterwarnings('ignore')
import ruptures as rpt

def execute_function(input_path, output_path):

    # Define Constant Values - Will need to be changed to suit different buildings
    device_to_occ = 1.2 # Assumed number of devices per person

    # read energy data file
    print("Reading energy meter data...")
    energy_files = os.listdir(os.path.join(input_path,'energy'))
    energy = pd.read_csv(os.path.join(input_path, 'energy',energy_files[0]))

    # read Wi-Fi data files
    print("Reading Wi-Fi device count data files...")
    wifi_files = os.listdir(os.path.join(input_path,'wifi'))
    wifi_files_csv = [f for f in wifi_files if f[-3:] == 'csv']
    wifi = pd.DataFrame()
    read_first_wifi_file = False
    for f in wifi_files_csv:
        if read_first_wifi_file == False:
            wifi1 = pd.read_csv(os.path.join(input_path,'wifi',f),index_col=0,parse_dates=True)
            wifi = pd.concat([wifi,wifi1[wifi1.columns[0]]],axis=1)
        else:
            data = pd.read_csv(os.path.join(input_path,'wifi',f), usecols=[1])
            wifi = pd.concat([wifi,data],axis=1)

    wifi['total'] = wifi.sum(axis=1)

    wifi = wifi.set_index(wifi1.index)
    wifi = wifi.asfreq('1H')

    # read zone-level HVAC data - extract fraction of active perimeter heating devices in all zones
    print("Reading zone-level HVAC data...")
    zone_files = os.listdir(os.path.join(input_path,'zone'))
    zone_files_csv = [f for f in zone_files if f[-3:] == 'csv']
    sRad = pd.DataFrame()
    for f in zone_files_csv:
        data = pd.read_csv(os.path.join(input_path,'zone',f), usecols=[4])
        sRad = pd.concat([sRad,data],axis=1)
        
    sRad.drop(sRad.tail(1).index,inplace=True) # drop last row of sRad
    

    # read AHU-level HVAC data
    print("Reading AHU-level HVAC data...")
    ahu_files = os.listdir(os.path.join(input_path,'ahu'))
    ahu_files_csv = [f for f in ahu_files if f[-3:] == 'csv']
    dfs = []
    num_of_ahus = 0
    for f in ahu_files_csv:
        num_of_ahus += 1
        data = pd.read_csv(os.path.join(input_path,'ahu',f)) #Specify the sample data for ahu files
        if len(data) > 8760:
            data.drop(data.tail(len(data)-8760).index,inplace=True)
        data = data.rename(columns={data.columns[1]:'tSa'+str(num_of_ahus),data.columns[2]:'tRa'+str(num_of_ahus),data.columns[3]:'tOa'+str(num_of_ahus),data.columns[4]:'pSa'+str(num_of_ahus),data.columns[5]:'sOa'+str(num_of_ahus),data.columns[6]:'sHc'+str(num_of_ahus),data.columns[7]:'sCc'+str(num_of_ahus),data.columns[8]:'sFan'+str(num_of_ahus)})
        dfs.append(data)

    ahu = pd.concat(dfs,axis=1)   

    # read inputted variables
    file = open(os.path.join(input_path,'endUseDisaggregation_var.txt'))
    content = file.readlines()

    bldg_area = int(content[0])
    cooling_type = str(content[1]) 

    file.close()
    
    #Extract normalized heating/cooling
    normalized_heating = (energy[energy.columns[3]]-energy[energy.columns[3]].min())/(energy[energy.columns[3]].max()-energy[energy.columns[3]].min())
    normalized_cooling = (energy[energy.columns[2]]-energy[energy.columns[2]].min())/(energy[energy.columns[2]].max()-energy[energy.columns[2]].min())

    #If heat/cool valve position > 0 while heat/cool energy is near zero, set  valve position to zero (no hot/chilled water in pipes to respond to valve opening/closing.
    for i in range(1,num_of_ahus+1):
        ahu['sHc'+str(i)] = ahu['sHc'+str(i)] * (normalized_heating > 0.1)
        ahu['sCc'+str(i)] = ahu['sCc'+str(i)] * (normalized_cooling > 0.1)

    sRad = sRad.multiply(normalized_heating > 0.1 , axis="index")

    #If AHU not running (supply pressure less than 100 Pa), 
    #heating/cooling valve position makes no impact on the heating/cooling energy consumption
    for i in range(1,num_of_ahus+1):
        ahu['sHc'+str(i)].loc[ahu['pSa'+str(i)] < 100] = 0
        ahu['sCc'+str(i)].loc[ahu['pSa'+str(i)] < 100] = 0
        ahu['pSa'+str(i)].loc[ahu['pSa'+str(i)] < max(ahu['pSa'+str(i)])/8] = 0

    data = pd.DataFrame(energy[energy.columns[0]]) #Create new dataframe with same timestamp as energy file

    for i in range(1,num_of_ahus+1):
        data['pSa'+str(i)] = (ahu['pSa'+str(i)]-ahu['pSa'+str(i)].min())/(ahu['pSa'+str(i)].max()-ahu['pSa'+str(i)].min()) #Populate with pSa data from all AHUs
        
        data['sHc'+str(i)] = ahu['sHc'+str(i)] #Populate with sHc data from all AHUs

        data['sCc'+str(i)] = ahu['sCc'+str(i)] #Populate with sCc data from all AHUs


    data['sRad'] = sRad.mean(axis=1) #Populate with sRad data
    data['Elec'] = energy[energy.columns[1]]#Populate with electricity data
    data['Clg'] = energy[energy.columns[2]]#Populate with cooling data
    data['Htg'] = energy[energy.columns[3]]#Populate with heating data

    occDataStart = min(wifi.index) #Define occupancy data collection start time
    occDataStop = max(wifi.index) #Define occupancy data collection end time

    energy_time = pd.to_datetime(energy[energy.columns[0]])
    start = max(occDataStart,min(energy_time))
    end = min(occDataStop, max(energy_time))

    ind = pd.date_range(start, end, freq='1H')

    if min(wifi.index) > min(energy_time):
        ind1 = energy_time>= min(wifi.index)

    data = data[ind1]

    #Convert wi-fi device count to occupancy
    occupancy = np.round((wifi['total']-min(wifi['total']))/device_to_occ)
    occupancy = occupancy[ind]
    data['occupancy'] = occupancy.values

    #find change points
    print('Finding change points using Ruptures... This will take a while...', flush=True)
    algo = rpt.Pelt(model= "rbf",min_size=200, jump=5).fit(data['Elec'].values)
    ipt = algo.predict(pen=10)

    # Select columns of ahu heating/cooling coil and supply air pressure
    x_Htg_list = []
    for i in range(1,num_of_ahus+1):
        x_Htg_list.append('sHc'+str(i))
    x_Htg_list.append('sRad')

    x_Clg_list = []
    for i in range(1,num_of_ahus+1):
        x_Clg_list.append('sCc'+str(i))

    x_Elec_list = []
    x_Elec_list.append('occupancy')
    for i in range(1,num_of_ahus+1):
        x_Elec_list.append('pSa'+str(i))

    x_Htg = data[x_Htg_list]
    x_Clg = data[x_Clg_list]

    if cooling_type == "Chillers (On-site)":
        ix = [i for i in list(range(data.index[0],data.index[0]+ipt[0])) + list(range(data.index[0]+ipt[5],data.index[-1]))]  
        x_Elec = data.loc[ix, x_Elec_list]
        y_Elec = data.loc[ix, 'Elec']

    else: 
        x_Elec = data[x_Elec_list]
        y_Elec = data[['Elec']]

    #Create function for cooling, heating, and electricity load disaggregation models

    def rmse_ElecMdl(x): #Electricity disagg model
        h = 0
        predictors = x_Elec
        response = y_Elec
        for i in range(predictors.shape[1]-1):
            h = x[i+1]*predictors.iloc[:,i+1] + h

        h = h + x[0]*predictors.iloc[:,0] + x[i+2]
        return np.sqrt(((response - h) ** 2).mean())

    def rmse_HtgMdl(x): #Heating disagg model
        h = 0
        predictors =data[x_Htg_list]
        response =data['Htg']
        for i in range(predictors.shape[1]-1):
            h = x[i]*predictors.iloc[:,i] + h
        
        h = h + x[i+1]*predictors.iloc[:,i+1] + x[i+2]
        return np.sqrt(((response - h) ** 2).mean())

    def rmse_ClgMdl(x): #Cooling disagg model
        predictors=data[x_Clg_list]
        response=data['Clg']
        h = 0
        for i in range(predictors.shape[1]):
            h = x[i]*predictors.iloc[:,i] + h
    
        return np.sqrt(((response - h) ** 2).mean())

    #Setting up parameters for genetic algorithm
    algorithm_param = {'max_num_iteration': 10,\
                    'population_size':10000,\
                    'mutation_probability':0.1,\
                    'elit_ratio': 0.01,\
                    'crossover_probability': 0.5,\
                    'parents_portion': 0.3,\
                    'crossover_type':'uniform',\
                    'max_iteration_without_improv':None}

    limits = [[0,200]] #Limit for multiplier for the occupancy-driven component of electricity
    for i in range(1,num_of_ahus+1): #For every AHU, add another upper/lower bound [0,100], multiplier for i'th ahu fan
        limits.append([0,100]) 
    limits.append([0,bldg_area*20/1000]) # limit for the constant electricity (background plug load and lighting)

    varbound = np.array(limits)

    model_Elec_GA = ga(function=rmse_ElecMdl,
                        dimension=2+num_of_ahus,
                        variable_type='real',
                        variable_boundaries=varbound,
                        algorithm_parameters=algorithm_param,
                        convergence_curve = False)

    print('Estimate parameters of electricity disaggregation model using GA... This will take a while...', flush=True)
    model_Elec_GA.run()

    #rmse_HtgMdl([1.2879,1.5583,0,0])

    limits = []
    for i in range(1,num_of_ahus+1): #For every AHU, add another upper/lower bound [0,10],multiplier for i'th ahu heating coil
        limits.append([0,10])
    limits.append([0,10]) #limits for multiplier for perimeter heating devices
    limits.append([0,bldg_area*2/1000]) #limits for the constant heating use (to account for hot water heating)

    varbound = np.array(limits)

    model_Htg_GA=ga(function=rmse_HtgMdl,
                    dimension=2+num_of_ahus, # This needs to be changed to 2 + # of AHUs
                    variable_type='real',
                    variable_boundaries=varbound,
                    algorithm_parameters=algorithm_param,
                    convergence_curve = False)

    print('Estimate parameters of heating use disaggregation model using GA... This will take a while...', flush=True)
    model_Htg_GA.run()

    varbound=np.array([[0,10]]*num_of_ahus) #limits for multiplier for i'th ahu cooling coil

    model_Clg_GA=ga(function=rmse_ClgMdl,
                    dimension=num_of_ahus, # This needs to be changed to # of AHUs
                    variable_type='real',
                    variable_boundaries=varbound,
                    algorithm_parameters=algorithm_param,
                    convergence_curve = False)

    print('Estimate parameters of cooling use disaggregation model using GA... This will take a while...',flush=True)
    model_Clg_GA.run()

    #Extract estimated parameter from genetic algorithm
    prmtr_Clg = model_Clg_GA.best_variable
    prmtr_Htg =model_Htg_GA.best_variable
    prmtr_Elec = model_Elec_GA.best_variable

    electricity_distribution = pd.DataFrame()
    for i in range(1,num_of_ahus+1):
        electricity_distribution = pd.concat([electricity_distribution,(data['pSa'+str(i)]*prmtr_Elec[i])], axis=1)

    electricity_distribution = electricity_distribution.sum(axis=1)

    electricity_occupant = data.loc[:,['occupancy']] * prmtr_Elec[0] + prmtr_Elec[-1]

    if cooling_type == "Chillers (On-site)":
        electricity_chiller = data['Elec'] - electricity_distribution -electricity_occupant['occupancy']
        electricity_chiller.loc[electricity_chiller < max(electricity_chiller)/10] = 0

    heating_ahu = pd.DataFrame()
    for i in range(1,num_of_ahus+1):
        heating_ahu = pd.concat([heating_ahu,(x_Htg['sHc'+str(i)]*prmtr_Htg[i-1])], axis=1)

    heating_perimeter = prmtr_Htg[-2] * x_Htg.loc[:,['sRad']]
    heating_other = prmtr_Htg[-1] *np.ones(x_Htg['sHc1'].shape)

    cooling_ahu = pd.DataFrame()
    for i in range(1,num_of_ahus+1):
        cooling_ahu = pd.concat([cooling_ahu,(x_Clg['sCc'+str(i)]*prmtr_Clg[i-1])], axis=1)

    data[data.columns[0]] = pd.to_datetime(data[data.columns[0]]) #Convert 'Timestamp' column of dataframe to datetime
    data['week_of_year'] = data[data.columns[0]].apply(lambda x: x.weekofyear)
    data['Week_Number'] = data[data.columns[0]].dt.week #Assign a week number to each data point

    # Calculate EUIs of end uses as KPIs
    print('Calculating KPIs...')
    kpi_electricity_chiller = int(round(electricity_chiller.sum()/bldg_area))
    kpi_electricity_distribution = int(round(electricity_distribution.sum()/bldg_area))
    kpi_electricity_occupant = int(round(electricity_occupant[electricity_occupant.columns[0]].sum()/bldg_area))
        
    kpi_heating_other = int(round(heating_other.sum()/bldg_area))
    kpi_heating_ahu = (heating_ahu.sum()/bldg_area).round().astype(int)
    kpi_heating_perimeter = int(round(heating_perimeter[heating_perimeter.columns[0]].sum()/bldg_area))
        
    kpi_cooling_ahu = (cooling_ahu.sum()/bldg_area).round().astype(int)


    #Export an excel sheet with KPIs
    print('Formatting KPIs...')
    d_elec = {'End-uses': ['Fans & pumps','Lighting & plug loads','Chillers'],
        'Total annual EUI (kWh/m2)': [kpi_electricity_distribution, kpi_electricity_occupant,kpi_electricity_chiller]}

    d_htg = {'End-uses': ['Perimeter heating','Heating coils (per AHU)','Other'],
        'Total annual EUI (kWh/m2)': [kpi_heating_perimeter,kpi_heating_ahu.values,kpi_heating_other]}

    d_clg = {'End-uses': ['Cooling coils (per AHU)'],
        'Total annual EUI (kWh/m2)': [kpi_cooling_ahu.values]}

    elec_kpi_df = pd.DataFrame(data=d_elec)
    htg_kpi_df = pd.DataFrame(data=d_htg)
    clg_kpi_df = pd.DataFrame(data=d_clg)

    writer = pd.ExcelWriter(output_path + r'\endUseDisagg_summary.xlsx', engine='xlsxwriter') # pylint: disable=abstract-class-instantiated
    elec_kpi_df.to_excel(writer, sheet_name='Electricity')
    htg_kpi_df.to_excel(writer, sheet_name='Heating')
    clg_kpi_df.to_excel(writer, sheet_name='Cooling')
    writer.save()
    writer.close()

    print('Creating disaggregation plots...',flush=True)
    disagg_Elect= pd.DataFrame()
    disagg_Elect['electricity_distribution'] = electricity_distribution
    disagg_Elect['electricity_occupant'] = electricity_occupant
    disagg_Elect['electricity_chiller'] = electricity_chiller

    disagg_Elect.index = data[data.columns[0]]

    disagg_Elect['weekofyear'] = disagg_Elect.index.weekofyear
    disagg_Elect['weekofyear'].loc[disagg_Elect['weekofyear'] == 1] = 53

    disagg_Htg = pd.DataFrame()
    disagg_Htg['heating_other'] = heating_other
    disagg_Htg['heating_perimeter'] = heating_perimeter.values

    for i in range(1,num_of_ahus+1):
        disagg_Htg['heating_ahu'+str(i)] = heating_ahu['sHc'+str(i)].values

    disagg_Htg['weekofyear'] = data['Week_Number'].values
    disagg_Htg['weekofyear'].loc[disagg_Htg['weekofyear'] == 1] = 53
    disagg_Clg = pd.DataFrame()
    for i in range(1,num_of_ahus+1):
        disagg_Clg['cooling_ahu'+str(i)] = cooling_ahu['sCc'+str(i)]

    disagg_Clg['weekofyear'] = data['Week_Number'].values
    disagg_Clg['weekofyear'].loc[disagg_Clg['weekofyear'] == 1] = 53

    weeklyElecIntensity =[]
    weeklyHtgIntensity = []
    weeklyClgIntensity = []
    for i in range(min(disagg_Elect['weekofyear']),max(disagg_Elect['weekofyear'])+1):
        if cooling_type == "Chillers (On-site)":
            a1 = disagg_Elect['electricity_distribution'].loc[disagg_Elect['weekofyear'] == i]
            a2 = disagg_Elect['electricity_occupant'].loc[disagg_Elect['weekofyear'] == i]
            a3 = disagg_Elect['electricity_chiller'].loc[disagg_Elect['weekofyear']==i]
            a = pd.DataFrame()
            a['a1']=a1
            a['a2']=a2
            a['a3']=a3
            a = np.sum(a)/bldg_area
            weeklyElecIntensity.append(a.values)

        else:
            a1 = disagg_Elect['electricity_distribution'].loc[disagg_Elect['weekofyear'] == i]
            a2 = disagg_Elect['electricity_occupant'].loc[disagg_Elect['weekofyear'] == i]
            a = pd.DataFrame()
            a['a1']=a1
            a['a2']=a2
            a = np.sum(a)/bldg_area
            weeklyElecIntensity = [weeklyElecIntensity,a]
        
        a = pd.DataFrame()
        for j in range(1,num_of_ahus+1):
            a['a'+str(j)] = disagg_Clg['cooling_ahu'+str(j)].loc[disagg_Clg['weekofyear']==i]
        
        a = np.sum(a)/bldg_area
        weeklyClgIntensity.append(a.values)

        a= pd.DataFrame()
        a['a1'] = disagg_Htg['heating_other'].loc[disagg_Htg['weekofyear'] == i]
        a['a2'] = disagg_Htg['heating_perimeter'].loc[disagg_Htg['weekofyear']==i]
        for j in range(1,num_of_ahus+1):
            a['a'+str(j+2)] = disagg_Htg['heating_ahu'+str(j)].loc[disagg_Htg['weekofyear']==i]
        
        a = np.sum(a)/bldg_area
        weeklyHtgIntensity.append(a.values)

    #Create subplots
    index=pd.date_range(start='2019/04/21', end='2019/12/31',freq='w')
    week=index.weekofyear+1

    plt.figure(figsize=(21,6))
    #pal = ["#9b59b7", "#e74c4c", "#34496e", "#2ecc72"]

    plt.subplot(131)
    weeklyElecIntensity = pd.DataFrame(weeklyElecIntensity, index=week)
    plt.stackplot(week,weeklyElecIntensity.iloc[:, 0:3].T)
    plt.xlim(0,52)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.xlabel('Week of year',fontsize = 22)
    plt.ylabel("Electricity (kWh/$m^{2}$)", fontsize= 22)
    plt.legend(("Fans & Pumps","Lighting & Plug loads","Chillers"), loc='upper center', bbox_to_anchor=(0.5, 1.25), ncol=2, prop={"size":17})

    plt.subplot(132)
    weeklyClgIntensity = pd.DataFrame(weeklyClgIntensity, index=week)
    plt.stackplot(week,weeklyClgIntensity.iloc[:, 0:2].T)
    plt.xlim(0,52)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.xlabel('Week of year',fontsize = 22)
    plt.ylabel("Cooling (kWh/$m^{2}$)", fontsize= 22)
    ahu_legend_labels = []
    for i in range(1,num_of_ahus+1):
        ahu_legend_labels.append('AHU '+str(i))
    plt.legend(ahu_legend_labels, loc='upper center', bbox_to_anchor=(0.5, 1.16+0.09*((num_of_ahus//2)-1)), ncol=2, prop={"size":17})

    plt.subplot(133)
    weeklyHtgIntensity = pd.DataFrame(weeklyHtgIntensity, index=week)
    plt.stackplot(week,weeklyHtgIntensity.iloc[:, 0:4].T)
    plt.xlim(0,52)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.xlabel('Week of year',fontsize = 22)
    plt.ylabel("Heating (kWh/$m^{2}$)", fontsize= 22)
    ahu_legend_labels = ['Domestic hot water','Perimeter heaters']
    for i in range(1,num_of_ahus+1):
        ahu_legend_labels.append('AHU '+str(i))
    plt.legend(ahu_legend_labels,loc='upper center', bbox_to_anchor=(0.5, 1.16+0.09*(((2+num_of_ahus)//2)-1)), ncol=2, prop={"size":17})

    plt.tight_layout()
    plt.savefig(output_path + r'\endUseDisaggregation.png',dpi=900)