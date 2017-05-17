import os

from plot_trajectories import *

data_dir = os.path.normpath(r"O:\QC Development\TEST FILES\ADW-PTR'S\PTR100716A-ADW\Encapsulated Submodule Test\\")
df_file = os.path.join(data_dir,'output.csv')
sm_file = os.path.join(data_dir,'sample_map.csv')
#aggregate_spire_from_dir(data_dir,'.')


# Load data and sample map
df = pd.read_csv(df_file,encoding='latin10')
sm = pd.read_csv(sm_file)

df.loc[:,'Serial']=df['Serial'].apply(lambda x:x.split()[0])

# Join them on the 'serial' column
df = pd.merge(df,sm,on='Serial',how='left')

layout_multiplot(cond_list=['Pmax','Voc','Isc'],data=df[df['Stress']=='85/0']
                 ,x_label='Date',sample_uid='Serial',cond_uid='Group',normalized=True,statistical=False)


