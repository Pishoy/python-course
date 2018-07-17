#!/usr/bin/python
import sys,os
for arg in sys.argv[1:]:
    if os.path.isfile(arg):
       with open(arg, 'r') as file:
          for line in file.readlines():
             print (line)

    else:
        print ("the entered input is not a file", arg)
