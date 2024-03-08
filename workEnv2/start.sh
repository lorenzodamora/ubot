#!/bin/bash
project_path="/home/ubuntu/Magnus/PycharmProj/ubot2/"
cd "${project_path}"
source "${project_path}/.python_venv/bin/activate"
cd "workEnv"
python -u main.py mMain.py >> ../output.txt 2>&1
