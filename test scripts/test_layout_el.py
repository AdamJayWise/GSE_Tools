# Import libraries
import sys
import pandas as pd
sys.path.append('C:\\Users\\GT9749\\PycharmProjects\\GSE_Tools')
from spire_tools import *
from plot_tools import *
from poll_gsps import *
from layout_IR_images import *
import matplotlib.pyplot as plt
import seaborn as sns

# define where results are stored
data_dir = r"S:\Technology\PTR\Process Test Request - GSET\Process Test Results\Process Test Results 2016\PTR010416A-JGV Evaluation of CMI TPO Dielectric with spacer beads to minimize voids\Round 3 6-cell"

# import Juan's excel file to get additional data not found in spire files
sm = pd.read_excel(os.path.join(data_dir,'PTR010416A-JGV ROUND3 Combined Data and Charts.xlsx'),sheetname='IV DATA')
sm = sm.rename(index=str, columns={'Serial#:          ':'ID'})
sm = sm[list(sm.columns)[0:12]]
sm.columns = [c.strip() for c in list(sm.columns)]

# Load spire files
files = find_files(data_dir,'*.csv')
df = spires_to_aggregate_df(files)
df = df.sort_values('Datetime')
df.loc[:,'ID'] = df.ID.apply(lambda x:x[-8:])

# Merge Juan's sample info and the spire files
df = pd.merge(df,sm,on='ID',how='left')
df.columns = [a.strip() for a in list(df.columns)]


el_dir = r"O:\QC Development\TEST FILES\JGV-PTRs\JGV 2016 PTR'S\PTR010416A-JGV Round 3\EL IMAGES"
layout_ir_from_df(df,el_dir,'Sample ID:')
