#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  12 14:44:02 2017

@author: gita
"""

import server_flask.speech_recording as sperec #Capture audio from mic using fmedia
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, login_user,logout_user,UserMixin, current_user
from pymongo import MongoClient #Manejos de base de datos
#import pprint
#import numpy as np
import os,shutil#,sys
import pandas as pd
import time
import hashlib
import json
#import subprocess
 
#Directorio de proyecto. Es una entrada desde BATCH (WINDOWS). 
main_path = os.path.dirname(os.path.abspath(__file__))

##Start mongoDB (Windows is stupid as fuck!)
#dbpath = main_path+'\\data\\db'
#if os.path.isdir(dbpath)==False:
#   os.makedirs(dbpath)
#subprocess.Popen(['mongod','--dbpath',dbpath],stdout=subprocess.PIPE)

#Name of the temporal recordings folder
temp_rec= 'temp_rec'

#Name of the final recording folder
recs = 'users\\recordings'

#Name of the metadata
metas = 'users\\questionaries'

##Crear Base de datos
##Crear cliente
client = MongoClient()
#
##Crear database
#client.drop_database('Speaker_database')
db = client.Speaker_database

##Crear colecciones
Speakers_data = db.Speaker_collection
Speakers_data_Scores = db.Speaker_collection_Scores


# App config.
DEBUG = True
#LOGIN_DISABLED = True #Solo habilitar para pruebas.
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

######################################################
######################################################
#               Login information
######################################################
######################################################
#Manejo de usuarios
login_manager = LoginManager()
login_manager.init_app(app)#Configurar app para login
login_manager.login_view = "login" #ir a esta html cuando se requiera el login

usertag = "speakerID"

#Usuario para login
class User(UserMixin):
    def __init__(self,usr_id):
        self.id = usr_id

    def __repr__(self):
        return '<User {}>'.format(self.usr_id)

#Cargar usuarios
users=[]
for docs in Speakers_data.find():
    usr_id=docs[usertag]
    users.append(User(usr_id))

@login_manager.user_loader
def load_user(usr_id):
    return User(usr_id)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#Codificar/decodificar contrasenna
def code_hash_pass(password):
    salt = os.urandom(hashlib.blake2b.SALT_SIZE)
    salt_hash = hashlib.blake2b(salt=salt)
    salt_hash.update(password.encode('utf-8'))
    hash_password = salt_hash.digest()
    return hash_password,salt

def deco_hash_pass(password,salt):
    salt_hash = hashlib.blake2b(salt=salt)
    salt_hash.update(password.encode('utf-8'))
    hash_password = salt_hash.digest()
    return hash_password
########################################################
#Verificar credenciales
def get_credentials(usr,userpass):
    temp = Speakers_data.find({usertag:usr}).count()
#    print(temp)
    if temp == 0:
        return False
    else:
        results = Speakers_data.find({usertag:usr})[0]
        if deco_hash_pass(userpass,results['salt']) == results['password']:
            return True
        return False
########################################################
#get user collection
def get_user_collection():
    usr_id = current_user.id
    spkINFO = Speakers_data.find({usertag:usr_id})[0]
    spkINFO.pop('_id', None)#JSON CANT SERIALIZED ObjectID 
    return spkINFO

def get_current_date():
     
     #Get date
     day = str(time.localtime()[2])
     if len(day)==1:
          day = '0'+day
     month = str(time.localtime()[1])
     if len(month)==1:
          month = '0'+month
     year = str(time.localtime()[0])
     
     date = year+'-'+month+'-'+day
     return date

#######################################################
def rec_folder_name():
     spkINFO = get_user_collection()
     date = get_current_date()
     folder_name = spkINFO[usertag]+'\\'+date
     return folder_name
     
#####CHEKC IF THE RECORDER IS ON BUT NOT PROPERLY FINISHED
def check_rec_pend():
    if os.path.isdir(main_path+'\\'+temp_rec)==True:
         #Check if there is any recording ongoing and cancel the process
         sperec.stop_recording()#Stop recording
         time.sleep(2)
         shutil.rmtree(main_path+'\\'+temp_rec)

######################################################
######################################################
#               INDEX AND NAVEGATION BAR
######################################################
######################################################
@app.route("/", methods=['GET', 'POST'])
def index():
    check_rec_pend()
    LogFlag = "False"
    if current_user.is_active==True:
        LogFlag = "True"
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('index.html',LogFlag=json.dumps(LogFlag))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_active==True:
         logout_user()
         
    if request.method == 'POST':
         lastname = request.form['reg_lastname']
         name = request.form['reg_name']
         bday = request.form['reg_birthday']
         speakerID = request.form['reg_spkID']
         gender = request.form['reg_gender']
         #Label to indicate if the speaker is a patient or a healthy control
         label = request.form['reg_spklabel']
         mtongue = request.form['reg_mothertongue']
         dialect = request.form['reg_dialekt']
         
         #Create login information
         hpassw,salt = code_hash_pass(speakerID) 
         
         ##Create database
         Speaker_index_data = {
                              "name":name,
                              "lastname":lastname,
                              "birthdate":bday,
                              "gender":gender,
                              usertag:speakerID,
                              "password":hpassw,
                              "salt":salt,
                              "label":label, 
                              "nativelanguage": mtongue,
                              "dialect":dialect
                              }
         
         temp = Speakers_data.find({usertag:speakerID}).count()
         if temp!=0:
              Speakers_data.update_one({usertag:speakerID},{"$set":Speaker_index_data})
         else:
              Speakers_data.insert_one(Speaker_index_data)
              
         #Addtional information in case of that the speaker is a patient
         if label=='CI':
              losshearing = request.form['reg_losshearing']
              if losshearing=='years':
                   losstime = request.form['reg_yearloss']
              elif losshearing=='childhood':
                   losstime = 'Ertaubung im Kindesalter'
              else:
                   losstime = 'Ertaubung im Erwachsenenalter'

              Speaker_index_data = {
                              "hearingloss":losstime,
                              }
              Speakers_data.update_one({usertag:speakerID},{"$set":Speaker_index_data})
              
         #Login user after registration
         user = User(speakerID)
         login_user(user)
         
         return redirect(url_for('CI_speech_tasks'))
    return render_template('register.html')

@app.route("/registration_completed", methods=['GET', 'POST'])
@login_required
def registration_completed():
    if request.method == 'POST':
        return redirect(url_for('registration_completed'))
    return render_template('registration_completed.html')

@app.route("/Fragebogen", methods=['GET', 'POST'])
@login_required
def Fragebogen():
    if request.method == 'POST':
        return redirect(url_for('Fragebogen'))
    return render_template('Fragebogen.html')

@app.route("/downloads", methods=['GET', 'POST'])
@login_required
def downloads():
    return render_template('downloads.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_active==True:
         logout_user()
    table = []     
    loghid = 'true'
    if request.method == 'POST': 
         
        username = request.form['log_search']
        if username!='':
             speakerID = Speakers_data.find({usertag:username})[0][usertag]
             #Login user after registration
             user = User(speakerID)
             login_user(user)
             return redirect(url_for('CI_speech_tasks'))
             
        radopt = request.form['log_patient']
        if radopt=='spkID':
             username = request.form['log_spkID']
             speakerID = Speakers_data.find({usertag:username})[0][usertag]
             #Login user after registration
             user = User(speakerID)
             login_user(user)
             return redirect(url_for('CI_speech_tasks'))             
             
        elif radopt=='spkbday':
               bday = request.form['log_inputbirth']
               for docs in Speakers_data.find({"birthdate":bday}).sort("lastname"):
                   docs.pop('_id', None)#JSON CANT SERIALIZED ObjectID
                   table.append([docs["lastname"],docs["name"],docs['birthdate'],docs[usertag]])
                   
        else:
               for docs in Speakers_data.find().sort("lastname"):
                   docs.pop('_id', None)#JSON CANT SERIALIZED ObjectID
                   table.append([docs["lastname"],docs["name"],docs['birthdate'],docs[usertag]])
         
        loghid = 'false'          
        return render_template('login.html',**{'table':table},loghid=loghid)
    return render_template('login.html',loghid=loghid)

######################################################
######################################################
#               SPEECH RECORDING TASKS
#               COCHLEAR IMPLANT USERS
######################################################
######################################################
def check_recordings(rec_path):
    if os.path.isdir(rec_path)==False:
        os.makedirs(rec_path)
        
    rec_list = os.listdir(rec_path)
    rec_list.sort()
    return len(rec_list)

def store_recordings(src_path,dst_path,task):
     if os.path.isdir(dst_path+'\\'+task)==False:
        shutil.copytree(src_path,dst_path+'\\'+task)
     else:
          count = 1
          listfolder = os.listdir(dst_path)
          for f in listfolder:
               if f.find(task)!=-1:
                    count = count+1
          shutil.copytree(src_path,dst_path+'\\'+task+str(count))
         
#Speech tasks index
@app.route("/CI_speech_tasks", methods=['GET', 'POST'])
@login_required
def CI_speech_tasks():     
     check_rec_pend()
     spkINFO = get_user_collection()
     meta_flag = 'on'
     if spkINFO['label']=='gesunde Kontrolle':
          meta_flag = 'off'
     if request.method == 'POST':   
          rec_comments = request.form['citest_recomments']   
          date = get_current_date()
          Speakers_data_Scores.update_one({usertag:spkINFO[usertag]},{"$set":{date+'_'+'Comments':rec_comments}})
#          pprint.pprint(Speakers_data_Scores.find({usertag:spkINFO[usertag]})[0])
     return render_template('CI_speech_tasks.html',**{'spkINFO':spkINFO},meta_flag = json.dumps(meta_flag))

@app.route("/module_PLAKSS", methods=['GET', 'POST'])
@login_required
def module_PLAKSS():   
    df = pd.read_excel(main_path+'\\static\\PLAKSS.xlsx')#Read file with PLAKKS' words
    ###########################################################################
    #                    CREATE FOLDER TO STORE AUDIO FILES
    ###########################################################################
    modname = 'module_PLAKSS'
    folder_name = rec_folder_name()
    rec_path = main_path+'\\'+temp_rec+'\\'+folder_name+'\\'+modname
    #--------------------------------------------------------------------------
    idx_word  = check_recordings(rec_path)#Number of files 
    ###########################################################################
    #                    LOAD PLAKKS WORD
    ###########################################################################
    if idx_word==len(df['Symbol']):#Check if every word was already displayed
        sperec.stop_recording()#Stop recording
        time.sleep(0.5)        
        #cuando termina debe copiar toda la carpeta
        dst_path = main_path+'\\'+recs+'\\'+folder_name
        store_recordings(rec_path,dst_path,modname)
        time.sleep(0.5)        
        shutil.rmtree(rec_path)
        return redirect(url_for('CI_speech_tasks'))
    
    word = ''#df['Symbol'][idx_word]#Word to display
    sound = rec_path+'\\'+df['Sound'][idx_word]#Words without special characters
    progr = round((idx_word+0.0)/(len(df['Symbol'])),2)*100
    recB = 'START'    
    if request.method == 'POST':    
        ###########################################################################
        #       STORE AUDIO FILE AND RELOAD PAG TO DISPLAY NEXT THE WORD
        ###########################################################################
        rec_flag = request.form['rec_button']    
        if rec_flag=="True":
             recB = 'WEITER'
             if idx_word==(len(df['Symbol'])-1):
                 recB = 'FERTIG'
             sperec.start_recording(filename=sound)#Start recording
             word = df['Symbol'][idx_word]#Word to display
        else:
             recB = 'START'
             sperec.stop_recording()#Stop recording
             time.sleep(1)             
    return render_template('module_PLAKSS.html',word=word,recB=recB,progr=progr)

@app.route("/module_Rhino", methods=['GET', 'POST'])
@login_required
def module_Rhino():            
    df = pd.read_excel(main_path+'\\static\\RHINO.xlsx')#Read file with PLAKKS' words
    modname = 'module_Rhino' 
    folder_name = rec_folder_name()
    rec_path = main_path+'\\'+temp_rec+'\\'+folder_name+'\\'+modname
    idx_sent  = check_recordings(rec_path)#Number of files
    
    if idx_sent==len(df['Symbol']):#Check if every sentence was recorded
        sperec.stop_recording()#Stop recording
        time.sleep(0.5)        
        #cuando termina debe copiar toda la carpeta
        dst_path = main_path+'\\'+recs+'\\'+folder_name
        store_recordings(rec_path,dst_path,modname)
        time.sleep(0.5)
        shutil.rmtree(rec_path)
        return redirect(url_for('CI_speech_tasks'))
 
    sentence = ''#df['Symbol'][idx_sent]#Word to display
    sound = rec_path+'\\'+df['Tag'][idx_sent]    
    progr = round((idx_sent+0.0)/(len(df['Symbol'])),2)*100
    recB = 'START'    
    if request.method == 'POST':     
#        recB = 'WEITER'
        ###########################################################################
        #       STORE AUDIO FILE AND RELOAD PAG TO DISPLAY NEXT THE SENTENCE
        ###########################################################################
        rec_flag = request.form['rec_button']    
        if rec_flag=="True":
             recB = 'WEITER'
             if idx_sent==len(df['Symbol'])-1:
                 recB = "FERTIG"
             sperec.start_recording(filename=sound)#Start recording
             sentence = df['Symbol'][idx_sent]#Word to display
        else:
             recB = 'START'
             sperec.stop_recording()#Stop recording
             time.sleep(1)
        
    return render_template('module_Rhino.html',sentence=sentence,recB=recB,progr=progr)

@app.route("/module_Nordwind", methods=['GET', 'POST'])
@login_required
def module_Nordwind():
    modname  = 'module_Nordwind'
    df = pd.read_excel(main_path+'\\static\\Nordwind.xlsx')
    folder_name = rec_folder_name()
    rec_path = main_path+'\\'+temp_rec+'\\'+folder_name+'\\'+modname
    check_recordings(rec_path)#Number of files

    name = rec_path+'\\Nordwind'
    title = ''#df['Titulo'][0]
    text = ''#df['Texto'][0]
    
    recB = 'START'    
    if request.method == 'POST':     
        rec_flag = request.form['rec_button']    
        if rec_flag=="True":
             recB = 'STOP'
             sperec.start_recording(filename=name)#Start recording
             title = df['Titulo'][0]
             text = df['Texto'][0]
        else:
             recB = 'START'
             sperec.stop_recording()#Stop recording
             time.sleep(0.5)        
             #cuando termina debe copiar toda la carpeta
             dst_path = main_path+'\\'+recs+'\\'+folder_name
             store_recordings(rec_path,dst_path,modname)
             time.sleep(0.5)
             shutil.rmtree(rec_path)
             return redirect(url_for('CI_speech_tasks'))
             
    return render_template('module_Nordwind.html',title=title,text=text,recB=recB)

@app.route("/module_Cookie", methods=['GET', 'POST'])
@login_required
def module_Cookie():            
    modname = 'module_Cookie'
    folder_name = rec_folder_name()
    rec_path = main_path+'\\'+temp_rec+'\\'+folder_name+'\\'+modname
    check_recordings(rec_path)#Number of files
    name = rec_path+'\\Cookie'

    recB = 'START'    
    if request.method == 'POST':     
        rec_flag = request.form['rec_button']    
        if rec_flag=="True":
             recB = 'STOP'
             sperec.start_recording(filename=name)#Start recording
        else:
             recB = 'START'
             sperec.stop_recording()#Stop recording
             time.sleep(0.5)        
             #cuando termina debe copiar toda la carpeta
             dst_path = main_path+'\\'+recs+'\\'+folder_name
             store_recordings(rec_path,dst_path,modname)
             time.sleep(0.5)
             shutil.rmtree(rec_path)
             return redirect(url_for('CI_speech_tasks'))
             
    return render_template('module_Cookie.html',recB=recB)


@app.route("/module_PATAKA", methods=['GET', 'POST'])
@login_required
def module_PATAKA():            
    modname = 'module_PATAKA'
    folder_name = rec_folder_name()
    rec_path = main_path+'\\'+temp_rec+'\\'+folder_name+'\\'+modname
    check_recordings(rec_path)#Number of files
    name = rec_path+'\\PATAKA'   
    recB = 'START'    
    text = ''
    if request.method == 'POST':     
        rec_flag = request.form['rec_button']    
        if rec_flag=="True":
             recB = 'FERTIG'
             sperec.start_recording(timerec=7,filename=name)#Start recording
             text = 'PATAKA PATAKA PATAKA PATAKA...' 
        else:
             time.sleep(0.5)        
             #cuando termina debe copiar toda la carpeta
             dst_path = main_path+'\\'+recs+'\\'+folder_name
             store_recordings(rec_path,dst_path,modname)
             time.sleep(0.5)
             shutil.rmtree(rec_path)
             return redirect(url_for('CI_speech_tasks'))
    return render_template('module_PATAKA.html',text=text,recB=recB)

@app.route("/module_VoiceSentences", methods=['GET', 'POST'])
@login_required
def module_VoiceSentences():            
    df = pd.read_excel(main_path+'\\static\\VSentences.xlsx')#Read file with PLAKKS' words
    modname = 'module_VoiceSentences' 
    folder_name = rec_folder_name()
    rec_path = main_path+'\\'+temp_rec+'\\'+folder_name+'\\'+modname
    idx_sent  = check_recordings(rec_path)#Number of files
    
    if idx_sent==len(df['Symbol']):#Check if every sentence was recorded
        sperec.stop_recording()#Stop recording
        time.sleep(0.5)        
        #cuando termina debe copiar toda la carpeta
        dst_path = main_path+'\\'+recs+'\\'+folder_name
        store_recordings(rec_path,dst_path,modname)
        time.sleep(0.5)
        shutil.rmtree(rec_path)
        return redirect(url_for('CI_speech_tasks'))
 
    sentence = ''#df['Symbol'][idx_sent]#Word to display
    sound = rec_path+'\\'+df['Tag'][idx_sent]    
    progr = round((idx_sent+0.0)/(len(df['Symbol'])),2)*100
    recB = 'START'    
    if request.method == 'POST':     
#        recB = 'WEITER'
        ###########################################################################
        #       STORE AUDIO FILE AND RELOAD PAG TO DISPLAY NEXT THE SENTENCE
        ###########################################################################
        rec_flag = request.form['rec_button']    
        if rec_flag=="True":
             recB = 'WEITER'
             if idx_sent==len(df['Symbol'])-1:
                 recB = "FERTIG"
             sperec.start_recording(filename=sound)#Start recording
             sentence = df['Symbol'][idx_sent]#Word to display
        else:
             recB = 'START'
             sperec.stop_recording()#Stop recording
             time.sleep(1)
        
    return render_template('module_VoiceSentences.html',sentence=sentence,recB=recB,progr=progr)

######################################################
######################################################
#               FORMS AND METADATA
#               COCHLEAR IMPLANT USERS
######################################################
######################################################
#Speech tasks index
@app.route("/form_fragebogen", methods=['GET', 'POST'])
@login_required
def form_fragebogen():     
    #Check if there is any recording ongoing and cancel the process
#    sperec.stop_recording()#Stop recording
    usr_id = current_user.id
    spkINFO = Speakers_data.find({usertag:usr_id})[0]
    spkINFO.pop('_id', None)#JSON CANT SERIALIZED ObjectID 
    answers = {}    
    form_name = 'Fragebogen'
#    if form_name in spkINFO:
#         answers = spkINFO[form_name]
    if request.method == 'POST':
         for j in request.form:                
              temp = request.form.getlist(j)
              if (j!='fragen_submit'):
                   answers[j] = [temp]
                   if len(answers[j])==1:
                         answers[j]=answers[j][0][0]        
         date = request.form['fragen_datum']
         temp = Speakers_data_Scores.find({usertag:usr_id}).count()
         if temp!=0:
              Speakers_data_Scores.update_one({usertag:usr_id},{"$set":{date+'_'+form_name:answers}})
         else:
              Speakers_data_Scores.insert_one({usertag:usr_id,date+'_'+form_name:answers})
         return redirect(url_for('CI_speech_tasks'))
         
    return render_template('form_fragebogen.html',**{'spkINFO':spkINFO})#,Rtas=json.dumps(answers))

#Speech tasks index
@app.route("/form_ASKUfragen", methods=['GET', 'POST'])
@login_required
def form_ASKUfragen():     
    #Check if there is any recording ongoing and cancel the process
#    sperec.stop_recording()#Stop recording
    usr_id = current_user.id
    spkINFO = Speakers_data.find({usertag:usr_id})[0]
    spkINFO.pop('_id', None)#JSON CANT SERIALIZED ObjectID 
    answers = {}    
    form_name = 'ASKU-Score'
#    if form_name in spkINFO:
#         answers = spkINFO[form_name]
    if request.method == 'POST':
         for j in request.form:                
              temp = request.form.getlist(j)
              if (j!='ASKU_submit'):
                   answers[j] = [temp]
                   if len(answers[j])==1:
                         answers[j]=answers[j][0][0]        
         date = request.form['ASKU_datum']
         temp = Speakers_data_Scores.find({usertag:usr_id}).count()
         if temp!=0:
              Speakers_data_Scores.update_one({usertag:usr_id},{"$set":{date+'_'+form_name:answers}})
         else:
              Speakers_data_Scores.insert_one({usertag:usr_id,date+'_'+form_name:answers})
              
         return redirect(url_for('CI_speech_tasks'))
         
    return render_template('form_ASKUfragen.html',**{'spkINFO':spkINFO})#,Rtas=json.dumps(answers))

#Speech tasks index
@app.route("/form_CAP2", methods=['GET', 'POST'])
@login_required
def form_CAP2():     
    spkINFO = get_user_collection()
    answers = {}    
    form_name = 'CAP-II-Score'
#    if form_name in spkINFO:
#         answers = spkINFO[form_name]
    if request.method == 'POST':
         for j in request.form:                
              temp = request.form.getlist(j)
              if (j!='CAP2_submit'):
                   answers[j] = [temp][0]
                   if len(answers[j])==1:
                         answers[j]=answers[j][0]     
         date = request.form['CAP2_datum']
         temp = Speakers_data_Scores.find({usertag:usr_id}).count()
         if temp!=0:
              Speakers_data_Scores.update_one({usertag:usr_id},{"$set":{date+'_'+form_name:answers}})
         else:
              Speakers_data_Scores.insert_one({usertag:usr_id,date+'_'+form_name:answers})              
              
#         pprint.pprint(Speakers_data_Scores.find({usertag:usr_id})[0])
#         answers = Speakers_data_Scores.find({usertag:usr_id})[0]
#         answers = answers[date+'_'+form_name]
         return redirect(url_for('CI_speech_tasks'))
#         return render_template('form_CAP2.html',**{'spkINFO':spkINFO},Rtas=json.dumps(answers))
         
    return render_template('form_CAP2.html',**{'spkINFO':spkINFO},Rtas=json.dumps(answers))

if __name__ == "__main__":
#     prompt=' <folder of platform>'
     app.run()
