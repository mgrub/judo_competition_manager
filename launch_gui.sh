#! /bin/bash
source ~/programs/python_virtualenv/py3_judo_competition_manager/bin/activate
export FLASK_APP=rest_api/main.py
flask run