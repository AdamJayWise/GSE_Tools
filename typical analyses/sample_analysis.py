import os

from plot_trajectories import *

data_dir = os.path.normpath(r"O:\QC Development\TEST FILES\ADW-PTR'S\PTR100716A-ADW\SUBMODULES 12 5 16\\")
df_file = os.path.join(data_dir,'output.csv')
sm_file = os.path.join(data_dir,'sample_map.csv')
#aggregate_spire_from_dir(data_dir,'.')


# Load data and sample map
df = pd.read_csv(df_file,encoding='latin10')
sm = pd.read_csv(sm_file)

# Join them on the 'serial' column
df = pd.merge(df,sm,on='Serial',how='left')

layout_multiplot(cond_list=['Pmax','Voc','Isc'],data=df,x_label='Date',sample_uid='Serial',cond_uid='Conditions',normalized=False,statistical=True)


