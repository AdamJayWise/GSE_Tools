import pandas as pd

import matplotlib.pyplot as plt
import os
import fnmatch
from datetime import datetime
import operator

#Takes a results file from an experiment, searches for images based on unique serials, and prepares a brief report
#Returns figure handles



############ Define Find Function to track down JPGs ##############
def find(pattern, rootdir):
    pattern = '*'+str(pattern)+'*jpg'
    result = []
    for root, dirs, files in os.walk(rootdir):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result
####################################################################

def layout_IR_images(fdir, fname, datadir='', type='spire',output_dir='.//images//'):
    #use a dictionary to look up the appropariate column heading for the instrument.
    # Need to double check what the 'big tester' is really called
    typedict={'bigtester':'Module#','spire':'Serial'}
    serial_string = typedict[type.lower()]
    results = pd.read_csv(fdir+fname,encoding = 'latin10')
    #print(results.head())

    jpeg_list=[]
    for q,S in enumerate(results[serial_string].unique()):

        print(S)
        jpeg_list = find(S,datadir)
        num_images = len(jpeg_list)
        if (num_images>0) & (num_images<9):
            times = [os.path.getmtime(z) for z in jpeg_list]
            times,jpeg_list = zip(*sorted(zip(times, jpeg_list),key=operator.itemgetter(0), reverse=True))
            print(jpeg_list,times)
            jpeg_list = list(jpeg_list)
            jpeg_list.reverse()
            fig=plt.figure()
            for i,f in enumerate(jpeg_list):
                img = plt.imread(f)
                ax = fig.add_subplot('1'+str(num_images)+str(i+1))
                ax.imshow(img,aspect='auto')
                sub_label = f.split('.')[0].split('\\')[-2:]
                ax.set_xlabel(sub_label[0]+'\n'+sub_label[-1], fontsize=9)
                ax.xaxis.set_ticklabels([])
                ax.yaxis.set_ticklabels([])
                fig.subplots_adjust(wspace=None, hspace=None)
                #fig.tight_layout()
            #fig.savefig(datadir+output_dir+str(S) + ".png")
    plt.show()


import pandas as pd
import matplotlib.pyplot as plt
import os
import fnmatch
from datetime import datetime
import operator


# Takes a results file from an experiment, searches for images based on unique serials, and prepares a brief report
# Returns figure handles


def layout_ir_from_df(df, data_dir, UIDcolumn):
    # use a dictionary to look up the appropariate column heading for the instrument.
    # Need to double check what the 'big tester' is really called
    serial_string = UIDcolumn
    results = df

    file_dump = find('*', data_dir)

    jpeg_list = []
    # Tracer()()
    for q, S in enumerate(results[serial_string].unique()):

        # print(S)
        jpeg_list = [f for f in file_dump if S in f]
        num_images = len(jpeg_list)
        # print(jpeg_list)

        # if too long, strip out middle values
        while num_images>=9:
            jpeg_list=jpeg_list[0:4]+jpeg_list[5:]
            num_images = len(jpeg_list)

        if (num_images > 1) & (num_images<9):
            times = [os.path.getmtime(z) for z in jpeg_list]
            times, jpeg_list = zip(*sorted(zip(times, jpeg_list), key=operator.itemgetter(0), reverse=True))
            # print(jpeg_list,times)
            jpeg_list = list(jpeg_list)
            jpeg_list.reverse()
            fig = plt.figure(figsize=(int(num_images * 2), 3))
            for i, f in enumerate(jpeg_list):
                img = plt.imread(f)
                ax = fig.add_subplot('1' + str(num_images) + str(i + 1))
                ax.imshow(img, aspect='auto')
                sub_label = f.split('.')[0].split('\\')[-2:]
                ax.set_xlabel(sub_label[0].split('-')[0][0:20] + '\n' + sub_label[-1].split('-')[0][0:20], fontsize=9)
                ax.xaxis.set_ticklabels([])
                ax.yaxis.set_ticklabels([])
                fig.subplots_adjust(wspace=None, hspace=None)
                ax.grid(False)
                fig.suptitle(S)
                # fig.tight_layout()
                # fig.savefig(datadir+output_dir+str(S) + ".png")
            plt.show()
            plt.close('all')