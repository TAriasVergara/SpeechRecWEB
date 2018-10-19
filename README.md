# SpeechRecWEB
Speech recording platform using a WEB interface

Current version:
- Only works with Windows64 due to the audio codec (fmedia, see requeriments.txt) version.
- Every text in the interface is in German.
- Audio is captured locally.

To execute the platform in windows, create the following batch script:
###########################BATCH FILE##########################################
@echo off
set dpath=%cd%\data\db
IF NOT EXIST %dpath% md %dpath%
start mongod --dbpath %dpath%
start python main.py
timeout 5 >nul
start "" http://127.0.0.1:5000
