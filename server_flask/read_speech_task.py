# -*- coding: utf-8 -*-
"""
Created on Fri May 18 15:45:42 2018

@author: TOMAS
"""

import pandas as pd


file_path = 'D:\Doctorado\CI_Recording_Platform\Source_Code\static\\PLAKSS.xlsx'

def read_plakss(file_path):
    df = pd.read_excel(file_path)
    words = list(df['Symbol'])
    sound = list(df['Sound'])
    return words,sound
    
    