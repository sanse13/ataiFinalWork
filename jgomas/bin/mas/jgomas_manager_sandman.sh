#!/bin/sh

java -classpath "lib/jade.jar:lib/jadeTools.jar:lib/Base64.jar:lib/http.jar:lib/iiop.jar:lib/beangenerator.jar:lib/jgomas.jar:lib/jason.jar:lib/JasonJGomas.jar:classes:." jade.Boot -gui -host 158.42.184.197 "Manager:es.upv.dsic.gti_ia.jgomas.CManager(6,map_04,125,10)"
