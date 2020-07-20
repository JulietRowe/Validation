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

# data = pd.read_csv('C:/Users/julie/GitHub/Validation/VelocityDataNew.csv',header = 0,
#                 keep_default_na = False) #Keep athlete 'NA' from becoming NaNs

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
fig1.suptitle('Instantaneous and Average Max Velocities', fontweight = "bold", size = 30)
NewData.plot(x = "Athlete", y = ["Radar_Max", "TimingGate_Max", "Optojump_Max"], ax = axes[0],
             kind = "bar", title = 'Instantaneous', rot = 45,
             legend = False, cmap = "Accent", fontsize = 26)
NewData.plot(x = "Athlete", y = ["Radar_Avg", "TimingGate_Avg", "Optojump_Avg"], ax = axes[1],
             kind = "bar", title = 'Average', rot = 45,
             legend = False, cmap = "Accent", fontsize = 26)
fig1.legend(['Radar', 'Timing Gate', 'Optojump'], loc = 'upper right', frameon = False, fontsize = 26)

for ax in axes.flat:
    ax.set_ylabel('Velocity (m/s)', fontsize = 26)
    ax.set_xlabel('Athlete', fontsize = 26)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.title.set_size(26)
for ax in axes.flat:
    ax.label_outer()
plt.show()

#Bland Altman plots
import statsmodels.api as sm
fig2, ax = plt.subplots(1, figsize = (8,5))
sm.graphics.mean_diff_plot(NewData['TimingGate_Max'], NewData['Radar_Max'], ax = ax)
plt.title('Timing Gate and Radar Bland Altman plot', fontsize = 18)
plt.show()   
fig3, ax = plt.subplots(1, figsize = (8,5))
sm.graphics.mean_diff_plot(NewData['TimingGate_Max'], NewData['Optojump_Max'], ax = ax)
plt.title('Timing Gate and Optojump Bland Altman plot', fontsize = 18)
plt.show()   

#ICC table
import pingouin as pg
ICCRadar = pd.DataFrame()
ICCRadar['Athlete'] = NewData['Athlete']
ICCRadar['TimingGate'] = NewData['TimingGate_Max']
ICCRadar['Radar'] = NewData['Radar_Max']
ICCRadar = ICCRadar.melt(id_vars = ['Athlete'])
ICCRadar.sort_values('Athlete', inplace = True, ascending = True)

ICCOpto = pd.DataFrame()
ICCOpto['Athlete'] = NewData['Athlete']
ICCOpto['TimingGate'] = NewData['TimingGate_Max']
ICCOpto['Optojump'] = NewData['Optojump_Max']
ICCOpto = ICCOpto.melt(id_vars = ['Athlete'])
ICCOpto.sort_values('Athlete', inplace = True, ascending = True)

iccRadar = pg.intraclass_corr(data = ICCRadar, targets = 'variable', raters = 'Athlete', ratings = 'value'  )
iccOpto = pg.intraclass_corr(data = ICCOpto, targets = 'variable', raters = 'Athlete', ratings = 'value'  )
iccRadar = iccRadar.round(decimals = 2)
iccOpto = iccOpto.round(decimals = 2)
iccRadar = iccRadar.drop("Description", axis = 1)
iccOpto = iccOpto.drop("Description", axis = 1)

from plotly.offline import plot
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.figure_factory as ff

# fig4, ax = plt.subplots(figsize = (16, 2))
# ax.axis('off')
# ax.axis('tight')
# ax.set_frame_on(False)

# ax.table(cellText = iccRadar.values, 
#           rowLabels = iccRadar.index,
#           colLabels = iccRadar.columns,
#           loc = "center")

# ax.set_title("Timing and Radar ICC values")
# fig4.tight_layout()


table1 = ff.create_table(iccRadar)
table2 = ff.create_table(iccOpto)
fig = make_subplots(rows = 2, 
                    cols = 1,
                    print_grid = True,
                    vertical_spacing = 0.085,
                    subplot_titles = ('ICC values for Timing Gates and Radar', 'ICC values for Timing Gate and Optojump'))

fig.add_trace(table1.data[0], 1, 1)
fig.add_trace(table2.data[0], 2, 1)
fig.layout.xaxis.update(table1.layout.xaxis)
fig.layout.yaxis.update(table1.layout.yaxis)
fig.layout.xaxis2.update(table2.layout.xaxis)
fig.layout.yaxis2.update(table2.layout.yaxis)

for k in range(len(table2.layout.annotations)):
    table2.layout.annotations[k].update(xref = 'x2', yref = 'y2')

all_annots = fig.layout.annotations+table1.layout.annotations + table2.layout.annotations
fig.layout.annotations = all_annots

fig.layout.update(width=800, height=600, margin=dict(t=100, l=50, r=50, b=50));

plot(fig, auto_open = True)


    
