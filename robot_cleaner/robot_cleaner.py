#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
current_module:: robot_cleaner.py
created_by:: Darren Xie
created_on:: 04/25/2024

Scheduled clean specific files from the specific direction.
As a microservice, accept POST call
"""
import datetime
import fnmatch
import json
import os
import re
import threading
import time
from typing import Dict, List
from pathlib import Path
import ntpath

import schedule
from flask import Flask, jsonify

CONFIG_FILE = "robot_cleaner_config.json"
FILE_PATH = "file_path"
FILENAME_PATTERN = "filename_pattern"
KEEP_DAYS = "keep_days"
START_TIME = "start_time"
PORT = "port"
MAX_KEEP = "max"

app = Flask(__name__)


def get_args():
    """
    Get arguments, including input file and output filename.
    The default path is the current path.
    """
    try:
        with open(Path.home()/CONFIG_FILE, 'r') as fh:
            json_data = json.load(fh)
        return json_data
    except IOError:
        raise IOError(f"IOError: Cannot open file {CONFIG_FILE}")
    except Exception:
        raise Exception(f"Exception: Cannot open file {CONFIG_FILE}")


config_dict: Dict = get_args()


@app.route('/cleanup', methods=['POST'])
def cleanup_exes(schedule_run=False):
    # Update Config
    global config_dict
    config_dict = get_args()
    # Calculate file age threshold
    now = datetime.datetime.now()
    age_threshold = now - datetime.timedelta(days=config_dict[KEEP_DAYS])
    # Calculate file pattern
    regex = fnmatch.translate(config_dict[FILENAME_PATTERN])
    reobj = re.compile(regex)

    directory = config_dict[FILE_PATH]
    if not directory:
        if schedule_run:
            return f"error: Directory is required"
        else:
            return jsonify({'error': 'Directory is required'}), 400

    if not os.path.exists(directory):
        if schedule_run:
            return f"error: Directory does not exist"
        else:
            return jsonify({'error': 'Directory does not exist'}), 404

    try:
        files_removed: List = []
        matched_files: List = []
        latest_files: List = []
        for item in os.listdir(directory):
            file_path = os.path.join(directory, item)
            if os.path.isfile(file_path):
                if reobj.match(item):
                    matched_files.append(file_path)

        for i in range(config_dict[MAX_KEEP]):
            latest_file = max(matched_files, key=os.path.getctime)
            latest_files.append(latest_file)
            matched_files.remove(latest_file)

        for item in matched_files:
            os.remove(item)
            files_removed.append(ntpath.basename(item))
        if schedule_run:
            return f"Cleanup successful. files_removed: {files_removed}"
        else:
            return jsonify({'message': 'Cleanup successful', 'files_removed': files_removed}), 200
    except Exception as e:
        if schedule_run:
            return f"error: {str(e)}"
        else:
            return jsonify({'error': str(e)}), 500


def sched_job():
    cleanup_exes(True)


def schedule_clean():
    schedule.every().day.at(config_dict[START_TIME]).do(sched_job)
    while True:
        schedule.run_pending()
        time.sleep(1)


def service_clean():
    app.run(debug=True, port=config_dict[PORT], use_reloader=False)


if __name__ == '__main__':
    schedule_thread = threading.Thread(target=schedule_clean)
    service_thread = threading.Thread(target=service_clean)

    schedule_thread.start()
    service_thread.start()
