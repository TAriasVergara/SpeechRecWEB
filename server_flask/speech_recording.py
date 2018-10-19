# -*- coding: utf-8 -*-
"""
Created on Fri May 18 09:37:07 2018

@author: TOMAS
"""

import subprocess
#import time

import os
code_path = os.path.dirname(os.path.abspath(__file__))


def start_recording(timerec=0,fmediaOS='win64',res='int16',rate='44100',chann='mono',filename='recording'):
    """
    Speech recording for Windows using fmedia: http://fmedia.firmdev.com/
    inputs:
        :param timerec (INT): If is greater than '0', then it will record audio up to the 
                              time set in this variable(measure in seconds).
                              If is '0', then it will record only when you call the 
                              'stop_recording()' function.
                              
        :param fmediaOS (STR): operative system and arichitecture for fmedia. Options
                              win64: Windows 64-bits (Default)
                              win32: Windows 32-bits (NOT IMPLEMENTED)
                              lin64: Linux 64-bits (NOT IMPLEMENTED)
                              lin32: Linux 32-bits (NOT IMPLEMENTED)
    """
    #####################################################
    #ADD OTHER FOLDERS HERE for different architectures of fmedia
    if fmediaOS == 'win64':
        exe_path = code_path+'\\fmedia_windows_64\\fmedia'
    
    ######################################################
    #Set audio recorder options
    file_format = '--format='+res
    file_rate = '--rate='+rate
    file_channel = '--channels='+chann
    audio_name = filename+'.wav'
    if timerec==0:
        subprocess.Popen([exe_path,
                          '--record',
                          file_format,
                          file_rate,
                          file_channel,
                          '-o',
                          audio_name,
                          '--globcmd=listen'], stdout=subprocess.PIPE)    
    elif timerec>0:
        timerec = '--until='+str(timerec)
        subprocess.Popen([exe_path,
                          '--record',
                          timerec,
                          file_format,
                          file_rate,
                          file_channel,
                          '-o',
                          audio_name,
                          '--globcmd=listen'], 
                          stdout=subprocess.PIPE)  
    
def stop_recording(fmediaOS='win64'):
    if fmediaOS == 'win64':
        exe_path = code_path+'\\fmedia_windows_64\\fmedia.exe'
    
    subprocess.Popen([exe_path,
                      '--globcmd=stop'],
                       stdout=subprocess.PIPE)

##############################################################################################
##############################################################################################
##############################################################################################