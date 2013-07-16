#!/usr/bin/env python

import os
import fnmatch
import sys

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d","--dir")
parser.add_option("-g","--grep",default="*.root")
(options,args) = parser.parse_args()

running_sum=0
for root, dirs, files in os.walk(options.dir):
  if len(dirs)==0:
    my_files = fnmatch.filter(files,options.grep)
    running_sum += len(my_files)
    print '%s/%15s -- %d'%(os.path.basename(os.path.abspath(os.path.join(root,os.pardir))),os.path.basename(root),len(my_files))

print 'Total matches =', running_sum
