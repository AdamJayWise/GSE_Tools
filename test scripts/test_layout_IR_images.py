#a quick script to test out the laout_IR_images function

from layout_IR_images import *

fdir_1 = 'O:\Wise, Adam\PTR Munge Output\\'
fname_1 = '\\PTR100716A-ADW Baseline.csv'
datadir_1 = 'O:\\QC Development\\TEST FILES\\ADW-PTR\'S\\PTR100716A-ADW'

layout_IR_images(fdir_1, fname_1, type='bigtester', datadir=datadir_1,output_dir='\\images\\')
print('Done')
