import os
import pandas as pd
import numpy as np
import csv

### Walk through directory structure starting at input_dir, and aggregate each spire file
### Then put summary into output_dir

def aggregate_spire_from_dir(input_dir='.',output_dir='.'):
    dir_to_check = os.path.normpath(input_dir)
    print(repr(dir_to_check))
    output_fname = dir_to_check.split('\\')[-1] + '.csv'

    with open(output_dir + '\\' + output_fname, 'w') as outfile:
        for roots, dir_list, files in os.walk(dir_to_check):
            files = filter(lambda x: (x.endswith('csv')) & ('output' not in x), files)
            print(dir_list)

            for data_file in files:
                print('Reading: '+roots + '/' + data_file)
                f = open(roots + '/' + data_file, 'r')
                lines = f.readlines()[0:80]
                if 'Title' not in lines[0]:
                    print('Skipping ' + data_file)
                    continue
                trim = lambda x: [x.split(',')[0].strip(), x.split(',')[1].strip()]
                lines = list(map(trim, lines))
                lines.insert(0, ['Serial', data_file.split('.')[0]])
                lines.insert(0, ['Lot', roots.split(os.sep)[-2]])
                lines.insert(0, ['Condition', roots.split(os.sep)[-1].upper()])
                lines.insert(0, ['Filename', roots+'\\'+data_file])
                props, vals = zip(*lines)
                f.close()

                if (outfile.tell() == 0):
                    for i in range(len(props)):
                        outfile.write(props[i].strip(':') + ',')
                    outfile.write('\n')

                for i in range(len(vals)):
                    outfile.write(vals[i] + ',')
                outfile.write('\n')
    print('Done!')

