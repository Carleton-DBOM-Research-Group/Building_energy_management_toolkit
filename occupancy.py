#Import required modules
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math
from datetime import timedelta
import os

def occupancy(floor,input_path,output_path,alwaysOnCount):   
    
    # Create a blank data frame to store KPIs
    kpi = pd.DataFrame(0,
                       index = floor.floor.unique(), 
                       columns = ['tArr_wkdy','tDpt_wkdy','sOcc_wkdy','tArr_wknd','tDpt_wknd','sOcc_wknd'])
    
    # Create a data frame to populate with building-level occupancy for weekdays
    bdg_wkdy = pd.DataFrame(0, 
                            index=range(0,23), 
                            columns = ['25th percentile','Median','75th percentile'])
    
    # Create a data frame to populate with building-level occupancy for weekdays
    bdg_wknd = pd.DataFrame(0, 
                            index=range(0,23), 
                            columns = ['25th percentile','Median','75th percentile'])
    
    # Loop through each floor 
    for j in floor.floor.unique():

        print("Generate KPIs for floor " + str(j) + "...")
        # Assign single floor to new data frame
        df = floor.loc[floor['floor']==j]

        #Subtract device count by average device count between 12am-3am (lower limit of 0) OR user inputted value
        if os.path.isfile(os.path.join(input_path, 'alwaysOn.txt'))==False:
                mask = ((df.index.hour>=0)&(df.index.hour<=3))
                alwaysOnCount = math.ceil(df[mask]['wifi counts'].mean())
        
        df['wifi counts'] = df['wifi counts'] - alwaysOnCount
        df.loc[df['wifi counts']<0,'wifi counts'] = 0

        # Specify desired quantiles
        quantiles = [.25,.5,.75]
        
        # Create blank list to store each quantile on workdays and populate
        line = []
        for i in quantiles:
            temp = df.loc[df['workday'] == True].groupby(['hour'])['wifi counts'].quantile(i)
            temp = round((temp-temp.min())/1.2) # 1.2 devices per occupant conversion
            line.append(temp)
        
        # Turn list into data frame, rename columns, and add to building-level data frame for workdays
        occ_wkdy = pd.concat(line, axis=1)
        occ_wkdy.columns = ['25th percentile','Median','75th percentile']
        bdg_wkdy = bdg_wkdy + occ_wkdy
        
        # Create blank list to store each quantile on weekends and populate
        line = []
        for i in quantiles:
            temp = df.loc[df['workday'] == False].groupby(['hour'])['wifi counts'].quantile(i)
            temp = round((temp-temp.min())/1.2) #Assuming 1.2 devices per person
            line.append(temp)
        
        # Turn list into data frame, rename columns, and add to building-level data frame for weekends
        occ_wknd = pd.concat(line, axis=1)
        occ_wknd.columns = ['25th percentile','Median','75th percentile']
        for col in occ_wknd:
                occ_wknd.loc[occ_wknd[col]<4,col] = 0 #If occupancy count is less than four per floor, count as no occupancy.
        bdg_wknd = bdg_wknd + occ_wknd

        # Determine KPIs and store them in data frame for function to return
        if occ_wkdy.iloc[:,2].max() == 0:
                kpi.iloc[j-1,0] = np.nan # no arrivals for Wkdy
                kpi.iloc[j-1,1] = np.nan # no departures for Wkdy
        else:
                tArr_Wkdy = max((np.where(occ_wkdy.iloc[:,2]/occ_wkdy.iloc[:,2].max() > 0.1)[0][0]-1),0) # tArr_Wkdy
                kpi.iloc[j-1,0] = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(tArr_Wkdy) * 60, 60))
                tDpt_wkdy = (np.where(occ_wkdy.iloc[:,2]/occ_wkdy.iloc[:,2].max() > 0.1)[0][-1]-1) # tDpt_wkdy
                kpi.iloc[j-1,1] = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(tDpt_wkdy) * 60, 60))
        kpi.iloc[j-1,2] = (occ_wkdy.iloc[:,2].max()) #sOcc_wkdy

        if occ_wknd.iloc[:,2].max() == 0:
                kpi.iloc[j-1,3] = np.nan # No arrivals for Wknd
                kpi.iloc[j-1,4] = np.nan # No departure for Wknd
        else:
                tArr_wknd = max((np.where(occ_wknd.iloc[:,2]/occ_wknd.iloc[:,2].max() > 0.1)[0][0]-1),0) # tArr_wknd
                kpi.iloc[j-1,3] = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(tArr_wknd) * 60, 60))
                tDpt_wknd = (np.where(occ_wknd.iloc[:,2]/occ_wknd.iloc[:,2].max() > 0.1)[0][-1]-1) # tDpt_wknd
                kpi.iloc[j-1,4] = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(tDpt_wknd) * 60, 60))
        kpi.iloc[j-1,5] = (occ_wknd.iloc[:,2].max()) # sOcc_wknd

    #----Building-level quantile plots----#
    print("Generate building-level quantile plots...")
    fig = plt.figure(figsize=(8, 4))

    # Weekday subplot
    ax = plt.subplot(1,2,1)
    ax.plot(bdg_wkdy.iloc[:,0],
            label = '25th percentile',
            color = 'red',
            linestyle = 'dashed',
            linewidth=2)
    ax.plot(bdg_wkdy.iloc[:,1],
            label = 'Median',
            color = 'black',
            linewidth=2)
    ax.plot(bdg_wkdy.iloc[:,2],
            label = '75th percentile',
            color = 'green',
            linestyle = 'dashed',
            linewidth=2)
    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # Subplot formatting
    plt.axis([0, 24, 0, math.ceil(bdg_wkdy.iloc[:,2].max()/50)*50])
    ax.set_xticks([0,6,12,18,24])
    ax.set_xticklabels(['00:00','06:00','12:00','18:00','23:45'])
    plt.title('Weekdays', fontsize=14, fontweight='bold')
    plt.xlabel('Time of day', fontsize=14)
    plt.ylabel('Estimated occupancy (persons)', fontsize=14)
    ax.fill_between(bdg_wkdy.index, bdg_wkdy.iloc[:,0],bdg_wkdy.iloc[:,2], color='grey',alpha=0.4)

    # Weekend subplot
    ax = plt.subplot(1,2,2)
    ax.plot(bdg_wknd.iloc[:,0],
            label = '25th percentile',
            color = 'red',
            linestyle = 'dashed',
            linewidth=2)
    ax.plot(bdg_wknd.iloc[:,1],
            label = 'Median',
            color = 'black',
            linewidth=2)
    ax.plot(bdg_wknd.iloc[:,2],
            label = '75th percentile',
            color = 'green',
            linestyle = 'dashed',
            linewidth=2)
    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # Subplot formatting
    plt.axis([0, 24, 0, math.ceil(bdg_wknd.iloc[:,2].max()/50)*50])
    ax.set_xticks([0,6,12,18,24])
    ax.set_xticklabels(['00:00','06:00','12:00','18:00','23:45'])
    plt.title('Weekends', fontsize=14, fontweight='bold')
    plt.xlabel('Time of day', fontsize=14)
    plt.ylabel('Estimated occupancy (persons)', fontsize=14)
    ax.fill_between(bdg_wknd.index, bdg_wknd.iloc[:,0],bdg_wknd.iloc[:,2], color='grey',alpha=0.4)
    
    # Output figure in console
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=3,prop={"size":12})
    plt.tight_layout()
    fig.savefig(os.path.join(output_path,'percentile_occ.png'),dpi=600,bbox_inches='tight')

    if len(floor) > 1 and os.path.isfile(os.path.join(input_path,'is_flr_lvl')):
        #----Floor-level occupancy plots----#
        print("Generate floor-level occupancy plots...")
        df = floor

        # Upper quantile at the floor level for the weekday and weekend for plot
        temp = df.loc[df['workday'] == True].groupby(['floor','hour'])['wifi counts'].quantile(0.75).unstack(level='hour').T
        occ_wkdy_floor = round((temp-temp.min())/1.2)
        for col in occ_wkdy_floor.columns:
                occ_wkdy_floor.loc[occ_wkdy_floor[col]<4,col] = 0 #If occupancy count is less than four per floor, count as no occupancy.

        temp = df.loc[df['workday'] == False].groupby(['floor','hour'])['wifi counts'].quantile(0.75).unstack(level='hour').T
        occ_wknd_floor = round((temp-temp.min())/1.2)
        for col in occ_wknd_floor.columns:
                occ_wknd_floor.loc[occ_wknd_floor[col]<4,col] = 0 #If occupancy count is less than four per floor, count as no occupancy.

        fig = plt.figure(figsize=(8, 4), dpi=600)

        # Weekday subplot
        x = occ_wkdy_floor.index
        y = occ_wkdy_floor.T.rename_axis('ID').values
        ax = plt.subplot(1,2,1)
        stacks = ax.stackplot(x,y,
                        labels = ["Floor " + str(floor_num) for floor_num in floor.floor.unique()])

        #hatches=["\\", "//","+",'*','o','x','.']
        #for stack, hatch in zip(stacks, hatches):
                #stack.set_hatch(hatch)

        # Hide the right and top spines
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # Subplot formatting
        plt.axis([0, 24, 0, math.ceil(bdg_wkdy.iloc[:,2].max()/50)*50])
        ax.set_xticks([0,6,12,18,24])
        ax.set_xticklabels(['00:00','06:00','12:00','18:00','23:45'])
        plt.title('Weekdays', fontsize=14, fontweight='bold')
        plt.xlabel('Time of day', fontsize=14)
        plt.ylabel('Estimated occupancy (persons)', fontsize=14)

        # Weekend subplot
        x = occ_wknd_floor.index
        y = occ_wknd_floor.T.rename_axis('ID').values
        ax = plt.subplot(1,2,2)
        stacks = ax.stackplot(x,y,
                        labels = ["Floor " + str(floor_num) for floor_num in floor.floor.unique()])
                        
        #for stack, hatch in zip(stacks, hatches):
                #stack.set_hatch(hatch)    

        # Hide the right and top spines
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # Subplot formatting
        plt.axis([0, 24, 0, math.ceil(bdg_wknd.iloc[:,2].max()/50)*50])
        ax.set_xticks([0,6,12,18,24])
        ax.set_xticklabels(['00:00','06:00','12:00','18:00','23:45'])
        plt.title('Weekends', fontsize=14, fontweight='bold')
        plt.xlabel('Time of day', fontsize=14)
        plt.ylabel('Estimated occupancy (persons)', fontsize=14)
        
        # Output figure in console
        handles, labels = ax.get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.97, 1), ncol=((len(kpi.index)//15)+1),prop={"size":10})
        plt.tight_layout()
        fig.savefig(os.path.join(output_path,'floor_level_occ.png'),dpi=600,bbox_inches='tight')
    
    else:
            print('Floor-level analysis disabled!')
    
    # Output KPIs in excel document
    print("Formatting KPIs...")
    writer = pd.ExcelWriter(os.path.join(output_path,'arrive_depart_maxOcc.xlsx'), engine='xlsxwriter')# pylint: disable=abstract-class-instantiated
    kpi.to_excel(writer, sheet_name='KPIs')
    writer.save()
    writer.close()
    
    return

def occupancyMotion(motion_df, output_path):
        """
        This function inputs motion detection data (presence undetected = 0, presence detected = 1) and outputs the typical
        earliest arrival time, latest arrival time, latest departure time, and duration of the longest break. This function is
        supplement to the base occupancy function (occupancy.py) which inputs wi-fi device count data. Users should be given
        the option to invoke either the base occupancy function or this function, or both, given availability of data.
        """

        start_date = motion_df.index.min() #Find first day of data
        end_date = motion_df.index.max() #Find last day of data

        delta = end_date - start_date #Find difference between first and last day

        firstArrTime_df = pd.DataFrame()
        lastDepTime_df = pd.DataFrame()
        breakDuration_df = pd.DataFrame()

        print('Analyzing ' + str(delta.days + 1) + ' days...')
        for i in range(delta.days + 1): #Cycle through each day
                day = start_date + timedelta(days=i)
                temp = motion_df[str(day.date())] #Create a temp df of hourly data for each day

                temp_firstArrTime = []
                temp_lastDepTime = []
                temp_breakDuration = []

                for j in temp.columns: #Cycle through the columns(sensors) of the temp df
                        
                        if temp[j].sum() > 0: #Check if any activity for the sensor for the day
                                temp_firstArrTime.append((temp[j] == 1).idxmax().hour) #Find first hour where occupancy is detected
                                temp_lastDepTime.append(temp[j].where(temp[j]==1).last_valid_index().hour) #Find last hour where occupancy is detected
                                temp_breakDuration.append((temp[(temp.index.hour>8) & (temp.index.hour<17)][j] == 0).sum()) #Sum hours between 8am and 5pm where vacancy is detected

                        else: #If no activity, give nan
                                temp_firstArrTime.append(0)
                                temp_lastDepTime.append(0)
                                temp_breakDuration.append(0)

                firstArrTime_df[day.date()] = pd.Series(temp_firstArrTime,dtype='float64')
                lastDepTime_df[day.date()] = pd.Series(temp_lastDepTime,dtype='float64')
                breakDuration_df[day.date()] = pd.Series(temp_breakDuration,dtype='float64')

        firstArrTime_df = firstArrTime_df.T #Transpose df to nxm (days(rows) x sensors(columns))
        lastDepTime_df = lastDepTime_df.T
        breakDuration_df = breakDuration_df.T

        firstArrTime_df.index = pd.to_datetime(firstArrTime_df.index) #Convert index to datetime
        lastDepTime_df.index = pd.to_datetime(lastDepTime_df.index)
        breakDuration_df.index = pd.to_datetime(breakDuration_df.index)

        mask = firstArrTime_df.index.weekday < 5 #Filter just the weekdays
        firstArrTime_df = firstArrTime_df[mask]
        lastDepTime_df = lastDepTime_df[mask]
        breakDuration_df = breakDuration_df[mask]

        absentDayFrac = []
        earliestArrTime = []
        latestArrTime = []
        latestDepTime = []
        longestBreakDuration = []

        for i in firstArrTime_df.columns: #For every sensor...
                temp_absentDayFrac = (firstArrTime_df[i]==0).sum()/len(firstArrTime_df[i]) #...find the fraction of time vacancy is detected.
                absentDayFrac.append(temp_absentDayFrac)
                earliestArrTime.append((firstArrTime_df[(firstArrTime_df[i]>5) & (firstArrTime_df[i]<22)][i].quantile(0.25+((temp_absentDayFrac*40)/100)))) #...find the 25th + 0.4(fraction of time vacancy is detected) quantile of first arrival time.
                latestArrTime.append((firstArrTime_df[(firstArrTime_df[i]>5) & (firstArrTime_df[i]<22)][i].quantile(0.75-((temp_absentDayFrac*40)/100)))) #...find the 75th - 0.4(fraction of time vacancy is detected) quantile of first arrival time.
                latestDepTime.append((lastDepTime_df[(lastDepTime_df[i]>5) & (lastDepTime_df[i]<22)][i].quantile(0.75-((temp_absentDayFrac*40)/100)))) #...find the 75th - 0.4(fraction of time vacancy is detected) quantile of last departure time.
                longestBreakDuration.append((breakDuration_df[(breakDuration_df[i]>0) & (breakDuration_df[i]<6)][i].quantile(0.75-((temp_absentDayFrac*40)/100)))) #...find the 75th - 0.4(fraction of time vacancy is detected) quantile of break duration.

        kpis = {'Earliest arrival time': ['{0:02.0f}:{1:02.0f}'.format(*divmod(float(round(np.nanquantile(earliestArrTime,0.25),1)) * 60, 60))], #Output 25th percentile of earliest arrival times
                'Latest arrival time': ['{0:02.0f}:{1:02.0f}'.format(*divmod(float(round(np.nanquantile(latestArrTime,0.75),1)) * 60, 60))], #Output 75th percentile of earliest arrival times
                'Latest departure time': ['{0:02.0f}:{1:02.0f}'.format(*divmod(float(round(np.nanquantile(latestDepTime,0.75),1)) * 60, 60))], #Output 75th percentile of latest departure times
                'Longest break duration': ['{0:02.0f}:{1:02.0f}'.format(*divmod(float(round(np.nanquantile(longestBreakDuration,0.75),1)) * 60, 60))]} #Output 75th percentile of longest break duration
        kpis_df = pd.DataFrame(data=kpis)

        #Output the KPIs in an excel spreadsheet
        print("Formatting KPIs...")
        writer = pd.ExcelWriter(os.path.join(output_path,'motion_detection_kpis.xlsx'), engine='xlsxwriter')# pylint: disable=abstract-class-instantiated
        kpis_df.to_excel(writer, sheet_name='KPIs')
        writer.save()
        writer.close()

        return

def execute_function_wifi(input_path, output_path):

        #Read csv files in input path
        wifi_files = os.listdir(input_path)
        wifi_files_csv = [f for f in wifi_files if f[-3:] == 'csv']

        #Read the wifi data
        floor_count = 0
        floor = []
        for f in wifi_files_csv:
                temp = pd.read_csv(os.path.join(input_path,f))
                temp[temp.columns[0]] = pd.to_datetime(temp[temp.columns[0]])#Convert timeframe column time to datetime object
                temp = temp.set_index(temp[temp.columns[0]])# Set the index to the timestamp
                time_diff = (temp.iloc[1][temp.columns[0]] - temp.iloc[0][temp.columns[0]]).total_seconds() / 60.0 #Find the difference (minutes) between time intervals

                floor_count += 1
                temp['floor'] = floor_count
                temp['hour'] = temp.index.hour
                temp['weekday'] = temp.index.weekday
                temp['workday'] = temp.weekday.isin(range(0,5)).values

                ind = temp['wifi counts'].rolling(int(480/time_diff)).std() > 0.001 # Disgard stagnant values (data acquisition error) based on an 8-hour window
                temp = temp.iloc[ind.values]

                floor.append(temp) # Store the data for this floor in the list

        floor = pd.concat(floor,axis=0)

        # extract start and end time from last temp file
        f = open(os.path.join(output_path, "period.txt"),"w+")
        f.write(str(min(temp[temp.columns[0]])) + " to " + str(max(temp[temp.columns[0]])))
        f.close()

        # Try to open alwaysOn text file.
        try:
                file = open(os.path.join(input_path,'alwaysOn.txt')) #Open text file if exists
                content = file.readlines()
                alwaysOnCount = int(content[0])
                
                file.close()
                print('Always-on device count entered...')
                
        except:
                print('No always-on device count entered. Always-on device count will be automatically calculated...')
                alwaysOnCount = 0

        #Run the occupancy analysis with wifi data
        occupancy(floor,input_path,output_path,alwaysOnCount)

        return

def execute_function_motion(input_path, output_path):

        #Read the motion detection data
        motion_files = os.listdir(input_path)
        motion_files_csv = [f for f in motion_files if f[-3:] == 'csv']
        motion_df = pd.read_csv(os.path.join(input_path, motion_files_csv[0]), index_col = 0, parse_dates=True)

        # extract start and end time from last temp file
        f = open(os.path.join(output_path, "period.txt"),"w+")
        f.write(str(min(motion_df.index)) + " to " + str(max(motion_df.index)))
        f.close()

        #Run the occupancy analysis with motion detection data
        occupancyMotion(motion_df,output_path)

        return 
