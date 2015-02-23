import csv
import netCDF4
from netCDF4 import num2date, date2num, chartostring
import time
import datetime
import uuid
import string
import re
import os


csv_file_path = "/home/coriolis_exp/spool/co05/co0508/ar_index_global_meta.txt"
template_file = "/home/isi-projets/sensorNanny/data/archive/argo/swe/templates/sml_template.xml"
target_directory= "/home/isi-projets/sensorNanny/data/archive/argo/swe/systems/"
####
record = {}
with open(csv_file_path, 'rb') as csvfile:
  spamreader = csv.reader(csvfile, delimiter=',')
  for row in spamreader:
    if(not row[0].startswith('# ') and not row[0].startswith('file')):
      print '/home/coriolis_exp/spool/co05/co0508/dac/' + row[0]
      nc = netCDF4.Dataset ('/home/coriolis_exp/spool/co05/co0508/dac/' + row[0])
      # platform number
      platform_number = str(chartostring(nc.variables['PLATFORM_NUMBER'][:])).strip()
      record['wmoplatformcode'] = platform_number
      record['name'] = 'ARGO profiling float ' + platform_number
      # platform model
      if 'PLATFORM_MODEL' in nc.variables.keys():
        platform_model = str(chartostring(nc.variables['PLATFORM_MODEL'][:])).strip()
      else:
	platform_model = ''
      # platform_maker
      platform_maker = str(chartostring(nc.variables['PLATFORM_MAKER'][:])).strip()    
      record['platformmaker'] = platform_maker
      # description
      record['description'] = platform_maker + ' ' + platform_model
      # localuuid
      record['localuuid'] = str(uuid.uuid1())
      # platform_type
      if 'PLATFORM_TYPE' in nc.variables.keys():
        platform_type = str(chartostring(nc.variables['PLATFORM_TYPE'][:])).strip()       
        record['platformtype'] = ' <!-- #### WMO PLATFORM TYPE ##### -->' \
		      + '<sml:identifier> \n' \
	              + '  <sml:Term definition="http://www.ifremer.fr/tematres/vocab/index.php?tema=50"> \n' \
                      + '    <sml:label>platformType</sml:label>  \n' \
                      + '    <sml:codeSpace xlink:href="http://www.ifremer.fr/tematres/vocab/index.php?tema=36"/> \n' \
                      + '    <sml:value>'+ platform_type +'</sml:value> \n' \
                      + '  </sml:Term> \n' \
		      + '</sml:identifier> \n'
      else:
	record['platformtype'] = ' '
      if 'PLATFORM_SERIAL_NO' in nc.variables.keys():
        platform_serial_number = str(chartostring(nc.variables['PLATFORM_SERIAL_NO'][:])).strip()       
        record['platformserialno'] = ' <!-- #### WMO PLATFORM TYPE ##### -->' \
		      + '<sml:identifier> \n' \
	              + '  <sml:Term definition="http://www.ifremer.fr/tematres/vocab/index.php?tema=48"> \n' \
                      + '    <sml:label>serialNumber</sml:label>  \n' \
                      + '    <sml:value>'+ platform_serial_number +'</sml:value> \n' \
                      + '  </sml:Term> \n' \
		      + '</sml:identifier> \n'
      else:
	record['platformserialno'] = ' '
      # launchdate
      launch_date = str(chartostring(nc.variables['LAUNCH_DATE'][:])).strip()
      try:
        dt_start = datetime.datetime.strptime(launch_date, "%Y%m%d%H%M%S")
        record['launchdate'] = dt_start.isoformat()
      except ValueError:
        record['launchdate'] = launch_date            
      # enddate
      end_date = str(chartostring(nc.variables['END_MISSION_DATE'][:])).strip()
      try:
        dt_end = datetime.datetime.strptime(end_date, "%Y%m%d%H%M%S")
        record['enddate'] = '<gml:endPosition>' + dt_end.isoformat() +'</gml:endPosition>'
      except ValueError:     
        record['enddate'] = '<gml:endPosition>' + end_date +'</gml:endPosition>'
      # pi_name
      pi_name = str(chartostring(nc.variables['PI_NAME'][:])).strip()      
      record['piname'] = pi_name
      # project name
      project_name  = str(chartostring(nc.variables['PROJECT_NAME'][:])).strip()     
      record['projectname'] = project_name
      # launch_latitude
      launch_latitude  = nc.variables['LAUNCH_LATITUDE'][:]
      record['launch_latitude'] = str(launch_latitude)
      # launch_longitude
      launch_longitude  = nc.variables['LAUNCH_LONGITUDE'][:]
      record['launch_longitude'] = str(launch_longitude)
      with open(target_directory + '/'+ 'argo_' + record['wmoplatformcode'] + ".xml", "wt") as fout:     
        with open(template_file, "rt") as fin:
          for line in fin:
	    foundPatList = re.findall('___[a-z]*___', line)
	    print foundPatList
  	    for pat in foundPatList:
              line= line.replace(pat, record[pat.split('___')[1]])
	    fout.write(line)
        fin.close()
      fout.close()
      #break

    




