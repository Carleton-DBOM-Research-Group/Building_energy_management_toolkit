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

  # do whatever work
  open(os.path.join(output_dir, 'result.png'), 'a').close()
  
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