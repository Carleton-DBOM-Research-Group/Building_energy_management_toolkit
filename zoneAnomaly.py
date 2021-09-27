#Import required modules
import os
import pandas as pd
import numpy as np
from sklearn import cluster,metrics,mixture
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
pd.options.mode.chained_assignment = None  # default='warn'

def zoneAnomaly (tIn,qFlo,qFloSp,sRad,output_path):

    print('Cleaning data...')
    #Remove stagnant and nan values
    mask = tIn.rolling(24).std().mean(axis=1) < 0.001
    for df in [tIn,qFlo,qFloSp,sRad]:
        df.drop(df[mask].index, inplace=True)     
    
    print('Extracting data for heating season...')
    #Extract workhours in WINTER (December-February)
    mask = ((tIn.index.hour>9)&(tIn.index.hour<17)) & (tIn.index.weekday<5) & ((tIn.index.month>11)|(tIn.index.month<3))
    tInWntr = tIn[mask].mean(axis=0)
    qFloWntr = qFlo[mask]
    qFloSpWntr = qFloSp[mask]
    sRadWntr_mean = sRad[mask].mean(axis=0) #Take the mean reheat/radiant heat valve per zone
    
    qFloWntrErr = ((qFloWntr-qFloSpWntr)/qFloSpWntr) #Calculate airflow control error
    qFloWntrErr = qFloWntrErr.replace(np.nan, 0) #If NaN value, replace with zero (NaNs are a result of (qFloWntr-qFloSpWntr)/qFloSpWntr == 0/0, and thus is no airflow error)
    qFloWntrErr = qFloWntrErr.replace([np.inf, -np.inf], np.nan).dropna(axis=0) #Remove inf/-inf values (This is a result of qFloSpWntr == 0, and thus is inconclusive)
    qFloWntrErr_mean = qFloWntrErr.mean(axis=0) #Take the mean airflow control error per zone

    tInErrNrm = tInWntr / np.linalg.norm(tInWntr)
    qFloErrNrm = qFloWntrErr_mean / np.linalg.norm(qFloWntrErr_mean)
    
    if sRadWntr_mean.max() > 1:
        sRadNrm = sRadWntr_mean/100
    else:
        sRadNrm = sRadWntr_mean

    frameWntr = pd.concat([tInErrNrm,qFloErrNrm,sRadNrm],axis=1, join='inner')

    best_score = 0
    print('Cluster zones for heating season based on indoor air temperature setpoint error, airflow setpoint error, & fraction of active perimeter heating devices...')
    for n in range(3,5): # loop through 3 to 4 clusters, try different cluster algorithms
        evaKMeans = cluster.KMeans(n_clusters=n,random_state=1).fit_predict(frameWntr) #Create cluster labels
        kmeans_score = metrics.calinski_harabasz_score(frameWntr, evaKMeans) # Score cluster labels

        evaGMdist = mixture.GaussianMixture(n_components=n,covariance_type='full').fit_predict(frameWntr) #Create cluster labels
        gmm_score = metrics.calinski_harabasz_score(frameWntr, evaGMdist) # Score cluster labels
        
        evaLinkage = cluster.AgglomerativeClustering(n_clusters=n).fit_predict(frameWntr) #Create cluster labels
        link_score = metrics.calinski_harabasz_score(frameWntr, evaLinkage) # Score cluster labels

        #Find best clustering method and take k-clusters
        if kmeans_score > best_score:
            best_score = kmeans_score
            eva = evaKMeans
            optimalK = n
        if gmm_score > best_score:
            best_score = gmm_score
            eva = evaGMdist
            optimalK = n
        if link_score > best_score:
            best_score = link_score
            eva = evaLinkage
            optimalK = n

    print('Heating season clustering complete... generating plot...')
    #Draw cluster plot
    fig, ax = plt.subplots(figsize=(12,10)) 
    ax.set_ylabel(r'Airflow control error (%)', fontsize=32)
    ax.set_xlabel(r'Indoor air temperature '+r'$(^{0}C)$', fontsize=32)
    ax.text(22.5, 10, 'OK', fontsize=25, ha='center')
    ax.text(16, 2, 'Cold', fontsize=25)
    ax.text(28, 2, 'Hot', fontsize=25)
    ax.text(21.5, 80, 'High flow', fontsize=25)
    ax.text(21.5,-80, 'Low flow', fontsize=25)
    ax.set_xlim(15,30)
    ax.set_ylim(-100,100)
    plt.xticks(np.arange(15, 31, 3))
    plt.yticks(np.arange(-100, 101, 20))
    ax.set_xticklabels(np.arange(15, 31, 3), fontsize=23)
    ax.set_yticklabels(np.arange(-100, 101, 20), fontsize=23)
    plt.tight_layout()
    
    #Pretty bad - red box
    rect = plt.Rectangle((15,-100), 15, 200, fc='r', alpha=0.1)
    ax.add_patch(rect)

    #Not so bad - yellow box
    rect = plt.Rectangle((18,-50), 9, 100, fc='yellow', ec='k', alpha = 0.1, lw=2)
    ax.add_patch(rect)

    #OK - green box
    rect = plt.Rectangle((20,-20), 5, 40, fc='lime', ec='k', alpha = 0.1, lw=2)
    ax.add_patch(rect)

    centerClust = pd.DataFrame(columns = ['Zones','Mean t_in','Mean q_Flo Error','Mean s_Rad'])
    for i in range(0,optimalK): #Extract zones identified in clustering solution per cluster and plot 
        
        x = tInWntr.to_frame().T.loc[:, eva==i].stack().mean() #Temp Bias
        y = (qFloWntrErr_mean.to_frame().T.loc[:, eva==i]*100).stack().mean() #Flow Bias
        z = sRadWntr_mean.to_frame().T.loc[:, eva==i].stack().mean() #Mean rad state
        centerClust = centerClust.append({'Zones':sum(eva==i),'Mean t_in':x,'Mean q_Flo Error':y,'Mean s_Rad':z},ignore_index=True) #cluster center
        if ((x>15) & (x<30) & (y>-100) &(y<100)):
            t = plt.text(x, y, 'C'+str(i+1), fontsize=25, color = 'w', ha = 'center', va= 'center')
            t.set_bbox(dict(facecolor='black', alpha=0.6, edgecolor='black'))
        t = plt.text(15.2, 99.5 - 7*(i+1), 'C'+str(i+1)+': '+str(sum(eva==i))+ ' zone(s)', fontsize=20, alpha=0.5)

    #Find samples in clusters
    cluster_map = pd.DataFrame()
    cluster_map['data_index'] = frameWntr.index.values
    cluster_map['cluster'] = eva

    cluster_samples = pd.DataFrame()
    for a in range(optimalK):
        samples = (cluster_map.data_index[cluster_map.cluster == a])
        cluster_samples = pd.concat([cluster_samples,samples], ignore_index=False, axis=1).rename(columns={'data_index':'C'+str(a+1)})

    heat_cluster_samples = cluster_samples.apply(lambda x: pd.Series(x.dropna().values))

    #Compute Winter Health index - count number of zones where the cluster falls beyond threshold.
    centerClust['Health Index'] = ''
    centerClust['Health Index'][0] = 1 - centerClust.loc[(centerClust['Mean t_in']>25) | (centerClust['Mean t_in']<20) | (centerClust['Mean q_Flo Error']>20) | (centerClust['Mean q_Flo Error']<-20), 'Zones'].sum()/centerClust['Zones'].sum()
    t = plt.text(15.2,-98,'Health Index=' + str(round(centerClust['Health Index'].iloc[0]*100,1))+'%', fontsize=25, alpha=0.5)

    plt.savefig(os.path.join(output_path,'zone_heat_season.png'),dpi=600)
    zoneWinterSummary = centerClust

    print('Extracting data for cooling season...')
    #Extract workhours in SUMMER (May-August)
    mask = ((tIn.index.hour>9)&(tIn.index.hour<17)) & (tIn.index.weekday<5) & ((tIn.index.month>4)|(tIn.index.month<9))
    tInSmr = tIn[mask].mean(axis=0)
    qFloSmr = qFlo[mask]
    qFloSpSmr = qFloSp[mask]

    qFloSmrErr = ((qFloSmr-qFloSpSmr)/qFloSpSmr) #Calculate airflow control error
    qFloSmrErr = qFloSmrErr.replace(np.nan, 0) #If NaN value, replace with zero (NaNs are a result of (qFloSmr-qFloSpSmr)/qFloSpSmr == 0/0, and thus is no airflow error)
    qFloSmrErr = qFloSmrErr.replace([np.inf, -np.inf], np.nan).dropna(axis=0) #Remove inf/-inf values (This is a result of qFloSpSmr == 0, and thus is inconclusive)
    qFloSmrErr_mean = qFloSmrErr.mean(axis=0) #Take the mean airflow control error per zone

    tInErrNrm = tInSmr / np.linalg.norm(tInSmr)
    qFloErrNrm = qFloSmrErr_mean / np.linalg.norm(qFloSmrErr_mean)

    frameSmr = pd.concat([tInErrNrm,qFloErrNrm],axis=1)
    
    best_score = 0
    print('Cluster zones for cooling season based on indoor air tmeperature setpoint error & airflow setpoint error...')
    for n in range(3,6): # loop through 3 to 5 clusters
        evaKMeans = cluster.KMeans(n_clusters=n,random_state=1).fit_predict(frameSmr) #Create cluster labels
        kmeans_score = metrics.calinski_harabasz_score(frameSmr, evaKMeans) # Score cluster labels

        evaGMdist = mixture.GaussianMixture(n_components=n,covariance_type='full').fit_predict(frameSmr)
        gmm_score = metrics.calinski_harabasz_score(frameSmr, evaGMdist)
        
        evaLinkage = cluster.AgglomerativeClustering(n_clusters=n).fit_predict(frameSmr)
        link_score = metrics.calinski_harabasz_score(frameSmr, evaLinkage)


        #Find best clustering method and take k-clusters
        if kmeans_score > best_score:
            best_score = kmeans_score
            eva = evaKMeans
            optimalK = n
        if gmm_score > best_score:
            best_score = gmm_score
            eva = evaGMdist
            optimalK = n
        if link_score > best_score:
            best_score = link_score
            eva = evaLinkage
            optimalK = n

    print('Cooling season clustering complete... generating plot...')
    #Draw cluster plot
    fig, ax = plt.subplots(figsize=(12,10))
    ax.set_ylabel(r'Airflow control error (%)', fontsize=32)
    ax.set_xlabel(r'Indoor air temperature '+r'$(^{0}C)$', fontsize=32)
    ax.text(22.5, 10, 'OK', fontsize=25, ha='center')
    ax.text(16, 2, 'Cold', fontsize=25)
    ax.text(28, 2, 'Hot', fontsize=25)
    ax.text(21.5, 80, 'High flow', fontsize=25)
    ax.text(21.5,-80, 'Low flow', fontsize=25)
    ax.set_xlim(15,30)
    ax.set_ylim(-100,100)
    plt.xticks(np.arange(15, 31, 3))
    plt.yticks(np.arange(-100, 101, 20))
    ax.set_xticklabels(np.arange(15, 31, 3), fontsize=23)
    ax.set_yticklabels(np.arange(-100, 101, 20), fontsize=23)
    plt.tight_layout()

    #Pretty bad - red box
    rect = plt.Rectangle((15,-100), 15, 200, fc='r', alpha=0.1)
    ax.add_patch(rect)

    #Not so bad - yellow box
    rect = plt.Rectangle((18,-50), 9, 100, fc='yellow', ec='k', alpha = 0.1, lw=2)
    ax.add_patch(rect)

    #OK - green box
    rect = plt.Rectangle((20,-20), 5, 40, fc='lime', ec='k', alpha = 0.1, lw=2)
    ax.add_patch(rect)

    centerClust = pd.DataFrame(columns = ['Zones','Mean t_in','Mean q_Flo Error'])
    for i in range(0,optimalK): #Extract zones identified in clustering solution per cluster and plot 
        
        x = tInSmr.to_frame().T.loc[:, eva==i].stack().mean() #Temp Bias
        y = (qFloSmrErr_mean.to_frame().T.loc[:, eva==i]*100).stack().mean() #Flow Bias
        centerClust = centerClust.append({'Zones':sum(eva==i),'Mean t_in':x,'Mean q_Flo Error':y},ignore_index=True) #cluster center
        if ((x>15) & (x<30) & (y>-100) &(y<100)):
            t = plt.text(x, y, 'C'+str(i+1), fontsize=25, color = 'w', ha = 'center', va= 'center')
            t.set_bbox(dict(facecolor='black', alpha=0.6, edgecolor='black'))
        t = plt.text(15.2, 99.5 - 7*(i+1), 'C'+str(i+1)+': '+str(sum(eva==i))+ ' zone(s)', fontsize=20, alpha=0.5)
    
    #Find samples in clusters
    cluster_map = pd.DataFrame()
    cluster_map['data_index'] = frameSmr.index.values
    cluster_map['cluster'] = eva

    cluster_samples = pd.DataFrame()
    for a in range(optimalK):
        samples = (cluster_map.data_index[cluster_map.cluster == a])
        cluster_samples = pd.concat([cluster_samples,samples], ignore_index=False, axis=1).rename(columns={'data_index':'C'+str(a+1)})

    cool_cluster_samples = cluster_samples.apply(lambda x: pd.Series(x.dropna().values))

    #Compute Summer Health index - count number of zones where the cluster falls beyond threshold.
    centerClust['Health Index'] = ''
    centerClust['Health Index'][0] = 1 - centerClust.loc[(centerClust['Mean t_in']>25) | (centerClust['Mean t_in']<20) | (centerClust['Mean q_Flo Error']>20) | (centerClust['Mean q_Flo Error']<-20), 'Zones'].sum()/centerClust['Zones'].sum()
    t = plt.text(15.2,-98,'Health Index=' + str(round(centerClust['Health Index'].iloc[0]*100,1))+'%', fontsize=25, alpha=0.5)

    plt.savefig(os.path.join(output_path,'zone_cool_season.png'),dpi=600)
    zoneSummerSummary = centerClust

    #Output the zone summary tables as excel files
    print('Formatting KPIs...')
    writer = pd.ExcelWriter(os.path.join(output_path,'zone_anomaly_summary.xlsx'), engine='xlsxwriter') # pylint: disable=abstract-class-instantiated
    zoneWinterSummary.to_excel(writer, sheet_name='Htg_summary')
    heat_cluster_samples.to_excel(writer, sheet_name='Htg_samples')
    zoneSummerSummary.to_excel(writer, sheet_name='Clg_summary')
    cool_cluster_samples.to_excel(writer,sheet_name='Clg_samples')
    writer.save()
    writer.close()

    return

def execute_function(input_path, output_path):

    #Read csv files in input path
    zone_files = os.listdir(input_path)
    zone_files_csv = [f for f in zone_files if f[-3:] == 'csv']
 
    #Create empty dataframes
    tIn = pd.DataFrame()
    qFlo = pd.DataFrame()
    qFloSp = pd.DataFrame()
    sRad = pd.DataFrame()

    print('Reading zone-level HVAC data files...')
    #Populate tIn,qFlo,qFloSp,and sRad dataframes
    for f in zone_files_csv:
        data = pd.read_csv(os.path.join(input_path,f), index_col=0)
        tIn = pd.concat([tIn,data[data.columns[0]]], axis=1,sort=False).rename(columns={data.columns[0]:str(f).replace('.csv','')})
        qFlo = pd.concat([qFlo,data[data.columns[1]]], axis=1,sort=False).rename(columns={data.columns[1]:str(f).replace('.csv','')})
        qFloSp = pd.concat([qFloSp,data[data.columns[2]]], axis=1,sort=False).rename(columns={data.columns[2]:str(f).replace('.csv','')})
        sRad = pd.concat([sRad,data[data.columns[3]]], axis=1,sort=False).rename(columns={data.columns[3]:str(f).replace('.csv','')})
    
    # extract start and end time from last read zone file
    print("Start time: "+str(min(data.index)),flush=True)
    print("End time: "+str(max(data.index)),flush=True)

    #Set index of all dataframes to datetime
    for df in [tIn,qFlo,qFloSp,sRad]:
        df.index = pd.to_datetime(df.index)

    print("Reading zone-level HVAC controls network data files successful!")
    print("Number of zones detected: " + str(len(tIn.columns)))

    #Run the zone anomaly analysis
    zoneAnomaly(tIn,qFlo,qFloSp,sRad,output_path)

    return





