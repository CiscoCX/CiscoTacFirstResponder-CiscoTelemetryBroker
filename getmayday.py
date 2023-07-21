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

try:
    import requests
    rqst_avail = True
except ImportError:
    rqst_avail = False

parser = ArgumentParser()
subparsers = parser.add_subparsers(dest="command", required=True)
parser_upload = subparsers.add_parser("upload")
parser_upload.add_argument("-c", "--case", help="The case number to attach the files to", required=True)
parser_upload.add_argument("-t", "--token", help="The token to upload files to cxd.cisco.com", required=True)
parser_no_upload = subparsers.add_parser("no-upload")
args = parser.parse_args()
if args.command == "upload":
    case = str(args.case)
    token = str(args.token)

if args.command == "no-upload":
    pass

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
    subprocess.run(["/opt/titan/bin/mayday","-o",f"/tmp/{mayday_filename}"])

def upload_file(case, token, f_name):
    if rqst_avail:
        try:
            with open(f_name, "rb") as data:
                response = requests.put(
                    f"https://cxd.cisco.com/home/{f_name}",
                    data=data, auth=requests.auth.HTTPBasicAuth(case, token),
                    headers={"accept": "application/json"})
                response.raise_for_status()
                print_log(f"`{f_name}` was uploaded to {case}", screen=True, log=True, color="green", level="info")
        except requests.HTTPError as rqst_err:
            print_log(f"[FAILURE] Failed to upload `{f_name}` to {case} with token {token}.", screen=True, color="red" )
            print_log(f"HTTP error:\n----------\n{rqst_err}\n----------", log=True, level="warning" )
            exit()
        except FileNotFoundError as file_err:
            print_log(f"[FAILURE] Failed to upload to {case}.", screen=True, log=True, color="red", level="warning")
            print_log(f"File Error {file_err}")
            exit()
    else:
        command = ["curl","-k","--progress-bar",f"https://{case}:{token}@cxd.cisco.com/home/","--upload-file"]
        try:
            output = subprocess.check_output(command)
            if output:
                print_log(f"[FAILURE] (cURL) Failed to upload to {case} with token {token}.", screen=True, color="red")
                print_log(f"Process error:\n----------\n{output}\n----------", log=True, level="warning")
                exit()
            print_log(f"(cURL) `{f_name}` was uploaded to {case}.", screen=True, log=True, color="green", level="info")
        except subprocess.CalledProcessError as e:
            print_log(f"[FAILURE] Failed to upload `{f_name}` to {case} with token {token}.", screen=True, color="red")
            print_log(f"Process error:\n----------\n{e}\n----------", log=True, level="warning")
            print_log("Notify Cisco TAC of Failure to upload for further assistance", log=True, level="warning")
            exit()

def main():
    print("\r\n*** Creating Support Bundle, this may take some time")
    make_mayday_file()
    if args.command == "upload":
        print("\nUploading file to TAC Case. This may take some time.")
        upload_file(case, token, f"/tmp/{mayday_filename}")
    else:
        pass

if root_check():
    main()
else:
    print("You are not root, re-run this script as root. Exiting.")
