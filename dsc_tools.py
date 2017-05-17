import pandas as pd
import numpy as np

# function to read DSC results
def readDSC(fname):
    lines = []
    with open(fname, 'r') as f:
        for line in f:
            lines.append(line)

    iso_index = [i for i, line in enumerate(lines) if 'DSC Iso' in line]
    dsc_index = [i for i, line in enumerate(lines) if 'DSC Temp' in line]
    stop_index = [i for i, line in enumerate(lines) if 'TEMPERATURE CALIBRATION INPUTS' in line]

    heat = lines[(1 + dsc_index[0]):iso_index[1]]
    heat = [line.strip().split('\t') for line in heat]
    heat = pd.DataFrame(data=heat, dtype='float')
    heat.columns = ['Time', 'Heat Flow', 'Baseline', 'Prog Temp', 'Temp', 'Gas Flow']

    cool = lines[(1 + dsc_index[1]):stop_index[0]]
    cool = [line.strip().split('\t') for line in cool]
    cool = pd.DataFrame(data=cool, dtype='float')
    cool.columns = ['Time', 'Heat Flow', 'Baseline', 'Prog Temp', 'Temp', 'Gas Flow']

    # create dictionary of additional props from first few lines of file
    a = [f.strip().split(':', 1) for f in lines[0:15] if ':' in f]
    propdict = {z[0].strip(): z[1].strip() for z in a}
    return heat, cool, propdict

# class to manipulate results from exported DSC data
class DSC_result:
    # define file read function
    def __init__(self,fname1):
        self.heat,self.cool,self.propdict = readDSC(fname1)


