# SpeechRecWEB
Speech recording platform using a WEB interface

# Current version:
- Only works with Windows64 due to the audio codec (fmedia, see below in requeriments) version.
- Every text in the interface is in German.
- Audio is captured locally.

# To execute the platform in windows, create the following batch script:
@echo off
set dpath=%cd%\data\db
IF NOT EXIST %dpath% md %dpath%
start mongod --dbpath %dpath%
start python main.py
timeout 5 >nul
start "" http://127.0.0.1:5000

# Requeriments
Windows64.

python 3 or higher.

# #############Speech recording#################################
Recordings are capture using fmedia: http://fmedia.firmdev.com/

# ##########################From Anaconda prompt############################
conda install -c anaconda mongodb

conda install -c anaconda pymongo 

conda install -c anaconda flask-login 
