#!/usr/bin/env python

# Wazuh installer for ELK integration index and dashboards
# Copyright (C) 2016 Wazuh, Inc. <info@wazuh.com>.
# May 23, 2016.
#
# This program is a free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.

import sys
import datetime
import json
import urllib2
try:
    import requests
except:
    print("[ERROR] Requests library not found. Please, install python-pip and execute 'pip install requests'.")
    sys.exit(1)

# Print available arguments
if ((len(sys.argv) > 1) and ((sys.argv[1] == '-h') or (sys.argv[1] == '-help'))):
    print("[HELP] Available arguments:\n-url to specify the Elasticsearch API url, instead of using default address (http://localhost:9200)\n-kversion to specify a Kibana version, instead of taking it from Elasticsearch.")
    sys.exit(1)

# URL (Read from argument, or http://localhost:9200)
if ((len(sys.argv) > 2) and (sys.argv[1] == '-url')):
    URL = sys.argv[2]
elif ((len(sys.argv) > 4) and (sys.argv[3] == '-url')):
    URL = sys.argv[4]
else:
    URL = 'http://localhost:9200'

# Kibana version control (Read from argument, or take from Elasticsearch)
if ((len(sys.argv) > 2) and (sys.argv[1] == '-kversion')):
    K_VERSION = sys.argv[2]
elif ((len(sys.argv) > 4) and (sys.argv[3] == '-kversion')):
    K_VERSION = sys.argv[4]
else:
    exit = False
    try:
        r = requests.get('{0}/.kibana/config/_search'.format(URL))
    except:
        print("[ERROR] Could not connect with Elasticsearch at {0}".format(URL))
        sys.exit(1)
    try:
        jsonResponse = r.json()
        #If more than one Kibana version, error and list versions
        if (jsonResponse["hits"]["total"] != 1):
            print("[ERROR] Multiple Kibana versions found in Elasticsearch. Execute the installer with -kversion parameter.")
            print("+ Kibana versions found:")
            for hit in jsonResponse["hits"]["hits"]:
                print ("     {0}".format(hit['_id']))
            exit = True
        else:
            K_VERSION = jsonResponse["hits"]["hits"][0]["_id"]
    except:
        #Error reaching Elasticsearch
        print("[ERROR] Could not get Kibana versions from Elasticsearch. Check Elasticsearch URL or start Kibana service from first time.")
        exit = True
    if (exit):
        sys.exit(1)

# Remote github files
MAPPING_FILE_URL = "https://raw.githubusercontent.com/wazuh/ossec-wazuh/stable/extensions/elasticsearch/elastic-ossec-template.json"
OBJECTS_FILE_URL = "https://raw.githubusercontent.com/wazuh/ossec-wazuh/stable/extensions/kibana/kibana-ossecwazuh-dashboards.json"

# Test if .kibana index exists in Elasticsearch
try:
    r = requests.get('{0}/.kibana/'.format(URL))
except:
    print("[ERROR] Could not connect with Elasticsearch at {0}".format(URL))
    sys.exit(1)
if (r.status_code != 200):
    print("[ERROR] .kibana index does not exists. Start Kibana service for first time.")
    sys.exit(1)

# Import mapping to elasticsearch
print("+ Importing mapping template...")
try:
    r = requests.put('{0}/_template/ossec/'.format(URL), data = urllib2.urlopen(MAPPING_FILE_URL).read())
except:
    print("[ERROR] Could not connect with Elasticsearch at {0}".format(URL))
    sys.exit(1)
if (r.text != '{"acknowledged":true}'):
    print("[ERROR] Mapping template could not be imported.")
    sys.exit(1)

# Create ossec-* index
print("+ Creating ossec-* index...")
try:
    r = requests.post('{0}/.kibana/index-pattern/ossec-*?op_type=create'.format(URL), data = '{title: "ossec-*", timeFieldName: "@timestamp"}')
except:
    print("[ERROR] Could not connect with Elasticsearch at {0}".format(URL))
    sys.exit(1)
if (r.status_code != 201):
    print("[ERROR] Could not create ossec-* index. It already exists?")
    sys.exit(1)

# Create ossec-* index pattern
print("+ Creating ossec-* index pattern...")
try:
    r = requests.post('{0}/.kibana/index-pattern/ossec-*'.format(URL), data = '{"title":"ossec-*","timeFieldName":"@timestamp"}')
except:
    print("[ERROR] Could not connect with Elasticsearch at {0}".format(URL))
    sys.exit(1)
if (r.status_code != 200):
    print("[ERROR] Could not create ossec-* index pattern. Check if the pattern exists.")
    sys.exit(1)

# Initializing ossec-* index pattern
print("+ Initializing ossec-* index pattern...")
try:
    r = requests.post('{0}/ossec-{1}/ossec/'.format(URL, datetime.date.today().strftime('%Y.%m.%d')), data = '{"rule": { "group": "", "sidid": 0, "firedtimes": 1, "groups": [ ], "PCI_DSS": [ ], "description": "This is the first alert on your ELK Cluster, please start OSSEC Manager and Logstash sever to start ship alerts.", "AlertLevel": 0 }, "full_log": "This is the first alert on your ELK Cluster, please start OSSEC Manager and Logstash sever to start ship alerts.", "decoder": { }, "location": "", "@version": "1", "@timestamp": "'+datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')+'", "path": "", "host": "", "type": "ossec-alerts", "AgentName": "" }')
except:
    print("[ERROR] Could not connect with Elasticsearch at {0}".format(URL))
    sys.exit(1)
if (r.status_code != 201):
    print("[ERROR] Could not insert example data into ossec-* index pattern. Check if the pattern exists.")
    sys.exit(1)

# Set ossec-* index by default
print("+ Setting ossec-* index as default index for Kibana...")
try:
    r = requests.post('{0}/.kibana/config/{1}/_update'.format(URL, K_VERSION), data= '{"doc":{"defaultIndex":"ossec-*"}}')
except:
    print("[ERROR] Could not connect with Elasticsearch at {0}".format(URL))
    sys.exit(1)
if (r.status_code != 200):
    print("[ERROR] Could not set ossec-* as default index for Kibana. Is the Kibana version correct?")
    sys.exit(1)

# Set last 24h as default search time
print("+ Setting last 24h as default search time...")
try:
    r = requests.post('{0}/.kibana/config/{1}/_update'.format(URL, K_VERSION), data= '{"doc":{"defaultIndex":"ossec-*","timepicker:timeDefaults":"{\\n \\"from\\": \\"now-24h\\",\\n \\"to\\": \\"now\\",\\n \\"mode\\": \\"quick\\"\\n}"}}')
except:
    print("[ERROR] Could not connect with Elasticsearch at {0}".format(URL))
    sys.exit(1)
if (r.status_code != 200):
    print("[ERROR] Could not set last 24h as default search time. Is the Kibana version correct?")
    sys.exit(1)

# Import dashboards, searches and visualizations
print("+ Importing Kibana objects (dashboards, searches and visualizations). This can take some time...")
jsonObjects = {}
#Download file and convert to JSON
try:
    objects = urllib2.urlopen(OBJECTS_FILE_URL).read()
    jsonObjects = json.loads(objects)
except:
    print("[ERROR] Could not load the objects JSON data")
    sys.exit(1)
importSuccess = True
#Iterate over the JSON
for kobject in jsonObjects:
    try:
        #Import object
        r = requests.post('{0}/.kibana/{1}/{2}?op_type=create'.format(URL, kobject["_type"], kobject["_id"]), data = json.dumps(kobject["_source"]))
        if (r.status_code != 201):
            importSuccess = False
            print("[ERROR] Error importing {0} {1}. It already exists?".format(kobject["_type"], kobject["_id"]))
    except:
        importSuccess = False
        print("[ERROR] Could not connect with Elasticsearch at {0}".format(URL))

#Final installer message
if (importSuccess):
    print("[SUCCESS] Kibana for Wazuh is ready for using")
    sys.exit(0)
else:
    print("[ERROR] Kibana for Wazuh is installed, but all the objects were not imported.")
    sys.exit(1)
