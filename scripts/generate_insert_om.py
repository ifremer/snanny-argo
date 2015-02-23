import csv
import time
import datetime
import uuid
import string
import re
import os
import requests
import json
import urllib2


#csv_file_path = "/home/coriolis_exp/spool/co05/co0508/ar_index_global_prof.txt"
csv_file_path = "/home/isi-projets/sensorNanny/data/archive/argo/inputs/ar_index_global_prof.txt"
rootFilePath = "file:///home/coriolis_exp/spool/co05/co0508/"
template_file = "/home/isi-projets/sensorNanny/data/archive/argo/swe/templates/om_template.xml"
target_directory= "/home/isi-projets/sensorNanny/data/archive/argo/swe/obs/"
snanny_system_view_rest = "http://visi-seadatanet-batch:8092/snanny_systems/_design/dev_snanny_system_keyfilter/_view/snanny_system_keyfilter"
sostT_server = "http://isi.ifremer.fr/snanny-sostServer/"

####

csvfile = open(csv_file_path, 'rb')
spamreader = csv.reader(csvfile, delimiter=',')
for row in spamreader:
  if(not row[0].startswith('# ') and not row[0].startswith('file')):
    record = {}
    print spamreader.line_num, row
    ## generate UUID
    record['localuuid'] = str(uuid.uuid1())
    ## platform number
    pathSplit = row[0].split('/')
    record['platformnumber'] = pathSplit[1]
    ## latitude
    record['latitude'] = row[2]
    ## longitude
    record['longitude'] = row[3]
    ## profile date time
    try:
      dt_profile = datetime.datetime.strptime(row[1], "%Y%m%d%H%M%S")
      record['profiledate'] = dt_profile.isoformat()
    except ValueError:
      record['profiledate'] = row[1]        
    ## update date time
    try:
      dt_update = datetime.datetime.strptime(row[7], "%Y%m%d%H%M%S")
      record['updatedate'] = dt_update.isoformat()
    except ValueError:
      record['updatedate'] = row[7]        
    ## procedure uri     
    param = {"key": str('"platformNumber___' + record["platformnumber"]+ '"') }
    r1 = requests.get(snanny_system_view_rest, params=param)     
    data = r1.json()
    if (len(data["rows"])>0):
      record['procedureuri'] = sostT_server + 'record/' + str(data["rows"][0]["id"])
      # filePath
      record['filepath'] = rootFilePath + row[0]           
      recordDataString = "";
      with open(template_file, "rt") as fin:
        for line in fin:
          foundPatList = re.findall('___[a-z]*___', line)
    	  for pat in foundPatList:
            line= line.replace(pat, record[pat.split('___')[1]])
	  recordDataString+=line
      fin.close()     
      urlPost = sostT_server + "sos?service=SOS&version=2.0&request=insertObservation"
      headers = {'content-type': 'text/xml'}      
      r2 = requests.post(urlPost, data=recordDataString, headers=headers)
      print record
    else:
      print "no platform metadata available"
csvfile.close()


    




