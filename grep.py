#!/usr/bin/python3

import sys,re,os
search_item = sys.argv[1]
file = sys.argv[2]

if os.path.isfile(file) is True:
       with open(file, 'r') as f:
          for line in f.readlines():
              if re.search(search_item, line):
                 print (line)


else:
        print ("the entered input is not a file", file)