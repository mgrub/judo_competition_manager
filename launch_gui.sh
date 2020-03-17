#! /bin/bash
source ~/programs/python_virtualenv/py3_judo_competition_manager/bin/activate
export FLASK_APP=judo_competition_manager/web_gui.py
flask run