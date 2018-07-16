import getpass
password = getpass.getpass()
mypassword  = 'hh'
count=0
import sys
if password == mypassword :
   print ("you are Authorized")

else :
   while (count<3): 
      print ("you are not auttorized, try again")
      password = getpass.getpass()
      if password == mypassword :
              print ("you are Authorized")
              sys.exit(0)
      else:
         count = count + 1

