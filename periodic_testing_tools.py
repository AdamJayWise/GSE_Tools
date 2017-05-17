import pickle
import sys
sys.path.append('C:\\Users\\GT9749\\PycharmProjects\\GSE_Tools')
from spire_tools import *
import os
import time
import pandas as pd

# Define where to read data from and where to put results
test_dir = 'O:\\QC Development\\TEST FILES\\SOP1000658- ICI Periodic Testing'
output_dir = 'O:\\Wise, Adam\\Periodic Testing Review'
output_fname = 'Periodic Test Results.csv'


# Load the last list of samples found to save time:
try:
    #load old pickled list of files
    with open(os.path.join(output_dir,'sample_list.pickle'), 'rb') as f:
        last_data_list = pickle.load(f)
except:
    print('Previous sample list not found')

# Promp user to re-find files, if desired
print('Find new files in Periodic Testing Folder? Y/N')
if input().upper() == 'Y':
    # look for csv files in the ICI periodic testing data dir
    sample_list = find_files(test_dir,'*.csv')
else:
    sample_list = last_data_list

#regenerate the periodic testing test dataframe if needed
def regenerate_pt_dataframe():
    # Load and concatenate the spire measurments found into a Pandas dataframe
    df = spires_to_aggregate_df(sample_list)
    # Guess the lot# via regex
    df['Lot']=df['Source'].str.extract('LOT\s*#(\d{4})')
    # Guess a backup serial number - as opposed to the ID which is generated from the Spire GUI - from the file name
    df['Serial'] = df.Source.apply(lambda s: s.split('\\')[-1].split('.')[0])
    # save the Dataframe
    df.to_csv(os.path.join(output_dir,output_fname))
    # save a date-coded backup copy... why not
    df.to_csv(os.path.join(output_dir,'Old PT Data',time.strftime("%m-%d-%Y")+' '+output_fname))
    # dump the dataframe to file to make re-loading it easier
    with open(os.path.join(output_dir, 'Periodic Testing Data.pickle'), 'wb') as f:
        pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)


# dump the sample list to file, so that we can check it later
with open(os.path.join(output_dir,'sample_list.pickle'), 'wb') as f:
    pickle.dump(sample_list, f, pickle.HIGHEST_PROTOCOL)




# try to open period test results
print('Regenerate PT data file? Y/N')
if input().upper()=='Y':
    regenerate_pt_dataframe()
else:
    print('No action required, closing...')
