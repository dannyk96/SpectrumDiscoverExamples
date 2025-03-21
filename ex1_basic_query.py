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
sd_auth=('dannyk95','CsitestlabsMonday@2024')

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
# Create my example query 
# here we ask for the file summary to be grouped 
myquery="""{
   "query": "platform='Spectrum Scale'",
   "filters": [
   ],
   "group_by": ["Site","Owner","Datasource"],
   "sort_by": [{"Site": "asc"},{"Owner": "asc"}],
   "limit": 100000
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

# Print Column Headers
print("%5s %-15s %-20s %-15s%15s %15s %15s" % ("     ","Site","Owner","Data Source", "Count", "Sum (GB)", "Sum_consumed"))
print("     %s" % ("-"*100))
total=0
for a in json.loads(data['rows']):
   site=a['site']
   owner=a['owner']
   source=a['datasource']
   count=int(a['count'])
   sumx=int(a['sum'])
   sumconsumed=int(a['sumconsumed'])
   print("%5s %-15s %-20s %-15s %15d %15.3f %15.3f" % ("     ",site,owner,source,count,sumx/1.e9,sumconsumed/1.e9))
# print totals below the table
print("     %s" % ("-"*100))
print()

#
# Next print out the whole of 'facet_tree' for reference
#   Afterwards we will pretty print out one or more pf the c. 12 tables
#
if debug:
  print("----------------------------")
  for x in data['facet_tree']:
    print (x)
    print (data['facet_tree'][x])

#
# Table 2 : File count grouped by Filetype 
#
# Of the c. 12 tables, we will concentrate of the table of file count per username
byowner= data['facet_tree']['OWNER']


#cars=[]
#data=[])
# Print Column Headers
print("%-22s %15s" % ("     FileGroup","count"))
print("     %s" % ("-"*33))
total=0
for a in json.loads(data['facet_tree']['FILEGROUP']):
    fg=a['filegroup']
    n=int(a['count'])
    print ("     %-22s %10d" % (fg,n))
    total+=n
#    cars.append(fg)
#    data.append(n)
# print totals below the table
print("     %s" % ("-"*33))
print ("     %-22s %10d" % ("Total",total))


#fig = plt.figure(figsize=(10, 7))
#plt.pie(data, labels=cars)

# show plot
#plt.show()

#byrows=data['rows']
#print("----------------------------")
#print(byrows)


# An other example - to get info on all the files owned by a particular user
# ToDo : Move this to its own example
myquery="""{
{
   "query": "",
   "filters": [
   {
      "key": "owner",
      "operator": "=",
      "value": "benjamin"
   }
],
   "group_by": [],
   "sort_by": [],
   "limit": 100
}"""
