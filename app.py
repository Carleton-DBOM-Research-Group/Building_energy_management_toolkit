#!/usr/bin/env python

from flask import Flask, request, redirect, render_template, url_for, send_file
import os
import uuid

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
  request_uuid = str(uuid.uuid4())
  
  # create a new directory in unprocessed folder
  path = os.path.join(cwd, 'userdata', 'unprocessed', request_uuid)
  os.makedirs(path, exist_ok=True)
  energy_path = os.path.join(path, 'energy')
  os.makedirs(energy_path, exist_ok=True)
  weather_path = os.path.join(path, 'weather')
  os.makedirs(weather_path, exist_ok=True)
  
  # put the uploaded energy file in energy subfolder
  uploaded_energy_file = request.files.getlist('energy_file[]')
  uploaded_energy_file[0].save(os.path.join(energy_path, uploaded_energy_file[0].filename))

  # put the uploaded weather file in weather subfolder
  uploaded_weather_file = request.files.getlist('weather_file[]')
  uploaded_weather_file[0].save(os.path.join(weather_path, uploaded_weather_file[0].filename))

  # create text file and store variables for NECB baseline heating model
  if (bool(request.form['numberOfFloors']) == True) and (bool(request.form['wwr']) == True) and (bool(request.form['floorArea']) == True):
    f = open(os.path.join(path, "necb_parameters.txt"),"w+")
    f.write(str(request.form['numberOfFloors']) + "\n")
    f.write(str(request.form['wwr']) + "\n")
    f.write(str(request.form['floorArea']) + "\n")
    f.write(str(request.form['exteriorFacadeArea']))
    f.close()
  else:
    pass

  if 'is_elec_clg' in request.form:
    open(os.path.join(path, 'elec_true'), 'a').close()

  # create a ready file & function ID file
  open(os.path.join(path, 'ready'), 'a').close()
  open(os.path.join(path, 'energyBaseline'), 'a').close()
  
  return f"Request accepted, check the result with this link\n http://localhost:3000/checkresult/{request_uuid}"

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
  request_uuid = str(uuid.uuid4())
  
  # create a new directory and subdirectories in unprocessed folder
  path = os.path.join(cwd, 'userdata', 'unprocessed', request_uuid)
  os.makedirs(path, exist_ok=True)
  ahu_path = os.path.join(path, 'ahu')
  os.makedirs(ahu_path, exist_ok=True)
  zone_path = os.path.join(path, 'zone')
  os.makedirs(zone_path, exist_ok=True)
  
  # put the uploaded AHU HVAC file in ahu subfolder
  uploaded_ahu_files = request.files.getlist('ahu_HVAC_files[]')
  for f in uploaded_ahu_files:
    f.save(os.path.join(ahu_path, f.filename))

  # put the uploaded zone HVAC files in zone subfolder
  uploaded_zone_files = request.files.getlist('zone_HVAC_files[]')
  for f in uploaded_zone_files:
    f.save(os.path.join(zone_path, f.filename))

  # create a ready file & function ID file
  open(os.path.join(path, 'ready'), 'a').close()
  open(os.path.join(path, 'ahuAnomaly'), 'a').close()

  return f"Request accepted, check the result with this link\n http://localhost:3000/checkresult/{request_uuid}"

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
  request_uuid = str(uuid.uuid4())
  
  # create a new directory in unprocessed folder
  path = os.path.join(cwd, 'userdata', 'unprocessed', request_uuid)
  os.makedirs(path, exist_ok=True)
  
  # put the uploaded files there
  uploaded_files = request.files.getlist('zone_HVAC_files[]')
  for f in uploaded_files:
    f.save(os.path.join(path, f.filename))

  # create a ready file & function ID file
  open(os.path.join(path, 'ready'), 'a').close()
  open(os.path.join(path, 'zoneAnomaly'), 'a').close()
  
  #zoneAnomaly.execute_function(uploaded_files, path)
  #return "Success!"
  return f"Request accepted, check the result with this link\n http://localhost:3000/checkresult/{request_uuid}"


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
  request_uuid = str(uuid.uuid4())
  
  # create a new directory and subdirectories in unprocessed folder
  path = os.path.join(cwd, 'userdata', 'unprocessed', request_uuid)
  os.makedirs(path, exist_ok=True)
  energy_path = os.path.join(path, 'energy')
  os.makedirs(energy_path, exist_ok=True)
  ahu_path = os.path.join(path, 'ahu')
  os.makedirs(ahu_path, exist_ok=True)
  zone_path = os.path.join(path, 'zone')
  os.makedirs(zone_path, exist_ok=True)
  wifi_path = os.path.join(path, 'wifi')
  os.makedirs(wifi_path, exist_ok=True)
  
  # put the uploaded energy file in energy subfolder
  uploaded_energy_file = request.files.getlist('energy_file[]')
  uploaded_energy_file[0].save(os.path.join(energy_path, uploaded_energy_file[0].filename))

  # put the uploaded AHU HVAC file in ahu subfolder
  uploaded_ahu_files = request.files.getlist('ahu_HVAC_files[]')
  for f in uploaded_ahu_files:
    f.save(os.path.join(ahu_path, f.filename))

  # put the uploaded zone HVAC files in zone subfolder
  uploaded_zone_files = request.files.getlist('zone_HVAC_files[]')
  for f in uploaded_zone_files:
    f.save(os.path.join(zone_path, f.filename))

  # put the uploaded wifi filies in wifi subfolder
  uploaded_wifi_files = request.files.getlist('wifi_files[]')
  for f in uploaded_wifi_files:
    f.save(os.path.join(wifi_path, f.filename))

  # create text file and store variables
  f = open(os.path.join(path, "endUseDisaggregation_var.txt"),"w+")
  f.write(str(request.form['floorArea']) + "\n")
  f.write(str(request.form['coolingType']))
  f.close()

  # create a ready file & function ID file
  open(os.path.join(path, 'ready'), 'a').close()
  open(os.path.join(path, 'endUseDisaggregation'), 'a').close()
  
  return f"Request accepted, check the result with this link\n http://localhost:3000/checkresult/{request_uuid}"


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
  request_uuid = str(uuid.uuid4())
  
  # create a new directory and subdirectories in unprocessed folder
  path = os.path.join(cwd, 'userdata', 'unprocessed', request_uuid)
  os.makedirs(path, exist_ok=True)
  cmms_path = os.path.join(path, 'cmms')
  os.makedirs(cmms_path, exist_ok=True)
  zone_path = os.path.join(path, 'zone')
  os.makedirs(zone_path, exist_ok=True)
  weather_path = os.path.join(path, 'weather')
  os.makedirs(weather_path, exist_ok=True)
  
  # put the uploaded energy file in energy subfolder
  uploaded_cmms_file = request.files.getlist('cmms_file[]')
  uploaded_cmms_file[0].save(os.path.join(cmms_path, uploaded_cmms_file[0].filename))

  # put the uploaded zone HVAC files in zone subfolder
  uploaded_zone_files = request.files.getlist('zone_HVAC_files[]')
  for f in uploaded_zone_files:
    f.save(os.path.join(zone_path, f.filename))

  # put the uploaded weather file in weather subfolder
  uploaded_weather_file = request.files.getlist('weather_file[]')
  uploaded_weather_file[0].save(os.path.join(weather_path, uploaded_weather_file[0].filename))

  # create text file and store inputted floor area
  f = open(os.path.join(path, "floor_area.txt"),"w+")
  f.write(str(request.form['floorArea']))
  f.close()

  # create a ready file & function ID file
  open(os.path.join(path, 'ready'), 'a').close()
  open(os.path.join(path, 'complaintAnalytics'), 'a').close()
  
  return f"Request accepted, check the result with this link\n http://localhost:3000/checkresult/{request_uuid}"


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
  
  cwd = os.getcwd()
  request_uuid = str(uuid.uuid4())
  
  # create a new directory in unprocessed folder
  path = os.path.join(cwd, 'userdata', 'unprocessed', request_uuid)
  os.makedirs(path, exist_ok=True)
  
  # put the uploaded wifi files there
  uploaded_wifi_files = request.files.getlist('wifi_files[]')
  for f in uploaded_wifi_files:
    f.save(os.path.join(path, f.filename))
  
  # create flag for floor level analysis
  if 'is_flr_lvl' in request.form:
    open(os.path.join(path, 'is_flr_lvl'), 'a').close()

  # create a ready file & function ID file
  open(os.path.join(path, 'ready'), 'a').close()
  open(os.path.join(path, 'occupancy_wifi'), 'a').close()
  
  #zoneAnomaly.execute_function(uploaded_files, path)
  #return "Success!"
  return f"Request accepted, check the result with this link\n http://localhost:3000/checkresult/{request_uuid}"

  
@app.route('/functions/occupancy/upload/run-occupancy-motion', methods=['POST'])
def run_occupancy_motion_function():

  cwd = os.getcwd()
  request_uuid = str(uuid.uuid4())
  
  # create a new directory in unprocessed folder
  path = os.path.join(cwd, 'userdata', 'unprocessed', request_uuid)
  os.makedirs(path, exist_ok=True)
  
  # put the uploaded files there
  uploaded_files = request.files.getlist('motion_files[]')
  for f in uploaded_files:
    f.save(os.path.join(path, f.filename))

  # create a ready file & function ID file
  open(os.path.join(path, 'ready'), 'a').close()
  open(os.path.join(path, 'occupancy_motion'), 'a').close()
  
  #zoneAnomaly.execute_function(uploaded_files, path)
  #return "Success!"
  return f"Request accepted, check the result with this link\n http://localhost:3000/checkresult/{request_uuid}"

#Function to check results

@app.route('/checkresult/<uuid:request_uuid>')
def check_result(request_uuid):
  cwd = os.getcwd()
  result_dir = os.path.join(cwd, 'userdata', 'done', str(request_uuid))
  if os.path.isfile(os.path.join(result_dir, 'ready')):
    return send_file(os.path.join(result_dir, 'report.pdf'))
  elif os.path.isfile(os.path.join(result_dir, 'error')):
    return "Something went wrong with the analysis. Please check your input data and try again."
  else:
    return "Your results are not ready yet. Please check back later."