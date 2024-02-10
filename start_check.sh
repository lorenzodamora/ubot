#!/bin/bash
project_path="/home/ubuntu/Magnus/PycharmProj/ubot/"
cd "${project_path}"
source "${project_path}/.python_venv/bin/activate"
python -u check_output_1.py &
deactivate
