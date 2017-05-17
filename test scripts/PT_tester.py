import sys
import pandas as pd
sys.path.append('C:\\Users\\GT9749\\PycharmProjects\\GSE_Tools')
from spire_tools import *
from plot_tools import *
from bokeh.plotting import figure, output_file, show, output_notebook
from bokeh.charts import BoxPlot
from bokeh import palettes
import pickle

output_dir = 'O:\\Wise, Adam\\Periodic Testing Review'
output_fname = 'Periodic Test Results.csv'

with open(os.path.join(output_dir,'Periodic Testing Data.pickle'), 'rb') as f:
    df = pickle.load(f)

df = df.dropna(subset=['Lot'])
df['Condition']=df.Source.apply(lambda x:x.split('\\')[-2])

df['Stress']=float('NaN')
for id,grp in df.groupby('ID'):
    if len(grp)<3:
        continue
    if grp['Condition'].str.contains('DAYS OLS').any():
            df.loc[list(grp.index),'Stress']='TC'
    if grp['Condition'].str.contains('CYCLES').any():
            df.loc[list(grp.index),'Stress']='OLS'
df=df.dropna(subset=['Stress'])


param = 'Pmax'
p=BoxPlot(df[[param,'Lot']],values='Pmax',label='Lot')
output_file('test.html')
show(p)