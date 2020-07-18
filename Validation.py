# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 14:03:45 2020

@author: julie
"""

from IPython import get_ipython
import pandas as pd
import PySimpleGUI as sg
import numpy as np

#Clear's console and variables
get_ipython().magic('reset -f')
get_ipython().magic('clear')

#Popup window with instructions 
sg.theme('LightBlue2')

sg.popup_ok('The following program was designed to analyze athlete data for the validation of timing gates', 
            title = 'Timing Gate Validation')
sg.popup_ok_cancel('This program will prompt you to upload a .csv file. Follow these instructions carefully as everything is case sensitive! This file MUST be formatted in the following way:',
            ' - Five columns', ' - One row containing column names',
            ' - Column names: Athlete, Trial, Radar, TimingGate, Optojump',
            title = 'Instructions')

#Select .csv file for analysis 
File = sg.popup_get_file('Please select the .csv file for analyzing')
data = pd.read_csv(File, header = 0, keep_default_na = False)

#data = pd.read_csv('C:/Users/julie/GitHub/Validation/VelocityDataNew.csv',header = 0,
                 #  keep_default_na = False) #Keep athlete 'NA' from becoming NaNs

#Sorting the data by athlete and trial in ascending order
data.sort_values(['Athlete', 'Trial'], inplace = True, ascending = [True, True])

#Create New DataFrame with max and average velocities for each athlete
NewData = pd.DataFrame()
NewData[['Radar_Max', 'Radar_Avg']] = data.groupby('Athlete')['Radar'].aggregate([max, np.mean])
NewData[['TimingGate_Max', 'TimingGate_Avg']] = data.groupby('Athlete')['TimingGate'].aggregate([max, np.mean])
NewData[['Optojump_Max', 'Optojump_Avg']] = data.groupby('Athlete')['Optojump'].aggregate([max, np.mean])
NewData.reset_index(inplace = True)

#Visualizing data 
import matplotlib.pyplot as plt
fig1, axes = plt.subplots(2, figsize =(20,15))
fig1.suptitle('Instantaneous and Average Max Velocities')
NewData.plot(x = "Athlete", y = ["Radar_Max", "TimingGate_Max", "Optojump_Max"],
             kind = "bar", ax = axes[0], title = 'Instantaneous', rot = 45,
             legend = False, cmap = "Accent")
NewData.plot(x = "Athlete", y = ["Radar_Avg", "TimingGate_Avg", "Optojump_Avg"], 
             kind = "bar", ax = axes[1], title = 'Average', rot = 45,
             legend = False, cmap = "Accent")

font = {'family': 'DejaVu Sans',
        'weight': 'normal',
        'size' : 20}
plt.rc('font', **font)
fig1.legend(['Radar', 'Timing Gate', 'Optojump'], loc = 'upper right', frameon = False)
fig1.savefig('Max and avg velocity plot', bbox_inches = 'tight')
for ax in axes.flat:
    ax.set(xlabel = 'Athlete', ylabel = 'Velocity (m/s)')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
for ax in axes.flat:
    ax.label_outer()



