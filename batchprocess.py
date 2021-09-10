#!/usr/bin/env python

import time
import os
import shutil

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
    open(os.path.join(output_dir, 'ready'), 'a').close()

  elif os.path.isfile(os.path.join(input_dir, 'ahuAnomaly')):
    print('Performing analysis using AHU anomaly function...')
    #Do AHU anomaly work here
    open(os.path.join(output_dir, 'ready'), 'a').close()

  elif os.path.isfile(os.path.join(input_dir, 'energyBaseline')):
    print('Performing analysis using baseline energy function...')
    #Do baseline energy work here
    open(os.path.join(output_dir, 'ready'), 'a').close()

  elif os.path.isfile(os.path.join(input_dir, 'endUseDisaggregation')):
    print('Performing analysis using end use disaggregation function...')
    #Do end use disaggregation work here
    open(os.path.join(output_dir, 'ready'), 'a').close()

  elif os.path.isfile(os.path.join(input_dir, 'metadata')):
    print('Performing analysis using metadata function...')
    #Do metadata work here
    open(os.path.join(output_dir, 'ready'), 'a').close()
  
  elif os.path.isfile(os.path.join(input_dir, 'occupancy')):
    print('Performing analysis using occupancy function...')
    #Do occupancy work here
    open(os.path.join(output_dir, 'ready'), 'a').close()
  
  elif os.path.isfile(os.path.join(input_dir, 'complaintAnalytics')):
    print('Performing analysis using complaint analytics function...')
    #Do complaint analytics work here
    open(os.path.join(output_dir, 'ready'), 'a').close()

def watch_queue():
  cwd = os.getcwd()
  queue_dir = os.path.join(cwd, 'userdata', 'unprocessed')
  
  for d in os.listdir(queue_dir):
    input_dir = os.path.join(queue_dir, d)
    if os.path.isdir(input_dir) and is_ready(input_dir):
      print(f'Processing {d}')
      process_work(d, input_dir)
      shutil.rmtree(input_dir)  

while True:
  print('Looking for work')
  watch_queue()
  time.sleep(SLEEP_TIME)