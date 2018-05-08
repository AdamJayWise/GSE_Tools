import pandas as pd
import os

def load_PICI_records(filename):
    """
    takes path+filename string 'filename' pointing to a mondragon PICI archive file, and returns Pandas dataframe merging relevant spreadsheet tabs
    """
    a = pd.read_excel(os.path.join(filename), sheetname = None) 
    rollmap = pd.melt(a['SubToRoll'],value_vars = ['SubIdL1','SubIdL2'], id_vars = 'RollId', value_name='SubId')[['RollId','SubId']]
    q = pd.merge( pd.merge( a['Sub'],pd.merge(a['Cell'],a['CellSub'], how = 'left', on = 'CellID'), how = 'left', on = 'SubId'),rollmap, on = 'SubId', how = 'left')
    return q.drop_duplicates('SubId')