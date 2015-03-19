import csv
import netCDF4
from netCDF4 import num2date, date2num, chartostring
import time
import datetime
import uuid
import string
import re
import os
from couchbase import Couchbase
import json

def extractFields( ncmetafile ):
  record_xml = {}
  record_json = {}
  nc = netCDF4.Dataset ('/home/coriolis_exp/spool/co05/co0508/dac/' + row[0])
  # platform number
  platform_number = str(chartostring(nc.variables['PLATFORM_NUMBER'][:])).strip()
  record_json['wmoplatformcode'] = platform_number
  record_xml['wmoplatformcode'] = platform_number
  record_json['name'] = 'ARGO profiling float ' + platform_number
  record_xml['name'] = 'ARGO profiling float ' + platform_number
  # platform model
  if 'PLATFORM_MODEL' in nc.variables.keys():
    platform_model = str(chartostring(nc.variables['PLATFORM_MODEL'][:])).strip()
  else:
    platform_model = ''
  # platform_maker
  platform_maker = str(chartostring(nc.variables['PLATFORM_MAKER'][:])).strip()    
  record_json['platformmaker'] = platform_maker
  record_xml['platformmaker'] = platform_maker
  # description
  record_json['description'] = platform_maker + ' ' + platform_model
  record_xml['description'] = platform_maker + ' ' + platform_model
  # localuuid
  localUUID = str(uuid.uuid1())
  record_json['localuuid'] = localUUID
  record_xml['localuuid'] = localUUID
  # platform_type
  if 'PLATFORM_TYPE' in nc.variables.keys():
    platform_type = str(chartostring(nc.variables['PLATFORM_TYPE'][:])).strip()       
    record_json['platformtype'] = '      "platformType":"' + platform_type + '",\n'
    record_xml['platformtype'] = ' <!-- #### WMO PLATFORM TYPE ##### -->' \
      + '<sml:identifier> \n' \
      + '  <sml:Term definition="http://www.ifremer.fr/tematres/vocab/index.php?tema=50"> \n' \
      + '    <sml:label>platformType</sml:label>  \n' \
      + '    <sml:codeSpace xlink:href="http://www.ifremer.fr/tematres/vocab/index.php?tema=36"/> \n' \
      + '    <sml:value>'+ platform_type +'</sml:value> \n' \
      + '  </sml:Term> \n' \
      + '</sml:identifier> \n'
  else:
    record_json['platformtype'] = ''
    record_xml['platformtype'] = ''
  if 'PLATFORM_SERIAL_NO' in nc.variables.keys():
    platform_serial_number = str(chartostring(nc.variables['PLATFORM_SERIAL_NO'][:])).strip()       
    record_json['platformserialno'] =  '      "serialNumber":"' + platform_serial_number + '",\n'
    record_xml['platformserialno'] = ' <!-- #### WMO PLATFORM TYPE ##### -->' \
      + '<sml:identifier> \n' \
      + '  <sml:Term definition="http://www.ifremer.fr/tematres/vocab/index.php?tema=48"> \n' \
      + '    <sml:label>serialNumber</sml:label>  \n' \
      + '    <sml:value>'+ platform_serial_number +'</sml:value> \n' \
      + '  </sml:Term> \n' \
      + '</sml:identifier> \n'        
  else:
    record_json['platformserialno'] = ''
    record_xml['platformserialno'] = ''
  # launchdate
  launch_date = str(chartostring(nc.variables['LAUNCH_DATE'][:])).strip()
  try:
    dt_start = datetime.datetime.strptime(launch_date, "%Y%m%d%H%M%S")
    record_json['launchdate'] = dt_start.isoformat()
    record_xml['launchdate'] = dt_start.isoformat()
  except ValueError:
    record_json['launchdate'] = launch_date
    record_xml['launchdate'] = launch_date
  # enddate
  end_date = str(chartostring(nc.variables['END_MISSION_DATE'][:])).strip()
  try:
    dt_end = datetime.datetime.strptime(end_date, "%Y%m%d%H%M%S")
    record_json['enddate'] = '"to":"' + dt_end.isoformat() + '"\n'
    record_xml['enddate'] = '<gml:endPosition>' + dt_end.isoformat() +'</gml:endPosition>'
  except ValueError:     
    record_json['enddate'] = '"to":"' + end_date + '"\n'
    record_xml['enddate'] = '<gml:endPosition>' + end_date +'</gml:endPosition>'
  # pi_name
  pi_name = str(chartostring(nc.variables['PI_NAME'][:])).strip()      
  record_json['piname'] = pi_name 
  record_xml['piname'] = pi_name  
  # project name
  project_name  = str(chartostring(nc.variables['PROJECT_NAME'][:])).strip()     
  record_xml['projectname'] = project_name
  # launch_latitude
  launch_latitude  = nc.variables['LAUNCH_LATITUDE'][:]
  record_xml['launchlatitude'] = str(launch_latitude)
  # launch_longitude
  launch_longitude  = nc.variables['LAUNCH_LONGITUDE'][:]
  record_xml['launchlongitude'] = str(launch_longitude)
  nc.close()
  return [record_json, record_xml]

############
### main ###
############
csv_file_path = "/home/coriolis_exp/spool/co05/co0508/ar_index_global_meta.txt"
template_json_record = "../swe/templates/sml_idx_template.json"
template_xml_file = "../swe/templates/sml_template.xml"
target_directory= "../swe/systems/"
## couchbase connexion
c = Couchbase.connect(bucket='snanny_systems_dev', host='134.246.144.118', timeout=1)

####
record_xml = {}
record_json = {}
with open(csv_file_path, 'rb') as csvfile:
  spamreader = csv.reader(csvfile, delimiter=',')
  for row in spamreader:
    if(not row[0].startswith('# ') and not row[0].startswith('file')):
      ncmetafile = '/home/coriolis_exp/spool/co05/co0508/dac/' + row[0]
      print ncmetafile;
      records = extractFields(ncmetafile)
      record_json = records[0]
      record_xml = records[1]
      jsonRecordDataString = "";
      with open(template_json_record, "rt") as fin:
          for line in fin:
	    foundPatList = re.findall('___[a-z]*___', line)
	    print foundPatList
  	    for pat in foundPatList:
              line= line.replace(pat, record_json[pat.split('___')[1]])
	    jsonRecordDataString+=line
      fin.close()            
      # push to couchbase
      c.set(record_json['localuuid'], json.loads(jsonRecordDataString));
      ## create sensorML file
      with open(target_directory + '/'+ 'argo_' + record_xml['wmoplatformcode'] + ".xml", "wt") as fout:
        with open(template_xml_file, "rt") as fin:
          for line in fin:
	    foundPatList = re.findall('___[a-z]*___', line)
	    print foundPatList
  	    for pat in foundPatList:
              line= line.replace(pat, record_xml[pat.split('___')[1]])
	    fout.write(line)
        fin.close()
      fout.close()
      #break



