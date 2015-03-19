import csv
import time
import datetime
import uuid
import string
import re
import os
import requests
import json
import geohash
import timehash
from couchbase import Couchbase

#csv_file_path = "/home/coriolis_exp/spool/co05/co0508/ar_index_global_prof.txt"
csv_file_path = "/home/isi-projets/sensorNanny/data/archive/argo/inputs/ar_index_global_prof.txt"
rootFilePath = "file:///home/coriolis_exp/spool/co05/co0508/"
template_file = "../swe/templates/om_json_template.json"
target_directory= "../swe/obs/"
snanny_system_view_rest = "http://visi-common-couchbase1:8092/snanny_systems_dev/_design/system_keyFilter/_view/snanny_system_keyFilter"
sostT_server = "http://isi.ifremer.fr/snanny-sostServer/"
## couchbase connexion
c = Couchbase.connect(bucket='snanny_observations_dev', host='134.246.144.118', timeout=1)


####

csvfile = open(csv_file_path, 'r')
spamreader = csv.reader(csvfile, delimiter=',')
for row in spamreader:
    if(not row[0].startswith('# ') and not row[0].startswith('file')):
        record = {}
        ## generate UUID
        record['localuuid'] = str(uuid.uuid1())
        ## platform number
        pathSplit = row[0].split('/')
        record['platformnumber'] = pathSplit[1]
        ## latitude
        record['latitude'] = row[2]
        ## longitude
        record['longitude'] = row[3]
        #print(row[2], row[3])
        try:
            record['geohash'] = '"' +  '","'.join(list(geohash.encode(float(row[2]), float(row[3])))) + '"'
        except Exception:
            record['geohash'] = '"_"'
        ## profile date time
        try:
            dt_profile = datetime.datetime.strptime(row[1], "%Y%m%d%H%M%S")
            epoch = datetime.datetime(1970, 1, 1)
            diff = dt_profile-epoch
            print(row[1])
            locaTimestamp = diff.days * 24 * 3600 + diff.seconds
            #locaTimestamp = time.mktime(dt_profile.timetuple())
            record['profiledate'] = str(locaTimestamp)
            timehashStr = timehash.encode(locaTimestamp)
            record['timehash'] = '"' + '","'.join(list(timehashStr)) + '"'
        except ValueError:
            timehashStr = '_'
            record['profiledate'] = '"' + row[1] + '"'
            record['timehash'] = '"_"'
        ## update date time
        try:
            dt_update = datetime.datetime.strptime(row[7], "%Y%m%d%H%M%S")
            locaTimestamp = time.mktime(dt_update.timetuple())
            record['updatedate'] = str(locaTimestamp)
        except ValueError:
            record['updatedate'] = row[7]
        ## procedure uri
        param = {"key": str('"platformnumber___' + record["platformnumber"]+ '"') }
        r1 = requests.get(snanny_system_view_rest, params=param)
        data = r1.json()
        if (len(data["rows"])>0):
            record['procedurekey'] = str('"' + data["rows"][0]["id"] + '"')
            # filePath
            record['filepath'] = rootFilePath + row[0]
            recordDataString = ""
            with open(template_file, "rt") as fin:
                for line in fin:
                    foundPatList = re.findall('___[a-z]*___', line)
                    for pat in foundPatList:
                        line= line.replace(pat, record[pat.split('___')[1]])
                    recordDataString+=line
            fin.close()
            #print(recordDataString)
            # push to couchbase
            try:
                c.set(record['localuuid'] + '_' +  timehashStr, json.loads(recordDataString));
            except ValueError:
                print('Insert failure:')
                print(recordDataString)
        else:
            print("no platform metadata available")
    else:
        print("header line")
csvfile.close()
c.close()


    




