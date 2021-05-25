#Import required modules
import pandas as pd
import numpy as np
import editdistance as ed
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
import time

#AHU tag Dictionary
tSaTagInc = ["tsa","sat"]
tSaTagExc = ['sp','stp','set','co','vv','vav','bf','lw','bv','rm']
tRaTagInc = ['tra','rat']
tRaTagExc = ['sp','stp','set','co','vv','vav','bf','lw','bv','rm','ew']
tOaTagInc = ['toa','oat']
tOaTagExc = ['cold','low','high','average','sp','stp','set']
pSaTagInc = ['psa','psa']
pSaTagExc = ['sp','stp','set']
sOaTagInc = ['dmfa','fad','oad','mad']
sOaTagExc = ['sp','stp','set','min pos','load']
sHcTagInc = ['rhc','hv','hcv']
sHcTagExc = ['sp','stp','set','vav','rm','vv']
sCcTagInc = ['rcc','cv','ccv']
sCcTagExc = ['sp','stp','set','vav','rm','vv']
sFanTagInc = ['sf','vsd','vfd']
sFanTagExc = ['sp','stp','set','vav','rm','vv','power','voltage','current','frequency','kwh','bv']
tSaSpTagInc = ['sat sp','tsa sp']
tSaSpTagExc = ['bv','vav','rm','vv','test']
pSaSpTagInc = ['psa sp','sasp sp']
pSaSpTagExc = ['bv','vav','rm','vv','test']

#Zone tag Dictionary
zoneIdentifier = ['rm','vv','vav']
tInTagInc = ['tst','rmt']
tInTagExc = ['sp','avg','co','average']
qFloTagInc = ['flow']
qFloTagExc = ['sp','rad','tot','desired']
qFloSpTagInc = ['flow sp','desired airflow']
qFloSpTagExc = ['avg']
sRadTagInc = ['rrh','rrp','rad']
sRadTagExc = ['flow sp','flow']

def searchAHUTags (tSaTagInc,tSaTagExc,tRaTagInc,tRaTagExc,tOaTagInc,tOaTagExc,
                   pSaTagInc,pSaTagExc,sOaTagInc,sOaTagExc,sHcTagInc,sHcTagExc,
                   sCcTagInc,sCcTagExc,sFanTagInc,sFanTagExc,tSaSpTagInc,tSaSpTagExc,
                   pSaSpTagInc,pSaSpTagExc,tag):
                   
    # Set diff function to return list of index in l1 that are NOT in l2
    def diff(l1,l2):
        return (list(set(l1) - set(l2)))
    
    tag['TL Name'] = tag['TL Name'].str.lower()
    tag['TL Name'] = tag['TL Name'].str.replace('tl','')
    tag['TL Name'] = tag['TL Name'].str.replace('_',' ')
    tag['TL Name'] = tag['TL Name'].str.replace('-',' ')
    tag['TL Name'] = tag['TL Name'].str.replace('/',' ')

    #CLASSIFY
    print('Classifying AHU-level metadata labels by tags...')
    #tsa
    indInc = tag.index[tag['TL Name'].str.contains('|'.join(tSaTagInc),case=False)].tolist()
    indExc = tag.index[tag['TL Name'].str.contains('|'.join(tSaTagExc),case=False)].tolist()
    
    ind = diff(indInc,indExc)
    
    tSa = tag[{'TL Name','TL Reference'}].iloc[ind].reset_index().rename(columns={'index':'TL'})

    #tRa
    indInc.clear()
    indExc.clear()
    indInc = tag.index[tag['TL Name'].str.contains('|'.join(tRaTagInc),case=False)].tolist()
    indExc = tag.index[tag['TL Name'].str.contains('|'.join(tRaTagExc),case=False)].tolist()
    
    ind = diff(indInc,indExc)
    
    tRa = tag[{'TL Name','TL Reference'}].iloc[ind].reset_index().rename(columns={'index':'TL'})

    #tOa
    indInc.clear()
    indExc.clear()
    indInc = tag.index[tag['TL Name'].str.contains('|'.join(tOaTagInc),case=False)].tolist()
    indExc = tag.index[tag['TL Name'].str.contains('|'.join(tOaTagExc),case=False)].tolist()
    
    ind = diff(indInc,indExc)
    
    tOa = tag[{'TL Name','TL Reference'}].iloc[ind].reset_index().rename(columns={'index':'TL'})

    #pSa
    indInc.clear()
    indExc.clear()
    indInc = tag.index[tag['TL Name'].str.contains('|'.join(pSaTagInc),case=False)].tolist()
    indExc = tag.index[tag['TL Name'].str.contains('|'.join(pSaTagExc),case=False)].tolist()
    
    ind = diff(indInc,indExc)
    
    pSa = tag[{'TL Name','TL Reference'}].iloc[ind].reset_index().rename(columns={'index':'TL'})

    #sOa
    indInc.clear()
    indExc.clear()
    indInc = tag.index[tag['TL Name'].str.contains('|'.join(sOaTagInc),case=False)].tolist()
    indExc = tag.index[tag['TL Name'].str.contains('|'.join(sOaTagExc),case=False)].tolist()
    
    ind = diff(indInc,indExc)
    
    sOa = tag[{'TL Name','TL Reference'}].iloc[ind].reset_index().rename(columns={'index':'TL'})

    #sHc
    indInc.clear()
    indExc.clear()
    indInc = tag.index[tag['TL Name'].str.contains('|'.join(sHcTagInc),case=False)].tolist()
    indExc = tag.index[tag['TL Name'].str.contains('|'.join(sHcTagExc),case=False)].tolist()
    
    ind = diff(indInc,indExc)
    
    sHc = tag[{'TL Name','TL Reference'}].iloc[ind].reset_index().rename(columns={'index':'TL'})

    #sCc
    indInc.clear()
    indExc.clear()
    indInc = tag.index[tag['TL Name'].str.contains('|'.join(sCcTagInc),case=False)].tolist()
    indExc = tag.index[tag['TL Name'].str.contains('|'.join(sCcTagExc),case=False)].tolist()
    
    ind = diff(indInc,indExc)
    
    sCc = tag[{'TL Name','TL Reference'}].iloc[ind].reset_index().rename(columns={'index':'TL'})

    #sFan
    indInc.clear()
    indExc.clear()
    indInc = tag.index[tag['TL Name'].str.contains('|'.join(sFanTagInc),case=False)].tolist()
    indExc = tag.index[tag['TL Name'].str.contains('|'.join(sFanTagExc),case=False)].tolist()
    
    ind = diff(indInc,indExc)
    
    sFan = tag[{'TL Name','TL Reference'}].iloc[ind].reset_index().rename(columns={'index':'TL'})

    #tSaSp
    indInc.clear()
    indExc.clear()
    indInc = tag.index[tag['TL Name'].str.contains('|'.join(tSaSpTagInc),case=False)].tolist()
    indExc = tag.index[tag['TL Name'].str.contains('|'.join(tSaSpTagExc),case=False)].tolist()
    
    ind = diff(indInc,indExc)
    
    tSaSp = tag[{'TL Name','TL Reference'}].iloc[ind].reset_index().rename(columns={'index':'TL'})

    #pSaSp
    indInc.clear()
    indExc.clear()
    indInc = tag.index[tag['TL Name'].str.contains('|'.join(pSaSpTagInc),case=False)].tolist()
    indExc = tag.index[tag['TL Name'].str.contains('|'.join(pSaSpTagExc),case=False)].tolist()
    
    ind = diff(indInc,indExc)
    
    pSaSp = tag[{'TL Name','TL Reference'}].iloc[ind].reset_index().rename(columns={'index':'TL'})


    #ASSOCIATE and ORGANIZE
    print('Associate AHU-level labels by name or address using Levenschtein distance...')
    ahu_df = pd.DataFrame(columns=['tSaTag','tSaID','tRaTag','tRaID','tOaTag','tOaID','pSaTag','pSaID','sOaTag','sOaID','sHcTag','sHcID','sCcTag','sCcID','sFanTag','sFanID','tSaSpTag','tSaSpID','pSaSpTag','pSaSpID'])

    print('Number of identified AHUs (Assuming one cooling coil sensor per AHU): ' + str(len(sCc)))
    for i in sCc.index: #Assume one sCc (cooling coil sensor) per AHU
        print('Associating labels in AHU ' + str(i+1))
        #sCc
        ahu_df = ahu_df.append({'sCcTag':sCc.iloc[i]['TL Name'],'sCcID':sCc.iloc[i]['TL Reference']},ignore_index=True)

        #tSa
        d = pd.DataFrame(columns=['d_Name','d_ID'],dtype=int)
        for j in tSa.index:
            d = d.append({'d_Name':ed.eval(str(sCc.iloc[i]['TL Name']),str(tSa.iloc[j]['TL Name'])),
            'd_ID':ed.eval(str(sCc.iloc[i]['TL Reference']),str(tSa.iloc[j]['TL Reference']))}, ignore_index=True)
        if d['d_Name'].min() < 5:
            ind = d['d_Name'].idxmin()
            ahu_df['tSaTag'][i] = tSa.iloc[ind]['TL Name']
            ahu_df['tSaID'][i] = tSa.iloc[ind]['TL Reference']
        elif d['d_ID'].min() < 2:
            ind = d['d_ID'].idxmin()
            ahu_df['tSaTag'][i] = tSa.iloc[ind]['TL Name']
            ahu_df['tSaID'][i] = tSa.iloc[ind]['TL Reference']

        #tRa
        d = pd.DataFrame(columns=['d_Name','d_ID'],dtype=int)
        for j in tRa.index:
            d = d.append({'d_Name':ed.eval(str(sCc.iloc[i]['TL Name']),str(tRa.iloc[j]['TL Name'])),
            'd_ID':ed.eval(str(sCc.iloc[i]['TL Reference']),str(tRa.iloc[j]['TL Reference']))}, ignore_index=True)
        if d['d_Name'].min() < 5:
            ind = d['d_Name'].idxmin()
            ahu_df['tRaTag'][i] = tRa.iloc[ind]['TL Name']
            ahu_df['tRaID'][i] = tRa.iloc[ind]['TL Reference']
        elif d['d_ID'].min() < 2:
            ind = d['d_ID'].idxmin()
            ahu_df['tRaTag'][i] = tRa.iloc[ind]['TL Name']
            ahu_df['tRaID'][i] = tRa.iloc[ind]['TL Reference']

        #tOa
        d = pd.DataFrame(columns=['d_Name','d_ID'],dtype=int)
        for j in tOa.index:
            d = d.append({'d_Name':ed.eval(str(sCc.iloc[i]['TL Name']),str(tOa.iloc[j]['TL Name']))}, ignore_index=True)
        ind = d['d_Name'].idxmin()
        ahu_df['tOaTag'][i] = tOa.iloc[ind]['TL Name']
        ahu_df['tOaID'][i] = tOa.iloc[ind]['TL Reference']

        #pSa
        d = pd.DataFrame(columns=['d_Name','d_ID'],dtype=int)
        for j in pSa.index:
            d = d.append({'d_Name':ed.eval(str(sCc.iloc[i]['TL Name']),str(pSa.iloc[j]['TL Name'])),
            'd_ID':ed.eval(str(sCc.iloc[i]['TL Reference']),str(pSa.iloc[j]['TL Reference']))}, ignore_index=True)
        if d['d_Name'].min() < 5:
            ind = d['d_Name'].idxmin()
            ahu_df['pSaTag'][i] = pSa.iloc[ind]['TL Name']
            ahu_df['pSaID'][i] = pSa.iloc[ind]['TL Reference']
        elif d['d_ID'].min() < 2:
            ind = d['d_ID'].idxmin()
            ahu_df['pSaTag'][i] = pSa.iloc[ind]['TL Name']
            ahu_df['pSaID'][i] = pSa.iloc[ind]['TL Reference']
        

        #sOa
        d = pd.DataFrame(columns=['d_Name','d_ID'],dtype=int)
        for j in sOa.index:
            d = d.append({'d_Name':ed.eval(str(sCc.iloc[i]['TL Name']),str(sOa.iloc[j]['TL Name'])),
            'd_ID':ed.eval(str(sCc.iloc[i]['TL Reference']),str(sOa.iloc[j]['TL Reference']))}, ignore_index=True)
        if d['d_Name'].min() < 5:
            ind = d['d_Name'].idxmin()
            ahu_df['sOaTag'][i] = sOa.iloc[ind]['TL Name']
            ahu_df['sOaID'][i] = sOa.iloc[ind]['TL Reference']
        elif d['d_ID'].min() < 2:
            ind = d['d_ID'].idxmin()
            ahu_df['sOaTag'][i] = sOa.iloc[ind]['TL Name']
            ahu_df['sOaID'][i] = sOa.iloc[ind]['TL Reference']

        #sHc
        d = pd.DataFrame(columns=['d_Name','d_ID'],dtype=int)
        for j in sHc.index:
            d = d.append({'d_Name':ed.eval(str(sCc.iloc[i]['TL Name']),str(sHc.iloc[j]['TL Name'])),
            'd_ID':ed.eval(str(sCc.iloc[i]['TL Reference']),str(sHc.iloc[j]['TL Reference']))}, ignore_index=True)
        if d['d_Name'].min() < 5:
            ind = d['d_Name'].idxmin()
            ahu_df['sHcTag'][i] = sHc.iloc[ind]['TL Name']
            ahu_df['sHcID'][i] = sHc.iloc[ind]['TL Reference']
        elif d['d_ID'].min() < 2:
            ind = d['d_ID'].idxmin()
            ahu_df['sHcTag'][i] = sHc.iloc[ind]['TL Name']
            ahu_df['sHcID'][i] = sHc.iloc[ind]['TL Reference']

        #sFan
        d = pd.DataFrame(columns=['d_Name','d_ID'],dtype=int)
        for j in sFan.index:
            d = d.append({'d_Name':ed.eval(str(sCc.iloc[i]['TL Name']),str(sFan.iloc[j]['TL Name'])),
            'd_ID':ed.eval(str(sCc.iloc[i]['TL Reference']),str(sFan.iloc[j]['TL Reference']))}, ignore_index=True)
        if d['d_Name'].min() < 5:
            ind = d['d_Name'].idxmin()
            ahu_df['sFanTag'][i] = sFan.iloc[ind]['TL Name']
            ahu_df['sFanID'][i] = sFan.iloc[ind]['TL Reference']
        elif d['d_ID'].min() < 2:
            ind = d['d_ID'].idxmin()
            ahu_df['sFanTag'][i] = sFan.iloc[ind]['TL Name']
            ahu_df['sFanID'][i] = sFan.iloc[ind]['TL Reference']

        #tSaSp
        d = pd.DataFrame(columns=['d_Name','d_ID'],dtype=int)
        for j in tSaSp.index:
            d = d.append({'d_Name':ed.eval(str(sCc.iloc[i]['TL Name']),str(tSaSp.iloc[j]['TL Name'])),
            'd_ID':ed.eval(str(sCc.iloc[i]['TL Reference']),str(tSaSp.iloc[j]['TL Reference']))}, ignore_index=True)
        if d['d_Name'].min() < 5:
            ind = d['d_Name'].idxmin()
            ahu_df['tSaSpTag'][i] = tSaSp.iloc[ind]['TL Name']
            ahu_df['tSaSpID'][i] = tSaSp.iloc[ind]['TL Reference']
        elif d['d_ID'].min() < 2:
            ind = d['d_ID'].idxmin()
            ahu_df['tSaSpTag'][i] = tSaSp.iloc[ind]['TL Name']
            ahu_df['tSaSpID'][i] = tSaSp.iloc[ind]['TL Reference']

        #pSaSp
        d = pd.DataFrame(columns=['d_Name','d_ID'],dtype=int)
        for j in pSaSp.index:
            d = d.append({'d_Name':ed.eval(str(sCc.iloc[i]['TL Name']),str(pSaSp.iloc[j]['TL Name'])),
            'd_ID':ed.eval(str(sCc.iloc[i]['TL Reference']),str(pSaSp.iloc[j]['TL Reference']))}, ignore_index=True)
        if d['d_Name'].min() < 5:
            ind = d['d_Name'].idxmin()
            ahu_df['pSaSpTag'][i] = pSaSp.iloc[ind]['TL Name']
            ahu_df['pSaSpID'][i] = pSaSp.iloc[ind]['TL Reference']
        elif d['d_ID'].min() < 3:
            ind = d['d_ID'].idxmin()
            ahu_df['pSaSpTag'][i] = pSaSp.iloc[ind]['TL Name']
            ahu_df['pSaSpID'][i] = pSaSp.iloc[ind]['TL Reference']           

    return ahu_df


def levenshtein (s, t):
    #https://www.python-course.eu/levenshtein_distance.php - Edited by Andre Markus
    #Edit Distance but numerical changes cost 4, letter changes cost 1.

    rows = len(s)+1
    cols = len(t)+1
    
    dist = [[0 for x in range(cols)] for x in range(rows)]

    #Delete Costs
    for row in range(1, rows):
        if s[row-1].isdigit():
            dist[row][0] = row * 4
        else:
            dist[row][0] = row * 1

    #Insert Costs
    for col in range(1, cols):
        if t[col-1].isdigit():
            dist[0][col] = col * 4
        else:
            dist[0][col] = col * 1
    
    #Substitution Costs
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                sub_cost = 0
            elif ((s[row-1] != t[col-1])&((s[row-1].isdigit())|(t[col-1].isdigit()))): #Chars do not equal AND one of the two chars are numbers
                sub_cost = 4
            else:
                sub_cost = 1 #Chars do not equal, both are either letters or numbers

            if ((s[row-1].isdigit()) | (t[col-1].isdigit())):
                del_cost = 4
                ins_cost = 4
            else:
                del_cost = 1
                ins_cost = 1

            dist[row][col] = min(dist[row-1][col] + del_cost,
                                 dist[row][col-1] + ins_cost,
                                 dist[row-1][col-1] + sub_cost)

    return dist[row][col]

def searchZoneTags (zoneIdentifier,tInTagInc,tInTagExc,qFloTagInc,qFloTagExc,qFloSpTagInc,qFloSpTagExc,sRadTagInc,sRadTagExc,tag):

    # Set diff function to return list of index in l1 that are NOT in l2
    def diff(l1,l2):
        return (list(set(l1) - set(l2)))

    tag['TL Name'] = tag['TL Name'].str.lower()
    tag['TL Name'] = tag['TL Name'].str.replace('tl','')
    tag['TL Name'] = tag['TL Name'].str.replace('_',' ')
    tag['TL Name'] = tag['TL Name'].str.replace('-',' ')
    tag['TL Name'] = tag['TL Name'].str.replace('/',' ')

    #CLASSIFY
    print('Classify zone-level metadata labels...')
    #zone
    indZone = tag.index[tag['TL Name'].str.contains('|'.join(zoneIdentifier),case=False)].tolist()
    
    #tIn
    indInc = tag.index[tag['TL Name'].str.contains('|'.join(tInTagInc),case=False)].tolist()
    indInc = set(indZone) & set(indInc)
    indExc = tag.index[tag['TL Name'].str.contains('|'.join(tInTagExc),case=False)].tolist()
    
    ind = diff(indInc,indExc)
    
    tIn = tag[{'TL Name','TL Reference'}].iloc[ind].reset_index().rename(columns={'index':'TL'})

    #qFlo
    indInc.clear()
    indExc.clear()
    indInc = tag.index[tag['TL Name'].str.contains('|'.join(qFloTagInc),case=False)].tolist()
    indInc = set(indZone) & set(indInc)
    indExc = tag.index[tag['TL Name'].str.contains('|'.join(qFloTagExc),case=False)].tolist()
    
    ind = diff(indInc,indExc)
    
    qFlo = tag[{'TL Name','TL Reference'}].iloc[ind].reset_index().rename(columns={'index':'TL'})

    #qFloSp
    indInc.clear()
    indExc.clear()
    indInc = tag.index[tag['TL Name'].str.contains('|'.join(qFloSpTagInc),case=False)].tolist()
    indInc = set(indZone) & set(indInc)
    indExc = tag.index[tag['TL Name'].str.contains('|'.join(qFloSpTagExc),case=False)].tolist()
    
    ind = diff(indInc,indExc)
    
    qFloSp = tag[{'TL Name','TL Reference'}].iloc[ind].reset_index().rename(columns={'index':'TL'})

    #sRad
    indInc.clear()
    indExc.clear()
    indInc = tag.index[tag['TL Name'].str.contains('|'.join(sRadTagInc),case=False)].tolist()
    indInc = set(indZone) & set(indInc)
    indExc = tag.index[tag['TL Name'].str.contains('|'.join(sRadTagExc),case=False)].tolist()
    
    ind = diff(indInc,indExc)
    
    sRad = tag[{'TL Name','TL Reference'}].iloc[ind].reset_index().rename(columns={'index':'TL'})

    
    # ASSOCIATE AND ORGANIZE
    print('Associate zone-level labels by name or address using modified Levenschtein distance (This will take a while)...')
    zone_df = pd.DataFrame(columns=['tInTag','tInID','qFloTag','qFloID','qFloSpTag','qFloSpID','sRadTag','sRadID'])

    print('Number of identified VAV terminals (Assuming one airflow rate sensor per VAV terminal): ' + str(len(qFlo)))
    for i in qFlo.index:#Assume one qFlo (Airflow rate) sensor per zone
        print('Associating labels in VAV terminal ' + str(i+1))
        #qFlo
        zone_df = zone_df.append({'qFloTag':qFlo.iloc[i]['TL Name'],'qFloID':qFlo.iloc[i]['TL Reference']},ignore_index=True)
        handle1 = qFlo.iloc[i]['TL Reference'].split('TL')
        
        #tIn
        d = pd.DataFrame(columns=['d_Name','d_ID'],dtype=int)
        for j in tIn.index:
            handle2 = tIn.iloc[j]['TL Reference'].split('TL')
            if handle1[0] == handle2[0]:
                d = d.append({'d_Name':levenshtein(str(qFlo.iloc[i]['TL Name']),str(tIn.iloc[j]['TL Name'])),'d_ID':abs(int(handle1[1])-int(handle2[1]))},ignore_index=True)
            else:
                d = d.append({'d_Name':levenshtein(str(qFlo.iloc[i]['TL Name']),str(tIn.iloc[j]['TL Name'])),'d_ID':10000},ignore_index=True)
        if d['d_Name'].min() < 10:
            ind = d['d_Name'].idxmin()
            zone_df['tInTag'][i] = tIn.iloc[ind]['TL Name']
            zone_df['tInID'][i] = tIn.iloc[ind]['TL Reference']
        elif d['d_ID'].min() < 30:
            ind = d['d_ID'].idxmin()
            zone_df['tInTag'][i] = tIn.iloc[ind]['TL Name']
            zone_df['tInID'][i] = tIn.iloc[ind]['TL Reference']
        
        #qFloSp
        d = pd.DataFrame(columns=['d_Name','d_ID'],dtype=int)
        for j in qFloSp.index:
            handle2 = qFloSp.iloc[j]['TL Reference'].split('TL')
            if handle1[0] == handle2[0]:
                d = d.append({'d_Name':levenshtein(str(qFlo.iloc[i]['TL Name']),str(qFloSp.iloc[j]['TL Name'])),'d_ID':abs(int(handle1[1])-int(handle2[1]))},ignore_index=True)
            else:
                d = d.append({'d_Name':levenshtein(str(qFlo.iloc[i]['TL Name']),str(qFloSp.iloc[j]['TL Name'])),'d_ID':10000},ignore_index=True)
        if d['d_Name'].min() < 10:
            ind = d['d_Name'].idxmin()
            zone_df['qFloSpTag'][i] = qFloSp.iloc[ind]['TL Name']
            zone_df['qFloSpID'][i] = qFloSp.iloc[ind]['TL Reference']
        elif d['d_ID'].min() < 30:
            ind = d['d_ID'].idxmin()
            zone_df['qFloSpTag'][i] = qFloSp.iloc[ind]['TL Name']
            zone_df['qFloSpID'][i] = qFloSp.iloc[ind]['TL Reference']
        
        #sRad
        d = pd.DataFrame(columns=['d_Name','d_ID'],dtype=int)
        for j in sRad.index:
            handle2 = sRad.iloc[j]['TL Reference'].split('TL')
            if handle1[0] == handle2[0]:
                d = d.append({'d_Name':levenshtein(str(qFlo.iloc[i]['TL Name']),str(sRad.iloc[j]['TL Name'])),'d_ID':abs(int(handle1[1])-int(handle2[1]))},ignore_index=True)
            else:
                d = d.append({'d_Name':levenshtein(str(qFlo.iloc[i]['TL Name']),str(sRad.iloc[j]['TL Name'])),'d_ID':10000},ignore_index=True)
        if d['d_Name'].min() < 10:
            ind = d['d_Name'].idxmin()
            zone_df['sRadTag'][i] = sRad.iloc[ind]['TL Name']
            zone_df['sRadID'][i] = sRad.iloc[ind]['TL Reference']
        elif d['d_ID'].min() < 30:
            ind = d['d_ID'].idxmin()
            zone_df['sRadTag'][i] = sRad.iloc[ind]['TL Name']
            zone_df['sRadID'][i] = sRad.iloc[ind]['TL Reference']
        
    return zone_df

def execute_function():
    #Specify current and input/output directories
    path = os.getcwd() #Get current directory
    output_path = path + r'\outputs\1-metadata' #Specify KPI/visualization output directory
    tk.messagebox.showinfo(title='Metadata',message='Please select the file (must be in CSV format) containing the metadata labels.')
    metadata_file_path = askopenfilename(title='Select metadata FILE (CSV)') #Ask user for metadata data file
    metadata_file_path = metadata_file_path.replace('/','\\') #Replace backward slashes with forward slashes in metadata data input directory
    if bool(metadata_file_path) == False:#User did not select a file
        print('Run terminated! No file containing metadata labels was selected.')
        tk.messagebox.showerror(title='Metadata',message='Error! Run will terminate.\n\n(No file containing metadata labels was selected.')
        return

    try: #Try reading the metadata data file
        print("Reading metadata file...")
        tag = pd.read_csv(metadata_file_path)
    except: #If file is not a CSV
        print('Run terminated! Error reading metadata file.')
        tk.messagebox.showerror(title='Metadata',message='Error! Run will terminate.\n\n(The selected metadata file could not be read. Please ensure it is CSV format and arranged as in the sample data files.)')
        return

    tk.messagebox.showinfo(title='Metadata',message='Metadata analysis will commence. This will take a while...')
    start_time = time.time() #Start timer

    try: #Try analyzing AHU- and zone-level metadata labels
        #Call the searchAHUTags local function
        ahu_df = searchAHUTags(tSaTagInc,tSaTagExc,tRaTagInc,tRaTagExc,tOaTagInc,\
                tOaTagExc,pSaTagInc,pSaTagExc,sOaTagInc,sOaTagExc,sHcTagInc,sHcTagExc,\
                sCcTagInc,sCcTagExc,sFanTagInc,sFanTagExc,tSaSpTagInc,tSaSpTagExc,\
                pSaSpTagInc,pSaSpTagExc,tag)

        #Call the searchZoneTags local function
        zone_df = searchZoneTags(zoneIdentifier,tInTagInc,tInTagExc,\
                qFloTagInc,qFloTagExc,qFloSpTagInc,qFloSpTagExc,sRadTagInc,sRadTagExc,tag)
        
        #Output resultant tags in excel file
        print('Formatting identified labels...')
        writer = pd.ExcelWriter(output_path + r'\metadata_summary.xlsx', engine='xlsxwriter') # pylint: disable=abstract-class-instantiated
        ahu_df.to_excel(writer, sheet_name='ahu')
        zone_df.to_excel(writer, sheet_name='zone')
        writer.save()

        timer = (time.time() - start_time)#Stop timer
        print("Analysis completed! Time elapsed: " + str(round(timer,3)) + ' seconds')
        tk.messagebox.showinfo(title='Metadata',message='Run successful!\n\nTime elapsed: ' + str(round(timer)) + ' seconds')

    except:#Error analyzing the metadata data file
        print('Run terminated! Error analyzing data.')
        tk.messagebox.showerror(title='Metadata',message='Error! Run will terminate.\n\n(There was an issue with the data analysis. Please ensure the data are arranged as in the sample data files.)')
        return