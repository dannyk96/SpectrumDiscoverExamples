#!/usr/bin/python3
#
# Example 1 : A basic query to the RestAPI. We extract and pretty print three tables
#
# Notes:
#  Use of the RestAPI is a two step process. First we do a GET against 'auth/v1/token'. From this we looks for 'x-auth-token' 
# in the returned headers. We then present this token instead of a username and password, in all subsequent PUT and POST calls
#
debug=False
#debug=True   # uncomment to get verbose output

# The usual ;ibraries for working with RestAPIs
import requests
import json

# Plot libraries - for now comment them out. In the future, consider a Jupyter Notebook with inline pie charts :-)
#from matplotlib import pyplot as plt
#import numpy as np

# Create a function class so that we can pass against "Authentication": our token "Bearer 
# We create this so we can use a simple way of passign the auth= string :-)
class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


# Define the URL of the Spectrum Discover server
# The next is in a sandbox environemnt hosted by my employer
server="https://console-ibm-data-cataloging.apps.fusionocp4.csitestlabs.co.uk/"

# which pre-exisiting user to get a token for
sd_auth=('sd_worker','Passw0rd')

url= server + 'auth/v1/token'
if debug: print(url)
try:
    # send a GET and return a response object
    request = requests.get(url = url, auth=sd_auth, verify=False)
except:
    print('An error has occurred.')
    sys.exit(1)

auth=request.headers['x-auth-token']
if debug: print ("x-auth-token=" +auth)


#
#   Request real statistical from Spectrum Discover (iaka Fusion Data Catalog)
#
url= server + 'db2whrest/v1/search'
headers = {'Content-Type': 'application/json'}

# ( Create a session object : we will skip here but maybe use in a later example)
#session = requests.Session()
#session.headers.update({'Content-Type': 'application/json'})

#print("----------------------------")
# see example at:
# https://www.ibm.com/docs/en/SSY8AC_2.0.2/com.ibm.spectrum.discover.v2r02.doc/pdf/discover_api.pdf

#
# Send a POST request with JSON data using the session object
#
# An other example - to get info on all the files owned by a particular user
# ToDo : Move this to its own example
myquery="""{
   "query": "",
   "filters": [
   {
      "key": "owner",
      "operator": "=",
      "value": "root"
   }
],
   "group_by": [],
   "sort_by": [],
   "limit": 100
}"""
response = requests.post(url, headers=headers,  auth=BearerAuth(auth), data=myquery, verify=False)
if debug:
  print("----------------------------")
  for x in response.json():
    print(x)

if debug: print(response.text)

data=json.loads(response.text)

if debug:
  print("----------------------------")
  for a in json.loads(byowner):
    print(a)
  print(" ")

if debug:
    print("----------------------------")
    print(data['facet_tree'])

#
# Table 1 : The main output from the query 
#
if debug: 
   print("----------------------------")
   for x in json.loads(data['rows']):
       print (x)

# Record is of the form:
# {'path': '/gpfs/deleteme/.afm/', 'filename': '.afmctl', 'filetype': 'afmctl', 'datasource': 'deleteme', 
# 'owner': 'root', 'group': 'root', 'revision': 'MO1', 'site': 'Dorset', 'platform': 'Spectrum Scale', 
# 'cluster': 'csi_techlabs_ess32k.local', 'inode': 108548, 'permissions': '-rw-r--r--', 'fileset': 'root', 
# 'uid': 0, 'gid': 0, 'recordversion': None, 'state': 'resdnt', 'migloc': 'NA', 
# 'mtime': '2025-03-04T15:11:01.917', 'atime': '2025-03-05T10:45:14.971', 'ctime': '2025-03-04T15:11:01.694', 
# 'tier': 'system', 'size': 1, 'fkey': 'csi_techlabs_ess32k.local_deleteme_108548', 'collection': 'spectrum-discover', 
# 'temperature': None, 'duplicate': None, 'sizeconsumed': 0, 'nodename': None, 'filespace': None, 'mgmtclass': None, 
# 'html': None, 'malignant': None, 'researchproject': None}

# Print Column Headers
print("%5s %-15s %-20s %-15s%15s %15s %15s" % ("     ","Site","Owner","Data Source", "Count", "Sum (GB)", "Sum_consumed"))
print("     %s" % ("-"*100))
total=0
for a in json.loads(data['rows']):
   path=a['path']
   filename=a['filename']
   owner=a['owner']
   mtime=a['mtime']
   size=int(a['size'])
   duplicate=a['duplicate']
   print("%5s%-15s %-20s %-15s %15d %15.3f %10s" % ("    ",filename, path, owner, mtime, size, duplicate))
# print totals below the table
print("     %s" % ("-"*100))
print()
