Cisco TAC First Responder script for Cisco Telemetry Broker.

This hosted script aids in the generation, compression, and transmission of a Cisco Telemetry Broker mayday file. 

Example output:
```
admin@ctb-node:~$ curl -s https://raw.githubusercontent.com/CiscoCX/CiscoTacFirstResponder-CiscoTelemetryBroker/main/getmayday.py | sudo python3 - upload -c 611111111 -t mkFAKEk2Y12345yuEkz

*** Creating Support Bundle, this may take some time
2023/07/05 16:55:33 running mayday build commit: e82e0abfb9bbf598ca15079273c303e38d49c1dd
2023/07/05 16:55:33 loading config from /etc/mayday/default.json
{removed-for-brevity}
2023/07/05 16:55:47 Output saved in /tmp/mayday-ctb-broker-node-VMware-1234a567890b123c-de4567f89ghi0j12.20230705.1655.tar.gz
2023/07/05 16:55:47 All done!

Uploading file to TAC Case. This may take some time.
######################################################################## 100.0%
`/tmp/mayday-ctb-broker-node-VMware-1234a567890b123c-de4567f89ghi0j12.20230705.1655.tar.gz` successfully uploaded to 611111111
admin@ctb-node:~$
```

If you do not run script as root / sudo, the script will error out. 
Example output: 
```
admin@ctb-node:~$ curl -s https://raw.githubusercontent.com/CiscoCX/CiscoTacFirstResponder-CiscoTelemetryBroker/main/getmayday.py | python3 - upload -c 611111111 -t mkFAKEk2Y12345yuEkz
You are not root, re-run this script as root. Exiting.
admin@ctb-node:~$
```

If you prefer to no upload the collected data you may use the 'no-upload' option. This option will not attempt to upload the data to Cisco TAC case.

```
admin@ctb-node:~$ curl -s https://raw.githubusercontent.com/CiscoCX/CiscoTacFirstResponder-CiscoTelemetryBroker/main/getmayday.py | sudo python3 - no-upload -c 611111111 -t mkFAKEk2Y12345yuEkz

*** Creating Support Bundle, this may take some time
2023/07/05 16:55:33 running mayday build commit: e82e0abfb9bbf598ca15079273c303e38d49c1dd
2023/07/05 16:55:33 loading config from /etc/mayday/default.json
{removed-for-brevity}
2023/07/05 16:55:47 Output saved in /tmp/mayday-ctb-broker-node-VMware-1234a567890b123c-de4567f89ghi0j12.20230705.1655.tar.gz
2023/07/05 16:55:47 All done!

admin@ctb-node:~$
```
