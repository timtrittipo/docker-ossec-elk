This document will guide you through the installation and configuration of ELK Stack and OSSEC HIDS for their integration.

We will make use of expanded logging features that have been implemented in our OSSEC Github fork, our OSSEC rule set, our OSSEC RESTful API, custom Logstash/Elaskticsearch configurations and Kibana hardcoded modifications. See below a more detailed description of the mentioned components:

OSSEC rule set
Includes new rules and decoders. In addition, compliance information has been included mapping rules with PCI DSS controls and CIS benchmark requirements. This rule set is updated periodically in our Github repository.

OSSEC expanded JSON output
Additional fields have been included in the alerts output, for better integration with Elasticsearch, for example to add compliance controls information. As well, JSON output has been implemented for raw events (archives), and as an output option for ossec binaries (e.g. agent_control).

OSSEC RESTful API
Provides an interface to interact with OSSEC from anything that can send an HTTP request. Will be used to monitor agent status and configuration and, in some cases, to manage your OSSEC installation.

Logstash and Elasticsearch
Logstash wil be used to add GeoIP information to OSSEC alerts, and to define how fields are going to be indexed, using a custom Elasticsearch template.

Kibana 4
Includes OSSEC Alerts, PCI DSS Compliance, CIS Benchmark, Agents management, Agents Info dashboards. It also hides non useful fields and displays a short description of compliance requirements on mouseover.

## An example container launch: 

`docker run -d -p 1514:1514/udp -p 514:514/udp -p 5601:5601  -v /somepath/ossec_mnt:/var/ossec/data --name ossec wazuh/ossec-elkstack`

## Available Configuration Parameters

* __AUTO_ENROLLMENT_ENABLED__: Specifies whether or not to enable auto-enrollment via ossec-authd. Defaults to `true`;
* __AUTHD_OPTIONS__: Options to passed ossec-authd, other than -p and -g. Defaults to empty;
* __SYSLOG_FORWADING_ENABLED__: Specify whether syslog forwarding is enabled or not. Defaults to `false`.
* __SYSLOG_FORWARDING_SERVER_IP__: The IP for the syslog server to send messagse to, required for syslog fowarding. No default.
* __SYSLOG_FORWARDING_SERVER_PORT__: The destination port for syslog messages. Default is `514`.
* __SYSLOG_FORWARDING_FORMAT__: The syslog message format to use. Default is `default`.

**Please note**: All SYSLOG configuration variables are only applicable to the first time setup. Once the container's data volume has been initialized, all the configuration options for OSSEC can be changed.

#### ossec-execd is not enabled

Since this is a docker container, ossec-execd really isn't a great idea anyway. Having a log server, such as graylog, react based on log entries is the recommended approach.

## Access to Kibana:

`http://ipmachine:5601`

## Add agents with:

`docker exec -it ossec /var/ossec/bin/manage_agents`

## Don't forget

Don't forget to do a `docker exec -it ossec /var/ossec/bin/ossec-control restart` after you'd added your first agent. 
