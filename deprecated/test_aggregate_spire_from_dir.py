import os

from deprecated.aggregate_spire_from_dir import *

datadir = os.path.normpath(r"O:\QC Development\TEST FILES\ADW-PTR'S\PTR011917A-ADW")
outdir = os.path.normpath(r"O:\Wise, Adam\PTR Munge Output")
aggregate_spire_from_dir(input_dir=datadir,output_dir=outdir)