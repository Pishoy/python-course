#!/usr/bin/python3
#!/usr/bin/env python3 # this if you do not know python path

import sys
import os
scriptname = sys.argv[0]
for arg in sys.argv[1:]:
    # check it is directoy or file
    if os.path.isdir(arg) is True:
        print ("Please note it is DIR")
        print(os.listdir(arg))
    else:
        print ("Please note it is file")
        print(os.stat(arg))