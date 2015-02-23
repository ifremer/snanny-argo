#!/bin/csh -f
set dir1=/home/isi-projets/sensorNanny/data/archive/argo/swe/systems
foreach file ($dir1/*.xml)
	if (-d $file) then
		echo "Skipping $file (is a directory)"
        else
		echo "Inserting $file"
		echo '<?xml version="1.0" encoding="UTF-8"?> <swes:InsertSensor service="SOS" version="2.0.0" xmlns:swes="http://www.opengis.net/swes/2.0" xmlns:sos="http://www.opengis.net/sos/2.0" xmlns:swe="http://www.opengis.net/swe/2.0" xmlns:sml="http://www.opengis.net/sensorml/2.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/sos/2.0 http://schemas.opengis.net/sos/2.0/sosInsertSensor.xsd http://www.opengis.net/swes/2.0 http://schemas.opengis.net/swes/2.0/swes.xsd"> <swes:procedureDescriptionFormat>text/xml;subtype="http://www.opengis.net/om/2.0"</swes:procedureDescriptionFormat> <swes:procedureDescription>' > /tmp/requestInsert.xml
		cat $file >> /tmp/requestInsert.xml
 		echo  '</swes:procedureDescription> <swes:observableProperty></swes:observableProperty> </swes:InsertSensor>' >>  /tmp/requestInsert.xml
		curl -X POST --insecure -d @/tmp/requestInsert.xml 'https://isi.ifremer.fr/snanny-sostServer/sos?service=SOS&version=2.0&request=insertSensor' --header "Content-Type:text/xml"
        endif
end

