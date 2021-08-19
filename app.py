#!/usr/bin/env python

from flask import Flask, request, redirect, render_template, url_for
import os

import metadata
import energyBaseline
import ahuAnomaly
import zoneAnomaly
import endUseDisaggregation
import occupancy
import complaintAnalytics
import generate_report

app = Flask(__name__)

@app.route('/', methods = ["GET"])
def index():
  return redirect(url_for('home'))

@app.route('/home', methods = ["GET"])
def home():
  return render_template('index.html')

@app.route('/functions', methods = ['GET'])
def functions():
  return render_template('functions.html')

#METADATA  

@app.route('/functions/metadata', methods = ['GET'])
def metadata_overview():
  return render_template('functions_metadata_overview.html')

@app.route('/functions/metadata/inputs', methods = ['GET'])
def metadata_inputs():
  return render_template('functions_metadata_inputs.html')

@app.route('/functions/metadata/outputs', methods = ['GET'])
def metadata_outputs():
  return render_template('functions_metadata_outputs.html')

@app.route('/functions/metadata/upload', methods=['GET'])
def metadata_upload():
  return render_template('functions_metadata_upload.html')

@app.route('/functions/metadata/upload/run-metadata', methods=['POST'])
def run_metadata_function():

  cwd = os.getcwd()
  path = cwd + r'\test_outputs'
  uploaded_metadata_file = request.files.getlist('metadata_file[]')

  metadata.execute_function(uploaded_metadata_file[0], path)
  return "Success!"

#ENERGY BASELINE  

@app.route('/functions/energyBaseline', methods = ['GET'])
def energyBaseline_overview():
  return render_template('functions_energyBaseline_overview.html')

@app.route('/functions/energyBaseline/inputs', methods = ['GET'])
def energyBaseline_inputs():
  return render_template('functions_energyBaseline_inputs.html')

@app.route('/functions/energyBaseline/outputs', methods = ['GET'])
def energyBaseline_outputs():
  return render_template('functions_energyBaseline_outputs.html')

@app.route('/functions/energyBaseline/upload', methods=['GET'])
def energyBaseline_upload():
  return render_template('functions_energyBaseline_upload.html')

@app.route('/functions/energyBaseline/upload/run-energyBaseline', methods=['POST'])
def run_energyBaseline_function():

  cwd = os.getcwd()
  path = cwd + r'\test_outputs'
  uploaded_energy_file = request.files.getlist('energy_file[]')
  uploaded_weather_file = request.files.getlist('weather_file[]')

  if (bool(request.form['exteriorFacadeArea']) == True):
    exteriorFacadeArea = float(request.form['exteriorFacadeArea'])
  else:
    exteriorFacadeArea = 0
  
  if (bool(request.form['numberOfFloors']) == True):
    numberOFFloors = int(request.form['numberOfFloors'])
  else:
    numberOFFloors = 0
  
  if (bool(request.form['wwr']) == True):
    wwr = float(request.form['wwr'])
  else:
    wwr = 0
  
  if (bool(request.form['floorArea']) == True):
    floorArea = float(request.form['floorArea'])
  else:
    floorArea = 0

  energyBaseline.execute_function(uploaded_energy_file[0], uploaded_weather_file[0], numberOFFloors, wwr, floorArea, exteriorFacadeArea, path)
  return "Success!"

#AHU ANOMALY  

@app.route('/functions/ahuAnomaly', methods = ['GET'])
def ahuAnomaly_overview():
  return render_template('functions_ahuAnomaly_overview.html')

@app.route('/functions/ahuAnomaly/inputs', methods = ['GET'])
def ahuAnomaly_inputs():
  return render_template('functions_ahuAnomaly_inputs.html')

@app.route('/functions/ahuAnomaly/outputs', methods = ['GET'])
def ahuAnomaly_outputs():
  return render_template('functions_ahuAnomaly_outputs.html')

@app.route('/functions/ahuAnomaly/upload', methods=['GET'])
def ahuAnomaly_upload():
  return render_template('functions_ahuAnomaly_upload.html')

@app.route('/functions/ahuAnomaly/upload/run-ahuAnomaly', methods=['POST'])
def run_ahuAnomaly_function():

  cwd = os.getcwd()
  path = cwd + r'\test_outputs'
  uploaded_ahu_files = request.files.getlist('ahu_HVAC_files[]')
  uploaded_zone_files = request.files.getlist('zone_HVAC_files[]')

  ahuAnomaly.execute_function(uploaded_ahu_files, uploaded_zone_files, path)
  return "Success!"

#ZONE ANOMALY  

@app.route('/functions/zoneAnomaly', methods = ['GET'])
def zoneAnomaly_overview():
  return render_template('functions_zoneAnomaly_overview.html')

@app.route('/functions/zoneAnomaly/inputs', methods = ['GET'])
def zoneAnomaly_inputs():
  return render_template('functions_zoneAnomaly_inputs.html')

@app.route('/functions/zoneAnomaly/outputs', methods = ['GET'])
def zoneAnomaly_outputs():
  return render_template('functions_zoneAnomaly_outputs.html')

@app.route('/functions/zoneAnomaly/upload', methods=['GET'])
def zoneAnomaly_upload():
  return render_template('functions_zoneAnomaly_upload.html')

@app.route('/functions/zoneAnomaly/upload/run-zoneAnomaly', methods=['POST'])
def run_zoneAnomaly():
  cwd = os.getcwd()
  path = cwd + r'\test_outputs'
  uploaded_files = request.files.getlist('zone_HVAC_files[]')

  zoneAnomaly.execute_function(uploaded_files, path)
  return "Success!"



#END-USE DISAGGREGATION  

@app.route('/functions/endUseDisaggregation', methods = ['GET'])
def endUseDisaggregation_overview():
  return render_template('functions_endUseDisaggregation_overview.html')

@app.route('/functions/endUseDisaggregation/inputs', methods = ['GET'])
def endUseDisaggregation_inputs():
  return render_template('functions_endUseDisaggregation_inputs.html')

@app.route('/functions/endUseDisaggregation/outputs', methods = ['GET'])
def endUseDisaggregation_outputs():
  return render_template('functions_endUseDisaggregation_outputs.html')

@app.route('/functions/endUseDisaggregation/upload', methods=['GET'])
def endUseDisaggregation_upload():
  return render_template('functions_endUseDisaggregation_upload.html')

@app.route('/functions/endUseDisaggregation/upload/run-endUseDisaggregation', methods=['POST'])
def run_endUseDisaggregation_function():

  cwd = os.getcwd()
  path = cwd + r'\test_outputs'
  uploaded_energy_file = request.files.getlist('energy_file[]')
  uploaded_ahu_files = request.files.getlist('ahu_HVAC_files[]')
  uploaded_zone_files = request.files.getlist('zone_HVAC_files[]')
  uploaded_wifi_files = request.files.getlist('wifi_files[]')

  bldg_area = int(request.form['floorArea'])
  cooling_type = request.form['coolingType']

  endUseDisaggregation.execute_function(uploaded_energy_file[0], uploaded_ahu_files, uploaded_zone_files, uploaded_wifi_files, bldg_area, cooling_type, path)
  return "Success!"


#COMPLAINT ANALYTICS  

@app.route('/functions/complaintAnalytics', methods = ['GET'])
def complaintAnalytics_overview():
  return render_template('functions_complaintAnalytics_overview.html')

@app.route('/functions/complaintAnalytics/inputs', methods = ['GET'])
def complaintAnalytics_inputs():
  return render_template('functions_complaintAnalytics_inputs.html')

@app.route('/functions/complaintAnalytics/outputs', methods = ['GET'])
def complaintAnalytics_outputs():
  return render_template('functions_complaintAnalytics_outputs.html')

@app.route('/functions/complaintAnalytics/upload', methods=['GET'])
def complaintAnalytics_upload():
  return render_template('functions_complaintAnalytics_upload.html')

@app.route('/functions/complaintAnalytics/upload/run-complaintAnalytics', methods=['POST'])
def run_complaintAnalytics_function():

  cwd = os.getcwd()
  path = cwd + r'\test_outputs'
  uploaded_cmms_file = request.files.getlist('cmms_file[]')
  uploaded_zone_files = request.files.getlist('zone_HVAC_files[]')
  uploaded_weather_file = request.files.getlist('weather_file[]')

  bldg_area = int(request.form['floorArea'])

  complaintAnalytics.execute_function(uploaded_cmms_file[0], uploaded_zone_files, uploaded_weather_file[0], bldg_area, path)
  return "Success!"


#OCCUPANCY  

@app.route('/functions/occupancy', methods = ['GET'])
def occupancy_overview():
  return render_template('functions_occupancy_overview.html')

@app.route('/functions/occupancy/inputs', methods = ['GET'])
def occupancy_inputs():
  return render_template('functions_occupancy_inputs.html')

@app.route('/functions/occupancy/outputs', methods = ['GET'])
def occupancy_outputs():
  return render_template('functions_occupancy_outputs.html')

@app.route('/functions/occupancy/upload', methods=['GET'])
def occupancy_upload():
  return render_template('functions_occupancy_upload.html')

@app.route('/functions/occupancy/upload/run-occupancy-wifi', methods=['POST'])
def run_occupancy_wifi_function():
  try:
    cwd = os.getcwd()
    path = cwd + r'\test_outputs'
    uploaded_files = request.files.getlist('wifi_files[]')
  
    occupancy.execute_function_wifi(uploaded_files,path)
    return "Success!"

  except:
    return "Something went wrong!"

  
@app.route('/functions/occupancy/upload/run-occupancy-motion', methods=['POST'])
def run_occupancy_motion_function():
  try:
    cwd = os.getcwd()
    path = cwd + r'\test_outputs'
    uploaded_files = request.files.getlist('motion_files[]')

    occupancy.execute_function_motion(uploaded_files[0],path)
    return "Success!"
  
  except:
    return "Something went wrong!"
