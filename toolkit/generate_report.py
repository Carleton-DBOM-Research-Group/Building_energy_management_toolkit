#import required modules
import os
import pandas as pd
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

#-----------------------------------------------GENERATE BASELINE ENERGY REPORT----------------------------------------------------
def energyBaseline():
    print('Generating report for Baseline Energy function...')

    path = os.getcwd() #Get current directory
    output_path = path + r'\reports\2-energyBaseline' #Specify the output path for report
    input_path = path + r'\outputs\2-energyBaseline'

    document = Document()

    document.add_heading('Baseline Energy - Analysis Report', 0) #Report title

    #Introductory paragraph
    p = document.add_paragraph('The Baseline energy function inputs building-level heating, cooling, and electricity energy meter data and ')
    p.add_run('compares energy use during operating hours and outside operating hours (afterhours) for heating, cooling, and electricity. ').bold=True
    p.add_run("This function is intended to help the user assess the effectiveness of schedules and their ability to reduce \
energy use outside of the building's operating hours. Visualizations compare the energy use rates during and outside operating \
as a function of outdoor air temperature, and predict energy consumption at representative outdoor air temperatures - these are \
done separately for heating, cooling, and electrcity. The generated key performance indicators (KPI) quantify schedule \
effectiveness and afterhours energy use. More information is found in the respective sections.")

    #Visualization heading and description
    document.add_heading('Visualizations', level=1)
    p = document.add_paragraph('The first set of visualizations compare the rate of energy use during operating hours and \
outside operating hours (afterhours) as a function of outdoor air temperatures - this is done separately for heating, \
cooling, and electricity. If the afterhours energy use is similiar or identical (in magnitude or degree of inclined slope) \
to the operating energy use, the current schedules are ineffective in reducing energy use during afterhours. If the slopes are vastly different, \
the current schedules are effective in reducing energy use outside operating hours.')
    p = document.add_paragraph('The second set of visualizations illustrates the predicted sensitivity of energy use on outdoor \
air temperatures - this is done separately for heating, cooling, and electricity. If the lines are spaced considerably apart, \
the energy use is particularily sensitive to outdoor air temperature.')

    #Add visualizations
    document.add_picture(input_path + r'\energyBase_heating.png', width=Inches(5.75))
    document.add_picture(input_path + r'\energyBase_cooling.png', width=Inches(5.75))
    document.add_picture(input_path + r'\energyBase_electricity.png', width=Inches(5.75))

    #KPIs heading and description
    document.add_heading('Key performance Indicators', level=1)
    p = document.add_paragraph('The generated KPIs are ')
    p.add_run('Schedule effectiveness').bold = True
    p.add_run(' and ')
    p.add_run('Afterhours energy use ratio').bold = True
    p.add_run('. Schedule effectiveness quanitfies the difference between the inclined slope of the modeled operating and modeled \
afterhours energy use rates. Values approaching zero (0) indicate similiar or identical inclined slopes, positive (+) values indcate \
a steeper operating hours energy use inclined slope, and negative (-) values indicate a steeper afterhours energy use inclined slope. \
The Afterhours energy use ratio is the ratio of energy use during afterhours over the total energy use.')

    document.add_page_break()

    #Extract data from excel sheet and add table to document
    kpis = pd.read_excel(input_path + r'\energyBase_summary.xlsx',sheet_name='KPIs')
    kpis.drop(kpis.columns[0],axis=1,inplace=True)

    p = document.add_heading('Schedule Effectiveness and Afterhours energy use ratio',level=2)
    t = document.add_table(kpis.shape[0]+1, kpis.shape[1])
    
    for j in range(kpis.shape[-1]): # add the header rows.
        t.cell(0,j).text = kpis.columns[j]
    
    for i in range(kpis.shape[0]): # add the rest of the data frame
        for j in range(kpis.shape[-1]):
            t.cell(i+1,j).text = str(kpis.values[i,j])

    #Save document in reports folder
    document.save(output_path + r'\energyBaseline_report.docx')
    print('Report successfully generated!')

    return

#-----------------------------------------------GENERATE AHU ANOMALY REPORT----------------------------------------------------
def ahuAnomaly():
    print('Generating report for AHU anomaly detection function...')

    path = os.getcwd() #Get current directory
    output_path = path + r'\reports\3-ahuAnomaly' #Specify the output path for report
    input_path = path + r'\outputs\3-ahuAnomaly'

    #Extract KPIs excel sheet
    faults_df = pd.read_excel(input_path + r'\ahu_anomaly_summary.xlsx',sheet_name='faults')
    faults_df.drop(faults_df.columns[0],axis=1,inplace=True)

    document = Document()

    document.add_heading('AHU Anomaly - Analysis Report', 0) #Report title

    #Introductory paragraph
    p = document.add_paragraph('The AHU anomaly detection function inputs AHU- and zone-level HVAC network trendlog data and ')
    p.add_run('detects hard and soft faults related to AHUs. ').bold=True
    p.add_run("This function is intended to help the user identify potential causes for anomalous AHU operations which may cause \
energy use inefficiencies. The accompanying visualizations are intended to aid understanding of the detected faults. These depict \
supply air temperature, and the coolest/warmest/average return air temperatures as a function of outdoor air temperature, and  \
damper and valve actuator positions as a function of outdoor air temperature. Additionaly, a number of diagrams are generated which \
depict damper and valve actuator positions and temperature readings at characteristic AHU operational periods. More informations is \
available at the respective sections.")

    #Visualization heading and description - Part 1
    document.add_heading('Visualizations - Split-range controller', level=1)
    p = document.add_paragraph('A set of two charts are generated for each AHU inputted. The top chart depicts supply air \
temperature, and the coolest/warmest/average return air temperatures as a function of outdoor air temperature. For \
reference, the "ideal" supply air temperature is depicted.\n\nThe bottom chart is a Split-range controller diagram, which \
plots damper and valve actuator positons and average fraction of active perimeter heaters per zone as a function of \
outdoor air temperature. The four underlaying color zones represent the four distinct operating mode: Heating (red zone) \
, economizer (yellow zone), economizer with cooling (grey zone), and cooling (blue zone). For reference, the below \
Split-range controller diagram is a typical example of normal AHU operations.')
    document.add_picture(output_path + r'\SRC_example.png', width=Inches(5.75))

    #For each AHU, output the first set of visuals
    for i in faults_df.index:

        document.add_heading('AHU: ' + str(faults_df.iloc[i][0]), level=2)
        document.add_picture(input_path + r'\f2a_ahu_'+str(i+1)+'.png', width=Inches(5))
    
    #Visualization heading and description - Part 2
    document.add_heading('Visualizations - Snapshots of AHU operating periods', level=1)
    p = document.add_paragraph("A set of four to six visuals per AHU are generated which depict characteristic operating \
periods of the AHU and the average damper/valve positions and temperatures at those periods. The fraction of time of \
operation is the percentage of the total time of the AHU's operation which exhibit the following damper/valve positions \
and temperatures.")
    
    #For each AHU, output the second set of visuals
    for i in faults_df.index:

        document.add_heading('AHU: ' + str(faults_df.iloc[i][0]), level=2)

        for j in range(1,7):
            try:
                document.add_picture(input_path + r'\f2b_ahu_'+str(i+1)+'_C_'+str(j)+'.png', width=Inches(5))
            except FileNotFoundError:
                break

    document.add_page_break()

    #Extract data from excel sheet and add table to document

    p = document.add_heading('AHU faults and anomalies',level=1)
    p = document.add_paragraph("The following table lists the hard and soft faults identified by the function.")
    t = document.add_table(faults_df.shape[0]+1, faults_df.shape[1])
    
    for j in range(faults_df.shape[-1]): # add the header rows.
        t.cell(0,j).text = faults_df.columns[j]
    
    for i in range(faults_df.shape[0]): # add the rest of the data frame
        for j in range(faults_df.shape[-1]):
            t.cell(i+1,j).text = str(faults_df.values[i,j])

    #Save document in reports folder
    document.save(output_path + r'\ahuAnomaly_report.docx')
    print('Report successfully generated!')

    return

#-----------------------------------------------GENERATE ZONE ANOMALY REPORT----------------------------------------------------
def zoneAnomaly():
    print('Generating report for zone anomaly detection function...')

    path = os.getcwd() #Get current directory
    output_path = path + r'\reports\4-zoneAnomaly' #Specify the output path for report
    input_path = path + r'\outputs\4-zoneAnomaly' #Specify the input path for report

    #Extract KPIs excel sheet
    kpis_heating = pd.read_excel(input_path + r'\zone_anomaly_summary.xlsx',sheet_name='Heating season')
    kpis_heating.drop(kpis_heating.columns[0],axis=1,inplace=True)
    kpis_cooling = pd.read_excel(input_path + r'\zone_anomaly_summary.xlsx',sheet_name='Cooling season')
    kpis_cooling.drop(kpis_cooling.columns[0],axis=1,inplace=True)

    #Generate Word document
    document = Document()

    #Report title
    document.add_heading('Zone Anomaly - Analysis Report', 0)

    #Introductory paragraph
    p = document.add_paragraph('The zone anomaly function inputs zone-level HVAC controls network data and ')
    p.add_run('detects anomalous zones based on indoor air temperature and airflow control errors. ').bold = True
    p.add_run('This report outputs the results of the clustering algorithm, including the number of clusters \
generated, the number of zones included in each cluster, the average indoor air temperature of each cluster of zones, and the average airflow rate setpoint error \
of each cluster of zones. Visualization are also generated which depict the zone clusters relative to their \
average indoor air temperature and average airflow rate setpoint error; this is done separately for the heating \
and cooling season. This function is intended to help the user identify abnormal or undesirable operating conditions in \
groups of zones.')

    #Visualization heading and description
    document.add_heading('Visualizations', level=1)
    p = document.add_paragraph('The generated visualizations depict the resultant zone clusters relative \
to their average indoor air temperature and average airflow rate setpoint error. This is done separately for \
the heating season (December through February) and cooling season (May thorugh August). Zone clusters \
are represented by the black semi-transparent boxes and cluster identifier. The cluster identifier \
(C1, C2, C3, etc.) is also presented on the top-left of the visualization along with the number of zones \
that are included in each cluster. This information is also provided in the Key Performance Indicators section.')

    #Add visualizations
    document.add_picture(input_path + r'\zone_heat_season.png', width=Inches(4.75))
    document.add_picture(input_path + r'\zone_cool_season.png', width=Inches(4.75))

    #KPIs heading and description
    document.add_heading('Key performance Indicators', level=1)
    p = document.add_paragraph('This section presents the generated KPIs - ')
    p.add_run('the zone health index').bold = True
    p.add_run('. The zone health index is the ') 
    p.add_run('ratio of zones with acceptable indoor air temperature and airflow setpoint error over the \
total number of zones ').bold = True
    p.add_run('- this is calculated separately for the heating season (December through February) and the \
cooling season (May thorugh August). An acceptable indoor air temperature is considered to be between 20 and \
25 degrees, and an acceptable airflow setpoint control error is +/- 20%. The airflow setpoint control error \
is the ratio of the difference between the actual airflow rate and setpoint airflow rate over the setpoint airflow rate.')

    heating_health_index = (round(kpis_heating.iloc[0]['Health Index'],3))*100
    cooling_health_index = (round(kpis_cooling.iloc[0]['Health Index'],3))*100

    p = document.add_paragraph('Zone health index for heating: ', style='List Bullet')
    p.add_run(str(heating_health_index) + '%').bold = True
    p = document.add_paragraph('Zone health index for cooling: ', style='List Bullet')
    p.add_run(str(cooling_health_index) + '%').bold = True

    #Add tables with summary tables
    p = document.add_paragraph('The clustering algorithm resulted in ' + str(len(kpis_heating.index))\
        + ' zone clusters for the heating season and ' + str(len(kpis_cooling.index)) + ' zone clusters \
for the cooling season. The below tables lists the resultant zone clusters, the number of zones included in each cluster, \
the average indoor air temperature, and average airflow rate setpoint error for each cluster. For the heating season, the average fraction \
of active (On-state) perimter heaters within a zone is also provided for each cluster.')
    
    document.add_page_break()

    kpis_heating.drop(kpis_heating.columns[-1],axis=1,inplace=True) #Drop the health index from the heating season table
    kpis_cooling.drop(kpis_cooling.columns[-1],axis=1,inplace=True) #Drop the health index from the cooling season table
    table_labels = ['Number of zones','Average indoor air temperature (C)','Average airflow rate setpoint error (%)','Average fraction of active perimeter heaters (%)']
    table_headings = ['Heating season KPIs','Cooling season KPIs']
    k = 0

    for df in [kpis_heating,kpis_cooling]:
        df = df.round(1)
        p = document.add_heading(table_headings[k],level=2)
        t = document.add_table(df.shape[0]+1, df.shape[1])
        
        for j in range(df.shape[-1]): # add the header rows.
            t.cell(0,j).text = table_labels[j]
        
        for i in range(df.shape[0]): # add the rest of the data frame
            for j in range(df.shape[-1]):
                t.cell(i+1,j).text = str(df.values[i,j])
        k+=1
        

    #Save document in reports folder
    document.save(output_path + r'\zoneAnomaly_report.docx')
    print('Report successfully generated!')

    return

#------------------------------------------------------GENERATE END-USE DISAGGREGATION REPORT -------------------------------------------------
def endUseDisaggregation():
    print('Generating report for end-uses disaggregation function...')

    path = os.getcwd() #Get current directory
    output_path = path + r'\reports\5-endUseDisaggregation' #Specify the output path for report
    input_path = path + r'\outputs\5-endUseDisaggregation' #Specify the input path for report

    #Extract KPIs excel sheet
    kpis_htg = pd.read_excel(input_path + r'\endUseDisagg_summary.xlsx',sheet_name='Heating')
    kpis_clg = pd.read_excel(input_path + r'\endUseDisagg_summary.xlsx',sheet_name='Cooling')
    kpis_ele = pd.read_excel(input_path + r'\endUseDisagg_summary.xlsx',sheet_name='Electricity')
    kpis_htg.drop(kpis_htg.columns[0],axis=1,inplace=True)
    kpis_clg.drop(kpis_clg.columns[0],axis=1,inplace=True)
    kpis_ele.drop(kpis_ele.columns[0],axis=1,inplace=True)

    #Generate Word document
    document = Document()

    #Report title
    document.add_heading('End-use Disaggregation - Analysis Report', 0)

    #Introductory paragraph
    p = document.add_paragraph('The end-use disaggregation function inputs energy meter, Wi-Fi device count, and AHU- and zone-level \
HVAC controls trendlog data, and calculates annual energy use intensities of major end-uses. The major end-uses for electricity are ')
    p.add_run('lighting and plug-loads, distribution (i.e., pumps and fans), and chillers').bold = True
    p.add_run('. The major end-uses for heating energy use are ')
    p.add_run('perimeter heating, the AHUs’ heating coils, and other appliances (i.e., domestic hot water)').bold = True
    p.add_run('. The major end-use for cooling energy are the ')
    p.add_run('AHUs’ cooling coils.').bold = True
    p.add_run(' This function is intended to help the user assess the distribution of energy consumption within a building and can \
be used to identify abnormal activity or lack thereof of end-uses in a yearly context.')

    #Visualization heading and description
    document.add_heading('Visualizations', level=1)
    p = document.add_paragraph('The generated visualization are energy use intensity profiles which depict the weekly distribution \
of the major end-uses for electricity, cooling, and heating separately.')

    #Add visualizations
    document.add_picture(input_path + r'\endUseDisaggregation.png', width=Inches(5.75))

    #KPIs heading and description
    document.add_heading('Key performance Indicators', level=1)
    p = document.add_paragraph('This section presents the generated KPIs - ')
    p.add_run('energy use intensities for major end-uses in heating energy, cooling energy, and electricity use').bold = True
    p.add_run(". The calculated energy use intensities for the AHU heating and cooling coils are disaggregated by each AHU. For \
example, if three (3) AHUs were analyzed, the energy use intensites for the AHU heating coils is provided as [NUM NUM NUM], whereby \
'NUM' represents the calculated energy use intensities for each consecutive AHU.")

    document.add_page_break()

    #Add KPIs
    table_labels = ['End-use','Total annual energy use intensity (kWh/m2)']
    table_headings = ['Heating energy','Cooling energy','Electricity']
    k = 0

    for df in [kpis_htg,kpis_clg,kpis_ele]:
        df = df.round(1)
        p = document.add_heading(table_headings[k],level=2)
        t = document.add_table(df.shape[0]+1, df.shape[1])
        
        for j in range(df.shape[-1]): # add the header rows.
            t.cell(0,j).text = table_labels[j]
        
        for i in range(df.shape[0]): # add the rest of the data frame
            for j in range(df.shape[-1]):
                t.cell(i+1,j).text = str(df.values[i,j])
        k+=1

    #Save document in reports folder
    document.save(output_path + r'\endUseDisaggregation_report.docx')
    print('Report successfully generated!')

    return

#------------------------------------------------------GENERATE OCCUPANCY REPORT-------------------------------------------------
def occupancy():
    print('Generating report for occupancy function...')

    path = os.getcwd() #Get current directory
    output_path = path + r'\reports\6-occupancy' #Specify the output path for report
    input_path = path + r'\outputs\6-occupancy' #Specify the input path for report

    #Extract KPIs excel sheet
    kpis = pd.read_excel(input_path + r'\arrive_depart_maxOcc.xlsx',sheet_name='KPIs')
    kpis = kpis.round() #Remove decimal places

    #Generate Word document
    document = Document()

    #Report title
    document.add_heading('Occupancy - Analysis Report', 0)

    #Introductory paragraph
    p = document.add_paragraph('The occupancy function inputs Wi-Fi device count data and determines typical ')
    p.add_run('earliest arrival times, latest departure times,').bold = True
    p.add_run(' and ')
    p.add_run('highest recorded occupancy').bold = True
    p.add_run(' for weekdays and weekends separately. This report outputs the results of the function and a set of visualizations \
illustrating building-level and floor-level occupant count profiles.')

    #Visualization heading and description
    document.add_heading('Visualizations', level=1)
    p = document.add_paragraph('The first set of visualizations are building-level hourly occupant count profiles for weekdays and \
weekends separately. The profiles are shown as the 25th, 50th (median), and 75th percentile whereby the 25th percentile represents \
the lower range of typical occupancy and the 75th represents the higher range. The second set of visualizations are \
occupant count profiles taken at the 75th percentile and broken down by floor.')

    #Add visualizations
    document.add_picture(input_path + r'\percentile_occ.png', width=Inches(5.75))
    document.add_picture(input_path + r'\floor_level_occ.png', width=Inches(5.75))

    #KPIs heading and description
    document.add_heading('Key performance Indicators', level=1)
    p = document.add_paragraph('This section presents the generated KPIs - ')
    p.add_run('typical earliest arrival times, latest departure times, and highest occupant count').bold = True
    p.add_run(' which are broken down by floor and determined sparately for weekdays and weekends. Typical earliest arrival times \
are determined at the hour whereby the 75th percentile occupant count exceeds '+r'10%'+' of the maximum recorded count per floor. Similiarily, typical latest \
departure times are determined whereby the 75th percentile occupant count dips below '+r'10%'+' of the maximum recorded count per floor. The highest occupant \
is taken as the highest recorded occupant count at the 75th percentile.')

    document.add_page_break()

    #Add tables with summary tables
    table_labels = ['Floor',
                    'Weekday earliest arrival time (hours after midnight)',
                    'Weekday latest departure time (hours after midnight)',
                    'Weekday highest occupant count',
                    'Weekend earliest arrival time (hours after midnight)',
                    'Weekend latest departure time (hours after midnight)',
                    'Weekend highest occupant count']

    p = document.add_heading('Earliest arrival times, latest departure times, and highest occupant count',level=2)
    t = document.add_table(kpis.shape[0]+1, kpis.shape[1])
    
    for j in range(kpis.shape[-1]): # add the header rows.
        t.cell(0,j).text = table_labels[j]
    
    for i in range(kpis.shape[0]): # add the rest of the data frame
        for j in range(kpis.shape[-1]):
            t.cell(i+1,j).text = str(kpis.values[i,j])
        

    #Save document in reports folder
    document.save(output_path + r'\occupancy_report.docx')
    print('Report successfully generated!')

    return

#------------------------------------------------------GENERATE COMPLAINTS REPORT-------------------------------------------------
def complaints():
    print('Generating report for occupant complaints analytics function...')

    path = os.getcwd() #Get current directory
    output_path = path + r'\reports\7-complaintsAnalytics' #Specify the output path for report
    input_path = path + r'\outputs\7-complaintsAnalytics' #Specify the input path for report

    #Extract KPIs excel sheet
    kpis = pd.read_excel(input_path + r'\complaints_freq.xlsx',sheet_name='Daily frequency of complaints')
    kpis.drop(kpis.columns[0],axis=1,inplace=True)

    #Generate Word document
    document = Document()

    #Report title
    document.add_heading('Occupancy - Analysis Report', 0)

    #Introductory paragraph
    p = document.add_paragraph('The occupant complaints function inputs occupant complaints logs and weather data and determines the ')
    p.add_run('daily frequency of hot/cold-related occupant complaints.').bold = True
    p.add_run(' Visualizations are generated which depict the distribution of complaints by month and by the period \
of the day by which the complaint was registered, the relationship of hot/cold complaints to indoor and outdoor \
air temperature, and the predicted proportion of the cold/hot complaints based on time of day, day of the week, \
and outdoor air temperature')

    #First visualization heading and description
    document.add_heading('Occupant complaints breakdown', level=1)
    p = document.add_paragraph('The first set of visualizations categorize the complaints by the type of complaint \
(hot or cold related), and quanitify the number of complaints by the month and period of the day the complaint was \
registered.')

    #Add first visualizations
    document.add_picture(input_path + r'\complaints_breakdown.png', width=Inches(5.75))

    #Second visualization heading and description
    document.add_heading('Occupant complaints with indoor/outdoor air temperature', level=1)
    p = document.add_paragraph('The second visualization depicts the relationship between a hot/cold complaint \
and the indoor and outdoor air temperature at the time the complaint was registered.')

    #Add second visualizations
    document.add_picture(input_path + r'\complaint_scatter.png', width=Inches(5.75))

    #Third visualization heading and description
    document.add_heading('Predicted proportion of complaints', level=1)
    p = document.add_paragraph("The third visualization predicts the proportion of complaints that would be made \
with respect to certain conditions in time of day, day of the week, and outdoor air temperatures. The decision tree \
diagram can be interpreted whereby boxes branching to the left represent the predicted proportion of complaints when \
the condition in the preceding box is satisfied. For example, if a box with the condition, 'Hour of the day <= 10' \
has a left node with "+r"40%"+" and a right node with "+r"60%"+", it is predicted that "+r"40%"+" of all complaints \
made will occur before 10 am. The condition is displayed at the top of the box and the predicted \
proportion of displayed at the center of each box between the 0.0s.")

    #Add third visualizations
    document.add_picture(input_path + r'\decision_tree.png', width=Inches(5.75))

    #KPIs heading and description
    document.add_heading('Key performance Indicators', level=1)
    p = document.add_paragraph('This section presents the generated KPIs - ')
    p.add_run('daily frequency of hot and cold complaints in the heating and cooling season.').bold = True
    p.add_run(' Higher frequencies indicate a higher rate of occurence of a type of complaint for the particular season.')

    table_labels = ['Type of complaint',
                    'Daily frequency for heating season (complaints per day)',
                    'Daily frequency for cooling season (complaints per day)']

    p = document.add_heading('Daily frequencies of hot/cold occupant complaints',level=2)
    t = document.add_table(kpis.shape[0]+1, kpis.shape[1])
    
    for j in range(kpis.shape[-1]): # add the header rows.
        t.cell(0,j).text = table_labels[j]
    
    for i in range(kpis.shape[0]): # add the rest of the data frame
        for j in range(kpis.shape[-1]):
            t.cell(i+1,j).text = str(kpis.values[i,j])
        

    #Save document in reports folder
    document.save(output_path + r'\complaint_report.docx')
    print('Report successfully generated!')

    return