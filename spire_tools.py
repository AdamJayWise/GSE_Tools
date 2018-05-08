import pandas as pd
import fnmatch
import sys
import os
from datetime import datetime, timedelta
import numpy as np
import re
import matplotlib.pyplot as plt



def find_files(data_dir,pattern):
    """
    Returns list of files matching pattern in directory data_dir and its subdirectories
    
    Args:
        data_dir (str): directory to search (including subdirectories) for files matching pattern
        pattern (str): unix-style filename pattern to matching
        
    Returns:
        result (list): List of strings with joined file+path pointing to filenames
    """
    result = []
    for root, dirs, files in os.walk(data_dir):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

    
def aggregate_module_tests(file_names):
    """
    Aggregates dataframe of spectra-nova module results for large-format modules
    
    Args:
        file_names (list): list of filename strings to load and aggregrate
    
    Returns:
        df (pandas.DataFrame): dataframe of measurements, stacked such that 1 row = 1 measurement
    """
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


def test_iv_measure_type(file_name):
    """
    Tests files to see if they were generated on the 8-Inch IV tester, or Spire IV tester
    
    Args:
        file_name (str): string pointing (file or path+file) to file in question
    
    Returns:
        string representing instrument that generated file ('Spire','8-Inch Tester')
    """
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


def spire_to_df(fname):
    """
    Loads single spire IV parameter measurement file into pandas.DataFrame format
    
    Args:
        fname (str): string pointing (file or path+file) to file in question
        
    Returns:
        dataframe with measurements from file, or nonetype
    """
    if test_iv_measure_type(fname) == 'SPIRE':
        try:
            df = pd.read_csv(fname, nrows=80, header=None, index_col=0).T
        except  UnicodeDecodeError:
            df = pd.read_csv(fname, nrows=80, header=None, index_col=0,encoding='latin10').T
        df.columns = [i.strip().strip(':') for i in df.columns]
        df['Source'] = fname
        return df
    else:
        return None



def spires_to_aggregate_df(fname_list):
    """
    Aggregates list of spire files fname_list to pandas.DataFrame
    
    Args:
        fname_list (list): list of spire filenames
    
    Returns:
        dataframe of aggregated results
    """
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

def spire_df_from_directory(data_dir):
    """
    Helper function to take a directory data_dir and return a dataframe with all spire measurements aggregated to dataframe
    
    Args:
        data_dir (str): target directory from which to aggregate measurements - includes subdirectories
        
    Returns:
        pandas.DataFrame with aggregated spire measurements
    
    """
    file_list = find_files(data_dir,'*.csv')
    return spires_to_aggregate_df(file_list)
   

def char_lab_IV_to_df(fname):
    """
    Loads Characterization Lab 8" IV tester file into pandas.DataFrame format
    
    Args:
        fname (str): filename of test file
    
    Returns:
        pandas.DataFrame with measurement, or nonetype if error
    
    """
    if test_iv_measure_type(fname) == '8-Inch Tester':
        try:
            df =pd.read_csv(fname, parse_dates=['Date/Time'])
        except  UnicodeDecodeError:
            df = pd.read_csv(fname, parse_dates=['Date/Time'], encoding='latin10')
        df['Source'] = fname
        return df
    else:
        return

        
def char_lab_IV_to_aggregate_df(fname_list):
    """
    function to return an aggregated dataframe from a list of 8 inch char lab IV tester files [fname_list]
    
    Args:
        fname_list (list): list of files to aggregate, must be of 8" tester type
        
    Returns:
        pandas.DataFrame of aggregated results
    """
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

	
	



def loss_profile_spire(df_uid = None ,kpis = None , order_column = 'Datetime', **kwargs):
    """
    Calculates a 'loss profile' from a single samples time series dataframe of repeated Spire IV measurements
    
    Args:
        df_uid (pandas.DataFrame): dataframe corresponding to repeated measurements of some unique sample
        kpis (list): list of dataframe columns to track, the difference between the initial and final values will be reported
        order_column (str): dataframe column to sequence measuremnents - e.g., time, date, datetime, stage
    
    Returns:
        dataframe with loss metrics
    
    """
    
    # make sure dataframe is sorted by datetime
    df_uid = df_uid.sort_values(by = order_column)
    
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

# Clean this up and check if it actually works!

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
    
    
def read_peel(file_list):
    """
    Helper function to load list of peel files into pandas dataframe
    
    Args:
        file_list: list of peel path + filesnames
    
    Returns:
        concatenated dataframe of peel file data
    """
    df_list = []
    for f in file_list:
        try:
            df = pd.read_excel(f, sheetname = 'Sheet1', skiprows = 15, parse_dates=False)
            df.drop(df.columns[4:], axis=1, inplace=True)
            df = df[df['Units'].astype(str).str.contains('N')]
            df['Source'] = f.split('\\')[-1].split('.')[0]
            df['Source Full'] = f
            df_list.append(df)
        except:
            print('Failed to read {}'.format(f.split('\\')[-1]))
    df_concat = pd.concat(df_list)
    return df_concat

# Spire degradation        
def degrade(x, p = 'Pmax', comment_col = 'Comment', start_str = 'AS REC', end_str = 'POST 21 DAYS OLS'):
    
    try:
        init = x[x[comment_col].str.contains(start_str)][p].iloc[0]
    except:
        init = np.nan

    try:
        fin = x[x[comment_col].str.contains(end_str)][p].iloc[0]
    except:
        fin = np.nan
    
        
    try:
        resultdict = {'{} Initial'.format(p):init , '{} Final'.format(p):fin, '{} Change, %'.format(p): 100*(fin-init)/init}
        return pd.Series(resultdict)
    except:
        return np.nan
        
        
#### GDOES Utility Functions

# function to load a single GDOES file to a pandas dataframe
def gdoes_file_to_dataframe(data_dir,fname):
    # read GDOES file into a dataframe
    df = pd.read_csv(os.path.join(data_dir,fname),sep='\t',header=0,encoding='utf_16')
    
    #Regex pattern to find Lot, downweb, and crossweb
    search_pattern = re.compile(r'(?P<Lot>[0-9]{4}SA|SB)\D+(?P<Downweb>[0-9]+)[^R0-9]*(?P<Crossweb>R[0-9]|[0-9]+)')
    
    # regex search through the filename for Lot, Downweb, and Crossweb Info
    regex_results = re.search(search_pattern,fname)
    
    for attribute in ['Lot','Downweb','Crossweb']:
        try:
            df[attribute] = regex_results.group(attribute)
        except:
            df[attribute] = 'Failed to Parse'

    #change micron tag to um to make UTF-8 friendly
    colnames = list(df.columns)
    colnames[0]='Depth, um'
    df.columns = colnames
    
    #tag results with source file filename
    df['Source File'] = fname
    return df

# function to load and concat a set of GDOES files to a dataframe
def gdoes_lot_to_dataframe(data_dir):
    #lot_number = str(lot_number)
    # look through the data directory for filenames containing the Lot# string lot_number
    file_list = [f for f in os.listdir(data_dir)]
    
    #start building up a list of results for the lot
    data_frame_collection = []
    
    # loop through the list of candidate files and load them using the single-file function above
    for filename in file_list:
        try:
        #print('Reading from: '+filename)
            data_frame_collection.append(gdoes_file_to_dataframe(data_dir,filename))
        except:
            print('could not load data from '+filename)
            continue
    # if more than one dataframe is found, return a concatenated version        
    if len(data_frame_collection)>1:
        return pd.concat(data_frame_collection)
    else:
        return data_frame_collection
        
    
def load_weather():
    
    files = ['0118rd.txt','0117rd.txt','0116rd.txt']
    root_dir = "O:\Wise, Adam\weather\cals.arizona.edu azmet weather data"

    weather = []

    for f in files:
        weather.append(pd.read_csv(os.path.join(root_dir,f),header=None))

    weather = pd.concat(weather)                        
    weather_cols = pd.read_csv(r"O:\Wise, Adam\weather\cals.arizona.edu azmet weather data\Weather_summary.csv").columns
    weather.columns = weather_cols[1:-1]
    weather['Date'] = pd.to_datetime(weather['Year'],format='%Y')+weather['Day of Year (DOY)'].apply(lambda x:timedelta(days=x-1))
    weather['Date'] = weather['Date'].apply(lambda x: x.date())
    
    return weather
        
        
        
def show_test( test_str, test_title, identifier = 'ID', power_cutoff = [0,999], data = None, fold_labels = True, **kwargs):

    # function to put line breaks into labels
    def process_string(x):
        if fold_labels:
            return x.replace('&','&\n')
        else:
            return x

    # make a subplots figure to contain results
    f, axarr = plt.subplots(ncols = 2 , nrows = 1, figsize = (12,3) )
    
    # find serials in the dataset relevant to the keyword provided
    serials = data[ data.Comment.str.contains( test_str ) ].sort_values('Datetime')[identifier].unique()
    
    if 'group_columns' not in kwargs.keys():
        
        for lbl, grp in data[(data[identifier].isin(serials)) & (data['Pmax'].between( *power_cutoff ) ) ].sort_values('Datetime').groupby(identifier):
            
            axarr[0].plot(grp['Comment'].apply(process_string) ,grp['Pmax'], '.-', label = lbl)    
            axarr[1].plot(grp['Comment'].apply(process_string) ,grp['Pmax']/grp['Pmax'].iloc[0], '.-', alpha = 0.5, label = lbl)
            
            if 'label_serials' not in kwargs.keys():
                plt.legend([])
              
            
            
    if 'group_columns' in kwargs.keys():
        
        data_subset = data[(data[identifier].isin(serials)) & (data['Pmax'].between( *power_cutoff ) ) ].sort_values('Datetime')
        line_color_options = [(1,0,0),(0,0,1),(0,0,0)]
        colors = {c:line_color_options[i] for i,c in enumerate(data_subset[ kwargs['group_columns'][0]].unique())}
        
        label_list = []
        
        for lbl, grp in data_subset.groupby(kwargs['group_columns']):
            
            if lbl[0] in label_list:
                label_to_show = '_'
            else:
                label_to_show = lbl[0]
                label_list.append(lbl[0])
            
            linecolor = colors[lbl[0]] * ( 0.5 + np.random.rand(3)/2 )
            
            axarr[0].plot(grp['Comment'].apply(process_string) ,
                          grp['Pmax'],
                          '.-',
                          color = linecolor,
                          label = label_to_show )
            
            axarr[1].plot(grp['Comment'].apply(process_string) ,
                          grp['Pmax']/grp['Pmax'].iloc[0], '.-',
                          alpha = 0.5,
                          color = linecolor,
                          label = label_to_show )
            plt.legend()
        
        
    
    axarr[0].set_ylabel('Pmax, W')
    axarr[1].set_ylabel('Pmax, Normalized')
    
    axarr[1].axhline(1, color = 'black' )
    
    for ax in axarr:
        
        plt.sca(ax)
        plt.xticks(rotation=60)
        plt.grid()
        
        if 'label_serials' in kwargs.keys():
            plt.legend()
    
    plt.suptitle(test_title, fontsize = 18)

    plt.show()
    
    return serials
