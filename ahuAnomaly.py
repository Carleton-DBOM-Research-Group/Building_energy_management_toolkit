#Import required libraries
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn import linear_model, cluster,metrics,mixture
from sklearn.decomposition import PCA
from geneticalgorithm import geneticalgorithm as ga
from PIL import Image, ImageDraw, ImageFont


#Local function to draw multiple AHU diagrams as snapshots of operations
def drawAHU (ahu,clustCenter,oaSlope,oaBias,output_path): 

    for k in clustCenter.index:

        img = Image.new('RGB', (3600, 1200), (255, 255, 255))
        d = ImageDraw.Draw(img)

        # draw AHU ducts   
        d.line([(600,800),(3000,800)], fill ="black", width = 20)
        d.line([(600,600),(1200,600)], fill ="black", width = 20)
        d.line([(1200,600),(1200,250)], fill ="black", width = 20)
        d.line([(1500,600),(1500,250)], fill ="black", width = 20)
        d.line([(1500,600),(3000,600)], fill ="black", width = 20)

        # draw dampers
        d.line([(1250,550),(1450,400)], fill ="black", width = 12) # return damper
        d.line([(850,750),(950,650)], fill ="black", width = 12) # outdoor damper
        d.line([(900,475),(1350,475)], fill ="black", width = 8)
        d.line([(900,700),(900,475)], fill ="black", width = 8)

        # draw coils/fans
        d.rectangle((1800, 725, 2100, 875), fill=(225, 0, 0)) #heating coil
        d.rectangle((2200, 725, 2500, 875), fill=(0, 0, 225)) #cooling coil
        d.ellipse((2600, 725, 2900, 875), fill=(0, 0, 0)) #supply fan

        # draw arrows
        d.polygon([(600,700), (500, 750), (530,700), (500,650)], fill = 'black') # outdoor arrow
        d.polygon([(1350,250), (1300, 150), (1350,180), (1400,150)], fill = 'black') # return arrow
        d.polygon([(3270,700), (3170, 750), (3200,700), (3170,650)], fill = 'black') # supply arrow

        # Add text
        font = ImageFont.truetype("arial.ttf", 100)
        #font = ImageFont.load_default()
        d.text((1220, 40), "return", font=font, fill='black')
        d.text((1240, 260), str(clustCenter.iloc[k][clustCenter.columns[6]])+" C", font=font, fill='black')#tRa
        d.text((150, 640), "outdoor", font=font, fill='black')
        d.text((620, 640), str(clustCenter.iloc[k][clustCenter.columns[5]])+" C", font=font, fill='black')#tOa
        d.text((2875, 640), "supply", font=font, fill='black')
        d.text((3300, 640), str(clustCenter.iloc[k][clustCenter.columns[7]])+" C", font=font, fill='black')#tSa

        handle = min((((clustCenter.iloc[k][clustCenter.columns[4]]/100)+oaBias)*oaSlope),1)
        tMa = clustCenter.iloc[k][clustCenter.columns[5]]*handle + clustCenter.iloc[k][clustCenter.columns[6]]*(1-handle) #compute mixed air temperature

        d.text((1500, 640), str(int(round(tMa)))+" C", font=font, fill='black')
        d.text((1790, 860), "heating", font=font, fill='black')
        d.text((1880, 960), "coil", font=font, fill='black')
        d.text((1830, 750), str(clustCenter.iloc[k][clustCenter.columns[3]])+"%", font=font, fill='white')#heating coil
        d.text((2190, 860), "cooling", font=font, fill='black')
        d.text((2280, 960), "coil", font=font, fill='black')
        d.text((2230, 750), str(clustCenter.iloc[k][clustCenter.columns[1]])+"%", font=font, fill='white')#cooling coil
        d.text((2610, 860), "supply", font=font, fill='black')
        d.text((2680, 960), "fan", font=font, fill='black')
        d.text((2630, 750), str(clustCenter.iloc[k][clustCenter.columns[2]])+"%", font=font, fill='white')#supply fan
        d.text((1790, 200), "Fraction of time operation: " + str(clustCenter.iloc[k][clustCenter.columns[8]])+'%', font=font, fill='black')#duration of operation
        d.text((1550, 300), "Fraction with active perimeter heaters: " + str(clustCenter.iloc[k][clustCenter.columns[0]])+'%', font=font, fill='black')#perimeter heaters
        d.text((800,365), str(clustCenter.iloc[k][clustCenter.columns[4]])+'%', font=font, fill='black')#damper
    
        img.save(os.path.join(output_path,'f2b_ahu_' + str(ahu+1) + '_C_' + str(k+1) + '.png'))

    return

#Local function calculates KPIs and generates visualizations
def ahuAnomaly (all_ahu_data,sRad,tIn,output_path):
    
    def ahuModes(x): #Dimension = 5
        # x[0] sOa min setpoint
        # x[1] tOa changepoint for mode 1/mode 2
        # x[2] tOa changepoint for mode 2/mode 3
        # x[3] tOa changepoint for mode 3/mode 4
        # x[4] sOa max
        conditions = [tOa <= x[1], (tOa > x[1]) & (tOa <= x[2]), (tOa > x[2]) & (tOa <= x[3]), tOa > x[3]]
        choices = [x[0], (x[4]-x[0])*(tOa-x[1])/(x[2]-x[1]) + x[0], x[4], x[0]]
        sOaPred = np.select(conditions,choices,default=0)

        if ((x[1]>x[2])|(x[2]>x[3])):
            return 100*(np.sqrt(((sOa - sOaPred) ** 2).mean()))
        else:
            return np.sqrt(((sOa - sOaPred) ** 2).mean())
        
    def tSaMdl(x): #Dimension = 4
        # x[0] tSa setpoint for heating season
        # x[1] tSa setpoint for cooling season
        # x[2] tOa changepoint for heating season
        # x[3] tOa changepoint for cooling season
        conditions = [tOa <= x[2], (tOa > x[2]) & (tOa <= x[3]), tOa > x[3]]
        choices = [x[0], (x[0]-x[1])/(x[2]-x[3])*(tOa-x[2])+x[0], x[1]]
        tSaPred = np.select(conditions,choices,default=0)

        return np.sqrt(((tSa - tSaPred) ** 2).mean())
    
    def ahuMdlMode1_2(x): #Dimension = 3
        # x[0] outdoor air fraction bias
        # x[1] Delta temp across heating coil
        # x[2] Temp bias across ducts
        sOa_mode1_2 = sOa/100
        oaFrac = (sOa_mode1_2 + x[1]) * x[0]
        oaFrac[oaFrac>1] = 1
        tMa = tOa*oaFrac + tRa*(1-oaFrac)
        yp = tMa + sHc*x[1] + x[2]
        
        return np.sqrt(((tSa - yp) ** 2).mean())

    def ahuMdlMode4(x): #Dimension = 2
        # x[0] Delta temp across cooling coil
        # x[1] Temp bias across ducts
        sOa_mode4 = sOa/100
        oaFrac = (sOa_mode4 + ahuMdlMode1_2_Prmtr[1]) * ahuMdlMode1_2_Prmtr[0]
        oaFrac[oaFrac>1] = 1
        tMa = tOa*oaFrac + tRa*(1-oaFrac)
        yp = tMa + sCc*x[0] + x[1]
        
        return np.sqrt(((tSa - yp) ** 2).mean())

    sRad = sRad.mean(axis=1)
    tInCld = tIn.quantile(.05, axis=1)
    tInWrm = tIn.quantile(.95, axis=1)
    tInAvg = tIn.mean(axis=1)

    ahuMdl = pd.DataFrame()
    faults_df = pd.DataFrame()
    ahu_num = 0

    for i in all_ahu_data.index.unique():
        print("Analyzing data from AHU: " + str(i))
        data = all_ahu_data.loc[i] #Select only data from AHU i
        data = data.set_index(data.columns[0])

        #Drop rows with nan values
        mask = data[data.columns[0]].isna()
        data = data.drop(data[mask].index)
        sRad = sRad.drop(sRad[mask].index)
        tInCld = tInCld.drop(tInCld[mask].index)
        tInWrm = tInWrm.drop(tInWrm[mask].index)
        tInAvg = tInAvg.drop(tInAvg[mask].index)
        
        #Drop stagnant data
        mask = data.iloc[:,3].rolling(24).std() < 0.001
        dataNew = data.drop(data[mask].index)
        sRadAvg = sRad.drop(sRad[mask].index)
        tInCldNew = tInCld.drop(tInCld[mask].index)
        tInWrmNew = tInWrm.drop(tInWrm[mask].index)
        tInAvgNew = tInAvg.drop(tInAvg[mask].index)
        
        #Extract only workhours
        mask = ((dataNew.index.hour>8)&(dataNew.index.hour<17)) & (dataNew.index.weekday<5)
        dataWrkHrs = dataNew[mask]
        sRadAvgWrkHrs = sRadAvg[mask]
        tInCldWrkHrs = tInCldNew[mask]
        tInWrmWrkHrs = tInWrmNew[mask]
        tInAvgWrkHrs = tInAvgNew[mask]
        
        #Draw split range controller plot
        tOa = dataWrkHrs[dataWrkHrs.columns[2]]
        sOa = dataWrkHrs[dataWrkHrs.columns[4]]
        if max(sOa)<=1:
            sOa = sOa * 100
        tSa = dataWrkHrs[dataWrkHrs.columns[0]]

        #Optimize parameters for all genetic algorithms
        varbound = np.array([[0,100],[-20,30],[-20,30],[-20,30],[0,100]]) # ([lower_bound,upper_bound])
        algorithm_param = {'max_num_iteration': 4,\
                   'population_size':5000,\
                   'mutation_probability':0.1,\
                   'elit_ratio': 0.01,\
                   'crossover_probability': 0.7,\
                   'parents_portion': 0.3,\
                   'crossover_type':'uniform',\
                   'max_iteration_without_improv':10}
        
        model=ga(function=ahuModes,\
            dimension=5,\
            variable_type='real',\
            variable_boundaries=varbound,\
            algorithm_parameters=algorithm_param,
            convergence_curve = False)
            
        print('Estimating change-points for split-range controller diagram using GA... This will take a while...',flush=True)
        model.run() #run ahuModes
        cp = model.output_dict['variable']
        
        tOa_range = np.arange(-25.0,35.0,0.1)
        conditions = [tOa_range <= cp[1], (tOa_range > cp[1]) & (tOa_range <= cp[2]), (tOa_range > cp[2]) & (tOa_range <= cp[3]), tOa_range > cp[3]]
        choices = [cp[0], (100-cp[0])*(tOa_range-cp[1])/(cp[2]-cp[1]) + cp[0], 100, cp[0]]
        y = np.select(conditions,choices,default=0)

        #Optimize parameters for genetic algorithms for tSaMdl
        varbound = np.array([[12,20],[12,20],[-20,10],[10,20]]) # ([lower_bound,upper_bound])
        model=ga(function=tSaMdl,\
            dimension=4,\
            variable_type='real',\
            variable_boundaries=varbound,\
            algorithm_parameters=algorithm_param,
            convergence_curve = False) 
        
        print('Estimating change-points for supply air temperature using GA... This will take a while...',flush=True)
        model.run() #Run tSaMdl
        tSaPrmtr = model.output_dict['variable'] #Extract estimated parameters

        #Plot first subplot of f2a_ahu_
        print('Plotting warmest/coldest/average tIns and tSa...', flush=True)
        fig = plt.figure(figsize=(15,12))
        ax = plt.subplot(2,1,1)
        ax.set_xlabel(r'Outdoor air temperature '+r'$(^{0}C)$', fontsize=24)
        ax.set_ylabel(r'Air temperature '+r'$(^{0}C)$', fontsize=24)
        ax.set_xlim(-25,35)
        ax.set_ylim(10,30)
        ax.set_xticks(np.arange(-25,36,5))
        ax.set_yticks(np.arange(12,31,3))
        ax.set_xticklabels(np.arange(-25,36,5),fontsize=25)
        ax.set_yticklabels(np.arange(12,31,3),fontsize=25)

        a = np.linspace(-25,35,num=100)
        #Plot coldest zone temperature
        print('Plotting coldest zone temperature...', flush=True)
        p = np.polyfit(tOa,tInCldWrkHrs,2)
        ax.plot(a,np.polyval(p,a),'b-', linewidth=4, label=r'Coldest')
        #Plot average zone temperature
        print('Plotting average zone temperature...', flush=True)
        p = np.polyfit(tOa,tInAvgWrkHrs,2) #tIn,avg
        ax.plot(a,np.polyval(p,a),'k-', linewidth=4, label=r'Average')
        #Plot warmest zone temperature
        print('Plotting warmest zone temperature...', flush=True)
        p = np.polyfit(tOa,tInWrmWrkHrs,2) #tIn,Wrm
        ax.plot(a,np.polyval(p,a),'r-', linewidth=4, label=r'Warmest')

        #Estimate/plot supply air temperature as a function of outdoor air temperature using tSaPrmtr
        print('Plotting supply air temperature as a function of outdoor air temperature using tSaPrmtr...', flush=True)
        conditions = [a <= tSaPrmtr[2], (a > tSaPrmtr[2]) & (a <= tSaPrmtr[3]), a > tSaPrmtr[3]]
        choices = [tSaPrmtr[0], (tSaPrmtr[0]-tSaPrmtr[1])/(tSaPrmtr[2]-tSaPrmtr[3])*(a-tSaPrmtr[2])+tSaPrmtr[0], tSaPrmtr[1]]
        tSaPr = np.select(conditions,choices,default=0)
        ax.plot(a,tSaPr,'k--', linewidth=4, label=r'Supply')

        #Plot ideal low/high supply air temperature
        print('Plotting ideal low supply air temperature...', flush=True)
        x_handle = [-12,12]
        y_handle = [17,12]
        tSaIdealLow = np.interp(a,x_handle,y_handle)
        tSaIdealLow[tSaIdealLow < y_handle[1]] = y_handle[1]
        tSaIdealLow[tSaIdealLow > y_handle[0]] = y_handle[0]

        print('Plotting ideal high supply air temperature...', flush=True)
        x_handle = [-6,19]
        y_handle = [20,13]
        tSaIdealHigh = np.interp(a,x_handle,y_handle)
        tSaIdealHigh[tSaIdealHigh < y_handle[1]] = y_handle[1]
        tSaIdealHigh[tSaIdealHigh > y_handle[0]] = y_handle[0]
        
        print('Fill gap in between high/low ideal tSa', flush=True)
        ax.fill_between(a,tSaIdealLow,tSaIdealHigh,facecolor='green',alpha=0.3)
        ax.text(-8.5, 13, 'Ideal supply air temperature',weight='bold',fontsize=22,rotation=-13,color='green')
        ax.legend(ncol=4,loc='upper center',prop={"size":22})

        #Plot second subplot f2a_ahu_
        print('Plotting split-range controller diagram...', flush=True)
        ax = plt.subplot(2,1,2)
        ax.set_xlabel(r'Outdoor air temperature '+r'$(^{0}C)$', fontsize=24)
        ax.set_ylabel('Damper/Valve position (%)', fontsize=24)
        ax.set_xlim(-25,35)
        ax.set_ylim(0,100)
        ax.set_xticks(np.arange(-25,36,5))
        ax.set_yticks(np.arange(0,101,10))
        ax.set_xticklabels(np.arange(-25,36,5),fontsize=25)
        ax.set_yticklabels(np.arange(0,101,10),fontsize=25)

        print('Plotting sOa...', flush=True)
        ax.plot(tOa_range,y,'k-.',linewidth=4,label='OA')

        print('Plotting sHc...', flush=True)
        htgMdInd = tOa <= cp[1]
        sHcHtgMode = dataWrkHrs[dataWrkHrs.columns[5]][htgMdInd]
        tOaHtgMode = tOa[htgMdInd]
        x_train = np.select([tOaHtgMode < cp[1]],[cp[1]-tOaHtgMode],default=0)[np.newaxis].T
        mdl = linear_model.LinearRegression(fit_intercept=False).fit(x_train, sHcHtgMode)
        x_test = np.select([tOa_range < cp[1]],[cp[1]-tOa_range],default=0)[np.newaxis].T
        y = mdl.predict(x_test) #Note y is overwritten
        ax.plot(tOa_range,y,'r-',linewidth=4,label='HC')

        print('Plotting sCc...', flush=True)
        clgMdInd = tOa > cp[2]
        sCcClgMode = dataWrkHrs[dataWrkHrs.columns[6]][clgMdInd]
        tOaClgMode = tOa[clgMdInd]
        x_train = np.select([tOaClgMode > cp[2]],[cp[2]-tOaClgMode],default=0)[np.newaxis].T
        mdl = linear_model.LinearRegression(fit_intercept=False).fit(x_train, sCcClgMode)
        x_test = np.select([tOa_range > cp[2]],[cp[2]-tOa_range],default=0)[np.newaxis].T
        y = mdl.predict(x_test)
        ax.plot(tOa_range,y,'b:',linewidth=4,label='CC')

        print('Plotting sRad...', flush=True)
        htgEconMdInd = tOa < cp[2]
        sRadHtgEconMode = sRadAvgWrkHrs[htgEconMdInd]
        tOaHtgEconMode = tOa[htgEconMdInd]
        x_train = np.select([tOaHtgEconMode < cp[2]],[cp[2]-tOaHtgEconMode],default=0)[np.newaxis].T
        mdl = linear_model.LinearRegression().fit(x_train, sRadHtgEconMode)
        x_test = np.select([tOa_range < cp[2]],[cp[2]-tOa_range],default=0)[np.newaxis].T
        y = mdl.predict(x_test)
        y = np.where(tOa_range >= cp[2],0,y)
        y = np.where(y>100,100,y)
        y = np.where(y<0,0,y)
        ax.plot(tOa_range,y,'r--',linewidth=4,label='RAD')

        ax.axvspan(-25, cp[1], alpha=0.2, color='r')
        ax.axvspan(cp[1], cp[2], alpha=0.2, color='y')
        ax.axvspan(cp[2], cp[3], alpha=0.2, color='k')
        ax.axvspan(cp[3], 35, alpha=0.2, color='b')
        ax.legend(ncol=4,loc='lower center',prop={"size":25},bbox_to_anchor=(0.5,-0.4))

        plt.tight_layout()
        print('Saving plot...', flush=True)
        fig.savefig(os.path.join(output_path,'f2a_ahu_' + str(ahu_num+1) + '.png'),dpi=300)

        #MULTIPLE LINEAR REGRESSION to extract ahuMdl
        print('Extracting data points in htgEconMd', flush=True)
        tSa = dataWrkHrs[dataWrkHrs.columns[0]][htgEconMdInd] 
        tRa = dataWrkHrs[dataWrkHrs.columns[1]][htgEconMdInd] 
        tOa = dataWrkHrs[dataWrkHrs.columns[2]][htgEconMdInd] #Note: tOa is redefined here.
        sOa = dataWrkHrs[dataWrkHrs.columns[4]][htgEconMdInd] 
        sHc = dataWrkHrs[dataWrkHrs.columns[5]][htgEconMdInd] 

        #Optimize parameters for genetic algorithms for ahuMdlMode1_2
        varbound = np.array([[0.0,1.5],[-1,1],[0,0.5]]) # ([lower_bound,upper_bound])
        
        #Same parameters as tSaMdl
        model=ga(function=ahuMdlMode1_2,\
            dimension=3,\
            variable_type='real',\
            variable_boundaries=varbound,\
            algorithm_parameters=algorithm_param,
            convergence_curve = False)
        
        print('Estimating temperature biases across heating coil(s) using GA... This will take a while...',flush=True)
        model.run() #Run ahuMdlMode1_2
        ahuMdlMode1_2_Prmtr = model.output_dict['variable']
        
        clgMdInd = dataWrkHrs[dataWrkHrs.columns[2]] > cp[3]
        tSa = dataWrkHrs[dataWrkHrs.columns[0]][clgMdInd] 
        tRa = dataWrkHrs[dataWrkHrs.columns[1]][clgMdInd] 
        tOa = dataWrkHrs[dataWrkHrs.columns[2]][clgMdInd] #Note: tOa is redefined here.
        sOa = dataWrkHrs[dataWrkHrs.columns[4]][clgMdInd] 
        sCc = dataWrkHrs[dataWrkHrs.columns[6]][clgMdInd] 

        #Optimize parameters for genetic algorithms for ahuMdlMode4
        varbound = np.array([[-0.5,0],[-1,1]]) # ([lower_bound,upper_bound])
        
        #Same parameters as tSaMdl and ahuMdlMode1_2
        model=ga(function=ahuMdlMode4,\
            dimension=2,\
            variable_type='real',\
            variable_boundaries=varbound,\
            algorithm_parameters=algorithm_param,
            convergence_curve = False)
        
        print('Estimating temperature biases across cooling coil(s) using GA... This will take a while...',flush=True)
        model.run() #Run ahuMdlMode4
        ahuMdlMode4_Prmtr = model.output_dict['variable']

        #Save variables from ahuMdlMode1_2 and ahuMdlMode4 in ahuMdl Dataframe
        ahuMdl = ahuMdl.append({'oaFrac':ahuMdlMode1_2_Prmtr[0],'dtHc':ahuMdlMode1_2_Prmtr[1]*100, 'dtCc':ahuMdlMode4_Prmtr[0]*100}, ignore_index=True)
        
        #Cluster operations into groups and snapshot operation
        print('Clustering operations...')
        ahuOperationDuration = sum(dataNew[dataNew.columns[7]]>0)/len(dataNew.index)*168
        mask = dataNew.iloc[:,7] > 0
        clusterFrame = pd.DataFrame()
        clusterFrame = pd.concat([dataNew[mask][dataNew.columns[0:3]], dataNew[mask][dataNew.columns[4:8]], sRadAvg[mask]], axis=1, sort=False)
        
        normData = clusterFrame / np.linalg.norm(clusterFrame)
        pca = PCA()
        pca.fit(normData)
        scores_array = pca.fit_transform(normData)
        scores = pd.DataFrame(data=scores_array)
        explained = pca.explained_variance_ratio_
        features = scores[scores.columns[0:1+min(min(np.where(np.cumsum(explained)>0.95)))]]

        best_score = 0
        for n in range(4,7): # loop through 4 to 6 clusters
            evaKMeans = cluster.KMeans(n_clusters=n,random_state=1).fit_predict(features) #Create cluster labels
            kmeans_score = metrics.calinski_harabasz_score(features, evaKMeans) # Score cluster labels

            evaGMdist = mixture.GaussianMixture(n_components=n,covariance_type='full').fit_predict(features)
            gmm_score = metrics.calinski_harabasz_score(features, evaGMdist)
        
            evaLinkage = cluster.AgglomerativeClustering(n_clusters=n).fit_predict(features)
            link_score = metrics.calinski_harabasz_score(features, evaLinkage)

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

        clusterCenter = pd.DataFrame()
        clusterSize = []
        
        for j in range (0,optimalK):
            clusterCenter = clusterCenter.append((round(clusterFrame[eva==j].median(axis=0))), ignore_index=True)
            clusterSize.append(round(sum(eva==j)/len(eva),2)*100)
        
        clusterCenter['size'] = clusterSize # Merge clusterSize with clusterCenter change
        clusterCenter = clusterCenter.sort_values(by=clusterCenter.columns[5]).astype('int64') #sort by ascending tOa

        print('Creating simplified AHU diagram of clusters...')
        drawAHU(ahu_num,clusterCenter,ahuMdlMode1_2_Prmtr[0],ahuMdlMode1_2_Prmtr[1],output_path) # Pass to function to draw AHUs


        #COMPUTE FAULTS
        print('Computing faults...')
        ahuHealthInd = 0
        if ahuMdlMode1_2_Prmtr[0] < 0.3:
            sOa_fault = 'Low outdoor air'
        elif ahuMdlMode1_2_Prmtr[0] > 1.3:
            sOa_fault = 'High outdoor air'
        else:
            sOa_fault = 'Normal'
            ahuHealthInd += 100/6
        
        if ahuMdlMode1_2_Prmtr[2]*100 < 1.0:
            sHc_fault = 'Stuck'
        else:
            sHc_fault = 'Normal'
            ahuHealthInd += 100/6
        
        if ahuMdlMode4_Prmtr[0]*100 > -1.0:
            sCc_fault = 'Stuck'
        else:
            sCc_fault = 'Normal'
            ahuHealthInd += 100/6
        
        fracRadOnEconomizer = sRadAvgWrkHrs[((dataWrkHrs[dataWrkHrs.columns[2]] > cp[1]) | (dataWrkHrs[dataWrkHrs.columns[2]] < cp[2]))].mean()
        tInWrmEcon = tInWrmWrkHrs[((dataWrkHrs[dataWrkHrs.columns[2]] > cp[1]) | (dataWrkHrs[dataWrkHrs.columns[2]] < cp[2]))].mean() #Check for overheating
        
        if (fracRadOnEconomizer > 50) & (tInWrmEcon < 24):
            tSaReset_fault = 'Check supply air temperature reset logic'
        else:
            tSaReset_fault = 'Normal'
            ahuHealthInd += 100/6
        
        if ahuOperationDuration > 100:
            modeOfOperation_fault = 'Check mode of operation logic'
        else:
            modeOfOperation_fault = 'Normal'
            ahuHealthInd += 100/6
        
        if (cp[4] < 90) or (cp[3] < 15) or (cp[0] > 90):
            economizer_fault = 'Check economizer logic'
        else:
            economizer_fault = 'Normal'
            ahuHealthInd += 100/6
        
        #Save faults in faults_df
        faults_df = faults_df.append({'AHU':str(i),'Outdoor Air Damper':sOa_fault,'Heating Coil':sHc_fault,'Cooling coil':sCc_fault,'Supply air temperature':tSaReset_fault,'Schedule':modeOfOperation_fault,'Economizer':economizer_fault,'AHU Health Index (%)':int(ahuHealthInd)}, ignore_index=True)

        ahu_num += 1 #Plus 1 ahu_num per AHU loop

    return ahuMdl,faults_df


def execute_function(input_path, output_path):

    #Reading AHU data
    print("Reading AHU-level HVAC controls network data files...")
    ahu_files = os.listdir(os.path.join(input_path,'ahu'))
    ahu_files_csv = [f for f in ahu_files if f[-3:] == 'csv']
    dfs = []
    for f in ahu_files_csv:
        data = pd.read_csv(os.path.join(input_path,'ahu',f))
        data = data.rename(columns={data.columns[1]:'tSa',data.columns[2]:'tRa',data.columns[3]:'tOa',data.columns[4]:'pSa',data.columns[5]:'sOa',data.columns[6]:'sHc',data.columns[7]:'sCc',data.columns[8]:'sFan'})
        dfs.append(data)
    ahu = pd.concat(dfs,keys=ahu_files_csv).reset_index(level=1, drop=True)
    ahu[ahu.columns[0]] = pd.to_datetime(ahu[ahu.columns[0]])
    print("AHU-level HVAC controls network data files read successful!")
    print("Number of AHUs detected: " + str(len(dfs)))

    
    #Reading zone data
    print("Reading zone-level HVAC controls network data files...")
    zone_files = os.listdir(os.path.join(input_path,'zone'))
    zone_files_csv = [f for f in zone_files if f[-3:] == 'csv']
    tIn = pd.DataFrame()
    sRad = pd.DataFrame()
    for f in zone_files_csv:
        data = pd.read_csv(os.path.join(input_path,'zone',f), index_col=0) #Specify the sample data and sheet name for zones
        data = data.rename(columns={data.columns[0]:'tIn',data.columns[1]:'qFlo',data.columns[2]:'qFloSp',data.columns[3]:'sRad'})
        tIn = pd.concat([tIn,data[data.columns[0]]], axis=1,sort=False).rename(columns={data.columns[0]:str(f).replace('.csv','')})
        sRad = pd.concat([sRad,data[data.columns[3]]], axis=1,sort=False).rename(columns={data.columns[3]:str(f).replace('.csv','')})
    for df in [tIn,sRad]:
        df.index = pd.to_datetime(df.index)
    print("Zone-level HVAC controls network data read successful!")
    print("Number of zones detected: " + str(len(tIn.columns)))

    #Analyze the data and generate KPIs and visuals
    ahuMdl, faults = ahuAnomaly(ahu,sRad,tIn,output_path) #Call ahuAnomaly local function, generate KPIs and visualizations

    #Output KPIs in excel spreadsheet
    writer = pd.ExcelWriter(os.path.join(output_path,'ahu_anomaly_summary.xlsx'), engine='xlsxwriter') # pylint: disable=abstract-class-instantiated
    ahuMdl.to_excel(writer, sheet_name='ahuMdl')
    faults.to_excel(writer, sheet_name='faults')
    writer.save()
    writer.close()

    return

