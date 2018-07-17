#!/usr/bin/python3

import sys,os
inputfile = sys.argv [1]
names_ages = {}
#revers_dict = {}
with open(inputfile, 'r') as csvfile:
    for line in csvfile.readlines():
        if not line:
            continue
        id,name,age = [ x.strip()for x in line.split(",")]
        names_ages[name] = age
        if "name" in names_ages.keys() :
            del names_ages["name"]
revers_dict = [(value, key) for key,value in names_ages.items()]
print ( "the youngest person is ", min(revers_dict))
print ("the oldest age is" , max(revers_dict))