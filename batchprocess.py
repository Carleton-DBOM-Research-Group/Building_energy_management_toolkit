#!/usr/bin/env python

import time
import os
import shutil

#import functions
import ahuAnomaly
import zoneAnomaly
import metadata
import endUseDisaggregation
import occupancy
import energyBaseline
import complaintAnalytics
import generate_report

SLEEP_TIME = 10

def is_ready(input_dir):
  return os.path.isfile(os.path.join(input_dir, 'ready'))

def process_work(job_id, input_dir):
  cwd = os.getcwd()
  output_dir = os.path.join(cwd, 'userdata', 'done', job_id)
  os.makedirs(output_dir, exist_ok=True)

  #Select function to invoke and perform analysis and generate outputs
  if os.path.isfile(os.path.join(input_dir, 'zoneAnomaly')):
    print('Performing analysis using zone anomaly function...')
    #Do zone anomaly work here
    try:
      zoneAnomaly.execute_function(input_dir,output_dir)
      generate_report.zoneAnomaly(output_dir)
      open(os.path.join(output_dir, 'ready'), 'a').close()
    except:
      open(os.path.join(output_dir, 'error'), 'a').close()

  elif os.path.isfile(os.path.join(input_dir, 'ahuAnomaly')):
    print('Performing analysis using AHU anomaly function...')
    try:
      ahuAnomaly.execute_function(input_dir,output_dir)
      generate_report.ahuAnomaly(output_dir)
      open(os.path.join(output_dir, 'ready'), 'a').close()
    except:
      open(os.path.join(output_dir, 'error'), 'a').close()

  elif os.path.isfile(os.path.join(input_dir, 'energyBaseline')):
    print('Performing analysis using baseline energy function...')
    #Do baseline energy work here
    try:
      energyBaseline.execute_function(input_dir,output_dir)
      generate_report.energyBaseline(output_dir)
      open(os.path.join(output_dir, 'ready'), 'a').close()
    except:
      open(os.path.join(output_dir, 'error'), 'a').close()

  elif os.path.isfile(os.path.join(input_dir, 'endUseDisaggregation')):
    print('Performing analysis using end use disaggregation function...')
    #Do end use disaggregation work here
    try:
      endUseDisaggregation.execute_function(input_dir,output_dir)
      generate_report.endUseDisaggregation(output_dir)
      open(os.path.join(output_dir, 'ready'), 'a').close()
    except:
      open(os.path.join(output_dir, 'error'), 'a').close()

  elif os.path.isfile(os.path.join(input_dir, 'metadata')):
    print('Performing analysis using metadata function...')
    #Do metadata work here
    open(os.path.join(output_dir, 'ready'), 'a').close()
  
  elif os.path.isfile(os.path.join(input_dir, 'occupancy_wifi')):
    print('Performing analysis using occupancy function (Wi-Fi)...')
    #Do occupancy(Wi-Fi) work here
    try:
      occupancy.execute_function_wifi(input_dir,output_dir)
      generate_report.occupancy(output_dir, True)
      open(os.path.join(output_dir, 'ready'), 'a').close()
    except:
      open(os.path.join(output_dir, 'error'), 'a').close()
  
  elif os.path.isfile(os.path.join(input_dir, 'occupancy_motion')):
    print('Performing analysis using occupancy function (Motion-detection)...')
    #Do occupancy(motion-detection) work here
    try:
      occupancy.execute_function_motion(input_dir,output_dir)
      generate_report.occupancy(output_dir, False)
      open(os.path.join(output_dir, 'ready'), 'a').close()
    except:
      open(os.path.join(output_dir, 'error'), 'a').close()
  
  elif os.path.isfile(os.path.join(input_dir, 'complaintAnalytics')):
    print('Performing analysis using complaint analytics function...')
    #Do complaint analytics work here
    try:
      complaintAnalytics.execute_function(input_dir,output_dir)
      generate_report.complaintAnalytics(output_dir)
      open(os.path.join(output_dir, 'ready'), 'a').close()
    except:
      open(os.path.join(output_dir, 'error'), 'a').close()


def watch_queue():
  cwd = os.getcwd()
  queue_dir = os.path.join(cwd, 'userdata', 'unprocessed')
  
  for id in os.listdir(queue_dir):
    input_dir = os.path.join(queue_dir, id)
    if os.path.isdir(input_dir) and is_ready(input_dir):
      print(f'Processing {id}')
      process_work(id, input_dir)
      shutil.rmtree(input_dir)  

while True:
  print('Looking for work')
  watch_queue()
  time.sleep(SLEEP_TIME)