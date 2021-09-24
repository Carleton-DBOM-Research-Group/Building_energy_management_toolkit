#Import required modules
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from sklearn.tree import DecisionTreeRegressor
from sklearn import tree
from sklearn import preprocessing

def complaintsAnalytics(cmms_data,tOa,time_tOa,zone,zone_time,area,output_path):

    cmms_data = cmms_data.rename(columns={cmms_data.columns[0]: "Report Time", cmms_data.columns[1]: "Operator comments"})
    cmms_time = cmms_data['Report Time']
    cmms_time = pd.to_datetime(cmms_time)

    #hotComplain = cmms_data[cmms_data['Operator comments'].str.contains("hot", "water")]
    #hotComplainTime = pd.to_datetime(hotComplain['Report Time'])

    #coldComplain = cmms_data[cmms_data['Operator comments'].str.contains("cold","water")]
    #coldComplainTime = pd.to_datetime(coldComplain['Report Time'])

    if len(zone) != 0:
        startTime = max(time_tOa.min(),zone_time.min(),cmms_time.min())
        stopTime = min(time_tOa.max(),cmms_time.max(),zone_time.max())
    else:
        startTime = max(time_tOa.min(),cmms_time.min())
        stopTime = min(time_tOa.max(),cmms_time.max())
    time = pd.date_range(start=startTime,end=stopTime,freq='h')

    data = pd.DataFrame()
    data['Report Time'] = time
    data['tOa'] = tOa
    
    
    zone_tIn = zone.filter(like='tIn').mean(axis=1)
    data['zone_tIn_mean'] = zone_tIn

    print('Collecting entries containing "cold" or "hot"...')
    cmms_data['coldComplain'] =cmms_data['Operator comments'].str.contains("cold",case=False).fillna(0).astype(int)
    cmms_data['hotComplain'] = cmms_data['Operator comments'].str.contains("hot",case=False).fillna(0).astype(int)


    fig = plt.figure(figsize=(12, 6)).gca()
    #Sort complaints by month
    print('Plotting entries with month...')
    ax = plt.subplot(1,2,1)
    months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    cmms_data['Report Time'] = pd.to_datetime(cmms_data['Report Time'], dayfirst=True)
    monthly_cold_complaints = cmms_data.groupby([cmms_data['Report Time'].dt.month_name()], sort=False).sum().eval('coldComplain')
    monthly_hot_complaints = cmms_data.groupby([cmms_data['Report Time'].dt.month_name()], sort=False).sum().eval('hotComplain')

    ax.bar(months,monthly_cold_complaints,width=0.65,color='tab:blue', bottom=monthly_hot_complaints)
    ax.bar(months,monthly_hot_complaints,width=0.65,color='tab:red')

    ax.set_ylabel('Number of complaints',fontsize=18)
    ax.set_xlabel('Month',fontsize=18)
    plt.yticks(fontsize=13)
    ax.legend(['Cold', 'Hot'],loc='upper center', frameon=False, bbox_to_anchor=(0.5, 1.15), ncol=2, prop={"size":13})
    ax.set_xticklabels(months, rotation=90, fontsize=13)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    #Sort complaints by time of day
    ax = plt.subplot(1,2,2)
    print('Plotting entries per period of day...')
    cmms_data['period'] = (cmms_data['Report Time'].dt.hour % 24 + 4) // 4
    cmms_data['period'].replace({1: 'Late Night',
                        2: 'Early Morning',
                        3: 'Morning',
                        4: 'Noon',
                        5: 'Evening',
                        6: 'Night'}, inplace=True)

    #Count number of cold complaints per period
    period_cold_complaints = []
    for period in ['Late Night','Early Morning','Morning','Noon','Evening','Night']:
        period_cold_complaints.append(((cmms_data['coldComplain']==1)&(cmms_data['period']==period)).sum())

    #Count number of hot complaints per period
    period_hot_complaints = []
    for period in ['Late Night','Early Morning','Morning','Noon','Evening','Night']:
        period_hot_complaints.append(((cmms_data['hotComplain']==1)&(cmms_data['period']==period)).sum())

    ax = plt.subplot(1,2,2)
    periods = ['Late night','Early morning','Morning','Afternoon','Evening','Night']
    ax.bar(periods,period_cold_complaints,width=0.65,color='tab:blue')
    ax.bar(periods,period_hot_complaints,width=0.65,bottom=period_cold_complaints,color='tab:red')

    ax.set_ylabel('Number of complaints',fontsize=18)
    ax.set_xlabel('Period of day',fontsize=18)
    ax.legend(['Cold', 'Hot'],loc='upper center', frameon=False, bbox_to_anchor=(0.5, 1.15), ncol=2, prop={"size":13})
    ax.set_xticklabels(periods, fontsize=13)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45,ha="right",rotation_mode="anchor")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.yticks(fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(output_path,'complaints_breakdown.png'),dpi=600)

    #Merge CMMS data with tOa and zone temp data
    cmms_data = pd.concat([cmms_data, data], ignore_index = True)
    cmms_data.sort_values(by='Report Time', inplace = True)

    #Interpolate any Nan values
    cmms_data[['tOa','zone_tIn_mean']] = cmms_data[['tOa','zone_tIn_mean']].interpolate(method='linear', limit_direction='forward', axis=0)
    cmms_data = cmms_data.dropna(how='any')

    #Take only cold and hot complaints
    coldComplain_grouped = cmms_data.loc[cmms_data['coldComplain'] == 1]
    hotComplain_grouped = cmms_data.loc[cmms_data['hotComplain'] == 1]

    #Plot complaints in relation to zone/outdoor air temp.
    print('Plotting entries with indoor/outdoor air temperatures...')
    fig = plt.figure(figsize=(7, 5))
    plt.scatter(x=coldComplain_grouped['zone_tIn_mean'],y=coldComplain_grouped['tOa'],c='blue',marker='o',s= [20**2],alpha=0.2)
    plt.scatter(x=hotComplain_grouped['zone_tIn_mean'],y=hotComplain_grouped['tOa'],c='red',marker='o',s=20**2,alpha=0.2)
    plt.xlabel('Indoor air temperature (C)',fontsize=16,fontweight='bold')
    plt.ylabel('Outdoor air temperature (C)',fontsize=16,fontweight='bold')
    plt.xlim(15,30)
    plt.ylim(-20,35)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.grid()
    plt.legend(['Cold complaint','Hot complaint'],loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, prop={"size":16},frameon=False)
    plt.tight_layout()
    plt.savefig(os.path.join(output_path,'complaint_scatter.png'),dpi=600)


    cmms_data['dayOfWeek'] =pd.to_datetime(cmms_data['Report Time']).dt.dayofweek
    cmms_data['hourOfDay'] =pd.to_datetime(cmms_data['Report Time']).dt.hour
    cmms_data['dayofweek_name'] = pd.to_datetime(cmms_data['Report Time']).dt.day_name()
    cmms_data['is_weekend'] = np.where(cmms_data['dayofweek_name'].isin(['Sunday','Saturday']),1,0)

    le = preprocessing.LabelEncoder()
    le.fit(cmms_data['period'])
    cmms_data['period'] =le.transform(cmms_data['period'])

    X = cmms_data[['hourOfDay','dayOfWeek','tOa']]
    y = cmms_data['coldComplain']+cmms_data['hotComplain']

    reg = DecisionTreeRegressor(max_leaf_nodes=3,random_state=0,splitter='random')
    reg.fit(X, y)

    fn=['Hour of the day','Day of the week','Outdoor air temperature (C)']
    fig, ax = plt.subplots(figsize = (7,5), dpi=600)
    tree.plot_tree(reg,feature_names = fn,filled = False, label='none',impurity='False',proportion=True,precision=0,fontsize=12)

    #plt.scatter(X['hour of day'], reg.predict(X), color = 'blue')
    #plt.xlabel('Outdoor air temperature (C)')
    #plt.ylabel('Frequency of Complaints')

    plt.tight_layout()
    fig.savefig(os.path.join(output_path,'decision_tree.png'),dpi=600)


    #Calculate KPIs
    print('Formatting KPIs...')
    cmms_data['month'] = pd.to_datetime(cmms_data['Report Time']).dt.month
    c = cmms_data[['hotComplain']].where((cmms_data['month'] < 5) | (cmms_data['month']> 9)).sum()
    b=cmms_data[['month']].where((cmms_data['month'] < 5) | (cmms_data['month']> 9)).sum()
    a = ((b *5/7/24)*area/1000)
    kpi_freqHot_winter = float(c)/float(a)

    d= cmms_data[['hotComplain']].where((cmms_data['month'] >= 5) & (cmms_data['month'] <= 9)).sum()
    kpi_freqHot_summer = float(d)/float(a)

    e = cmms_data[['coldComplain']].where((cmms_data['month'] < 5) | (cmms_data['month']> 9)).sum()
    kpi_freqCold_winter = float(e)/float(a)

    f= cmms_data[['coldComplain']].where((cmms_data['month'] >= 5) & (cmms_data['month'] <= 9)).sum()
    kpi_freqCold_summer = float(f) / float(a)

    #Output an excel table with KPIs
    d = {'Type of complaint': ['Hot complaint', 'Cold complaint'],
        'Winter': [kpi_freqHot_winter,kpi_freqCold_winter],
        'Summer':[kpi_freqHot_summer,kpi_freqCold_summer]}
    kpi_df = pd.DataFrame(data=d)

    writer = pd.ExcelWriter(os.path.join(output_path,'complaints_freq.xlsx'), engine='xlsxwriter') # pylint: disable=abstract-class-instantiated
    kpi_df.to_excel(writer, sheet_name='Daily frequency of complaints')
    writer.save()
    writer.close()

    return

def execute_function(input_path, output_path):

    #Try reading CMMS data file
    print('Reading CMMS data file...')
    cmms_files = os.listdir(os.path.join(input_path,'cmms'))
    cmms = pd.read_csv(os.path.join(input_path, 'cmms',cmms_files[0]),encoding='unicode escape')

    # try reading AMY weather data
    print('Reading weather data file...')
    weather_files = os.listdir(os.path.join(input_path,'weather'))
    weather = pd.read_csv(os.path.join(input_path, 'weather',weather_files[0]),usecols=[3],skiprows=18,encoding='unicode escape')
    tOa = weather[weather.columns[0]]
    time_tOa = pd.date_range(start="2019-01-01",end="2019-12-31 23:00:00" ,freq='h')
    

    # Try reading zone-level HVAC data files
    print('Reading zone-level HVAC data files...')
    zone_files = os.listdir(os.path.join(input_path,'zone'))
    zone_files_csv = [f for f in zone_files if f[-3:] == 'csv']
    zone = pd.DataFrame()
    read_first_file = False
    for f in zone_files_csv:
        data = pd.read_csv(os.path.join(input_path,'zone',f), usecols=[0,1,2,3,4])

        #Remove any entries over 8760 hours
        if len(data) > 8760:
            data.drop(data.tail(len(data)-8760).index,inplace=True)

        #Save the timeframe column of the first zone dataframe
        if read_first_file == False:
            zone_time = data[data.columns[0]]
            zone_time= pd.to_datetime(zone_time)
            read_first_file = True

        data.drop(data.columns[0], axis=1, inplace=True)
        zone = pd.concat([zone,data],axis=1)
    
    # read inputted floor area from floor_area.txt
    file = open(os.path.join(input_path,'floor_area.txt'))
    content = file.readlines()
    bldg_area = int(content[0])
    file.close()

    #Try analyzing the data
    complaintsAnalytics(cmms,tOa,time_tOa,zone,zone_time,bldg_area,output_path)