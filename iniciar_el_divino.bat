@echo off
cd /d %~dp0
start "" http://192.168.10.4:8050
python app.py
