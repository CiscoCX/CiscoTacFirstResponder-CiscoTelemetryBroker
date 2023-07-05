#!/usr/bin/python3

__author__ = "CTB TAC First Responders"
__copyright__ = "Copyright 2023, Cisco Systems Inc."
__version__ = "1.0"
__status__ = "Production"

from datetime import datetime, timezone
from subprocess import check_output
import subprocess
import os
import logging
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-c", "--case", help="The case number to attach the files to", required=True)
parser.add_argument("-t", "--token", help="The token to upload files to cxd.cisco.com", required=True)
args = parser.parse_args()
case = str(args.case)
token = str(args.token)

def root_check():
    return os.geteuid() == 0

def print_log(msg, screen=False, log=False, color=None, level='info'):
    if screen:
        color_code = {'red': '\033[91m', 'green': '\033[92m'}.get(color, '')
        print(f'{color_code}{msg} \033[00m' if color_code else msg)
    if log:
        logging_func = getattr(logging, level)
        logging_func(msg)

def make_filename():
    curdate = datetime.now(timezone.utc).strftime('%Y%m%d.%H%M')
    model = "awk -F '[=]' '/APPLIANCE_TYPE/ {print $2}' /etc/titanos_version"
    serial = "tr -d '[:space:]' < /sys/class/dmi/id/product_serial"
    get_model = check_output(model, shell=True, text=True).strip()
    get_serial = check_output(serial, shell=True, text=True).strip()
    filename = f"mayday-{get_model}-{get_serial}.{curdate}.tar.gz"
    return filename

def make_mayday_file():
    global mayday_filename
    mayday_filename = make_filename()
    subprocess.run(["/opt/titan/bin/mayday","-o",f"/tmp/{mayday_filename}"],stdout = subprocess.DEVNULL)

def upload_file(case, token, f_name):
    command = ["curl", "-k", "--progress-bar", f"https://{case}:{token}@cxd.cisco.com/home/", "--upload-file", f_name]
    try:
        subprocess.check_output(command)
        print_log(f'`{f_name}` successfully uploaded to {case}', screen=True, log=True, color='green', level='info')
    except subprocess.CalledProcessError as e:
        print_log(f'[FAILURE] Failed to upload `{f_name}` to {case}.', screen=True, color='red')
        print_log(f'Upload failed with the following error:\n----------\n{e}\n----------', log=True, level='warn')
        print_log('Notify Cisco TAC of Failure to upload for further assistance', log=True, level='warn')

def main():
    print("\r\n*** Creating Support Bundle, this may take some time")
    make_mayday_file()
    print("\nUploading file to TAC Case. This may take some time.")
    upload_file(case, token, f"/tmp/{mayday_filename}")

if root_check():
    main()
else:
    print("You are not root, re-run this script as root. Exiting.")
  
