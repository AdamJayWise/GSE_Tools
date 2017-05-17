import pandas as pd
import fnmatch
import sys
import os
from datetime import datetime
import numpy as np




# Search directory data_dir and all its subdirs for CSV files
def find_files(data_dir,pattern):
    result = []
    for root, dirs, files in os.walk(data_dir):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def aggregate_module_tests(file_names):
    df_list=[]
    for f in file_names:
        d = pd.read_excel(f)
        d['Source'] = f
        d['Condition'] = f.split('\\')[-2]
        
        # Check if column number is appropriate for measurement from spectra_nova
        if len(d.columns)<30:
            df_list.append(d)
    df = pd.concat(df_list)
    #df.loc[:,Date] = df['Date'].apply(lambda x:datetime.strptime(x,'%Y-%m-%d'))
    return df



# Test CSV files to see if they were made on the spire
def test_iv_measure_type(file_name):
    try:
        with open(file_name) as f:
            first_line = f.readline()
            if 'Title:' in first_line:
                return 'SPIRE'
            if 'Company' in first_line:
                return '8-Inch Tester'
            else:
                return
    except UnicodeDecodeError:
        print(sys.exc_info()[0], ' Unicode Error')
        return
    except FileNotFoundError:
        print('Couldn\'t find file: ',file_name)
        return
    except OSError:
        return


# return spire file fname as dataframe
def spire_to_df(fname):
    if test_iv_measure_type(fname) == 'SPIRE':
        try:
            df = pd.read_csv(fname, nrows=80, header=None, index_col=0).T
        except  UnicodeDecodeError:
            df = pd.read_csv(fname, nrows=80, header=None, index_col=0,encoding='latin10').T
        df.columns = [i.strip().strip(':') for i in df.columns]
        df['Source'] = fname
        return df
    else:
        return


# return list of spire files fname_list as aggregated dataframe
def spires_to_aggregate_df(fname_list):
    df_list = []

    if len(fname_list) > 1:
        for f in fname_list:
            try:
                df_list.append(spire_to_df(f))
                print('Read ', f)
            except:
                print('Failed to read ',f)
    df=pd.concat(df_list)
    df = df.apply(pd.to_numeric, errors='ignore')
    df['Date'] = df['Date'].apply(lambda x: datetime.strptime(x, '%m/%d/%Y'))
    df['Time'] = df['Time'].apply(lambda x: datetime.time(datetime.strptime(x, '%H:%M:%S')))
    df['Datetime'] = df[['Date', 'Time']].apply(lambda x: datetime.combine(x['Date'], x['Time']), axis=1)
    return df

# helper function to take a directory data_dir and return a dataframe with all spire files in it
def spire_df_from_directory(data_dir):
    file_list = find_files(data_dir,'*.csv')
    return spires_to_aggregate_df(file_list)
   
# return spire file fname as dataframe
def char_lab_IV_to_df(fname):
    if test_iv_measure_type(fname) == '8-Inch Tester':
        try:
            df =pd.read_csv(fname, parse_dates=['Date/Time'])
        except  UnicodeDecodeError:
            df = pd.read_csv(fname, parse_dates=['Date/Time'], encoding='latin10')
        df['Source'] = fname
        return df
    else:
        return

# function to return an aggregated dataframe from a list of 8 inch char lab IV tester files [fname_list]
def char_lab_IV_to_aggregate_df(fname_list):
    df_list = []
    if len(fname_list) > 1:
        for f in fname_list:
            try:
                df_list.append(char_lab_IV_to_df(f))
                print('Read ', f)
            except:
                print('Failed to read ', f)
    df = pd.concat(df_list)
    #df = df.apply(pd.to_numeric, errors='ignore')
    return df

	
	

# function to calculate a 'loss profile' from a single samples time series dataframe of repeated Spire IV measurements
# takes a single samples dataframe and returns a single-row dataframe 

# function to calculate a 'loss profile' from a single samples time series dataframe of repeated Spire IV measurements
# takes a single samples dataframe and returns a single-row dataframe 

def loss_profile_spire(df_uid,kpis,**kwargs):
    
    # make sure dataframe is sorted by datetime
    df_uid = df_uid.sort_values(by='Datetime')
    
    # list of metadata to add to the result
    uids = ['Title','ID']
    
    # open result dataframe
    loss_profile = pd.DataFrame(columns = uids + kpis).astype(np.int64)
    
    # use an index_bounds keyword if provided to bound the timeseries for each sample with a (i_start,i_stop) tuple
    if 'index_bounds' in kwargs.keys():
        first,last = kwargs['index_bounds']
    else:
        first,last = (0,-1)
    #Tracer()()
    # populate loss profile with 100(last-first)/first
    loss_profile.loc[0,kpis] = (100 * ( df_uid[kpis].iloc[last] - df_uid[kpis].iloc[first]) /df_uid[kpis].iloc[first] )
    
    
    # populate results with metadata as defined above
    loss_profile.loc[0,uids] = df_uid[uids].iloc[first]
    
    # Create a timedelta column to show exposure time in hours
    datecol = 'Datetime'
    loss_profile.loc[0,'Timedelta, Hours'] = np.round((df_uid.iloc[last][datecol]-df_uid.iloc[first][datecol]).total_seconds()/60/60,1)
    
    # if 'normalize==True' is provided in kwargs, make the performance results a vector with unit length
    if 'normalize' in kwargs.keys():
        if kwargs['normalize']==True:
            magsq = loss_profile[kpis].apply(lambda x:x**2).sum(axis=1).iloc[0]
            loss_profile.loc[:,kpis] = loss_profile.loc[:,kpis]/ (magsq**0.5)
            
    # if 'normalize_time==True' is provided in kwargs, divide performance results by timedelta
    if 'normalize_time' in kwargs.keys():
        if kwargs['normalize_time']==True:
            loss_profile[kpis + ['Timedelta, Hours']] =   loss_profile[kpis + ['Timedelta, Hours']]/loss_profile['Timedelta, Hours'].iloc[0]
            
    
    # if 'pass_columns' is provided in kwargs, transfer columns from input to output 
    if 'pass_columns' in kwargs.keys():
        if all([c in df_uid.columns for c in kwargs['pass_columns']]) :
            for col in kwargs['pass_columns']:
                loss_profile[col] = df_uid[col].iloc[0]
        
        else: 
            print('Error - group column not found in index')
    
    # rename columns to significy that they are differences rather than normal values
    loss_profile.rename(columns = {k:'d'+k+",%" for k in kpis},inplace=True)
    
    #return loss_profile
    start_vals = pd.DataFrame(df_uid.iloc[0]).T[kpis].reset_index()
    start_vals.columns = [lbl+', Init.' for lbl in start_vals.columns]
    return pd.concat([loss_profile,start_vals],axis=1,join_axes=[loss_profile.index])

#

def batch_loss_profile(batch_df, kpis, **kwargs):
    
    uidcol='ID'
    
    profiles = pd.DataFrame()
    
    for uid,grp in batch_df.groupby(uidcol):
        if len(grp)==1:
            continue
        profiles = pd.concat([profiles,loss_profile_spire(grp,kpis,**kwargs)])
    
    profiles=profiles.set_index('ID')
    return profiles
        
        
        
        
	

#################################################################################################################
####### Function to read spire IV file and return pandas dataframe with first (highest power?) IV curve
####### takes a filename string, returns a dataframe with current and voltage data from Spire flash tester

#define function to read spire file.  Takes a filename string which can be local or full path
def read_spire_IV(filename):
    ### make a quick function to convert all amenable entries in the dataframe to either float value or the string 'x'
    def try2float(x):
        try:
            return float(x)
        except:
            return ('x')

    # read the csv file and make a dataframe
    t = pd.read_csv(filename)

    # rename the columns
    t.columns = ['V', 'I']

    # find the start of each individual IV curve, which has the heading Voltage, Voltage2 and so on
    tags = t[t.V.str.contains('Volt')]

    # convert the numbers strings of the CSV to float, all other strings (labels etc) to 'x'
    t.loc[:,'I'] = t.I.apply(try2float)
    t.loc[:,'V'] = t.V.apply(try2float)

    # add a column which I'll use to flag the IV curves as separate
    t['num'] = 0

    # step through each IV curve start (from flags) and then subset to the first non-number value
    for n in range(1, len(tags)):
        #print(n)
        sub = t.iloc[tags.index[n]:]
        tag_end = sub[sub.I == 'x']
        t.loc[tags.index[n] + 1:tag_end.index[1],'num'] = n
        #print('n is: ', n - 1, ' start is: ', tags.index[n] + 1, ' end is: ', tag_end.index[1])
        #print(tag_end)

    # return just the first IV curve for now
    # return t[t.num == 1][['I','V']].reset_index(drop=True)

    # Remove unused (?) calibration iv curve at num = 0, and any non-numeric entires
    t = t[ (t['I']!='x') & (t['V']!='x') & (t['num']!=0) ]

    # make IV curve numbers start at 0
    t.loc[:,'num'] = t.loc[:,'num'].apply(lambda x : x-1)

    return t.reset_index(drop=True)
    #################################################################################################################
    #################################################################################################################