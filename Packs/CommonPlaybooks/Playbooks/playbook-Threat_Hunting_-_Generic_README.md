This playbook purpose is to allow threat hunting for IOC's in your enterprise.
This playbook currently supports the following integrations:
- Splunk
- Qradar
- Pan-os
- Cortex data lake 
- Autofocus

## Dependencies
This playbook uses the following sub-playbooks, integrations, and scripts.

### Sub-playbooks
* Palo Alto Networks - Hunting And Threat Detection
* QRadar Indicator Hunting V2
* Splunk Indicator Hunting

### Integrations
This playbook does not use any integrations.

### Scripts
This playbook does not use any scripts.

### Commands
This playbook does not use any commands.

## Playbook Inputs
---

| **Name** | **Description** | **Default Value** | **Required** |
| --- | --- | --- | --- |
| MD5 | The MD5 hash file or an array of hashes to search. |  | Optional |
| SHA256 | The SHA256  hash file or an array of hashes to search.. |  | Optional |
| Hostname | Hostname of the machine on which the file is located. |  | Optional |
| SHA1 | The SHA1 hash file or an array of hashes to search. | D4ABAC114DBE28BAD8855C10D37F2B727177C9CA | Optional |
| IPAddress | Source or destination IP to search. Can be a single address or an array of addresses.<br/> |  | Optional |
| URLDomain | Domain or Url can be single or an array of domain/urls to search. By default the LIKE clause is used. |  | Optional |
| InternalRange | A list of internal IP ranges to check IP addresses against. The list should be provided in CIDR notation, separated by commas. An example of a list of ranges would be: "172.16.0.0/12,10.0.0.0/8,192.168.0.0/16" \(without quotes\). If a list is not provided, will use default list provided in the IsIPInRanges script \(the known IPv4 private address ranges\). |  | Optional |
| InternalDomainName | The organizations internal domain name. This is provided for the script IsInternalHostName that checks if the detected host names are internal or external if the hosts contain the internal domains suffix. For example demisto.com. If there is more than one domain, use the \| character to separate values such as \(demisto.com\|test.com\) |  | Optional |
| InternalHostRegex | This is provided for the script IsInternalHostName that checks if the detected host names are internal or external. if the hosts match the organizations naming convention. For example the host testpc1 will have the following regex \\w\{6\}\\d\{1\} |  | Optional |

## Playbook Outputs
---

| **Path** | **Description** | **Type** |
| --- | --- | --- |
| Splunk.DetectedUsers | Users detected based on the username field in your search. | string |
| Splunk.DetectedInternalIPs | Internal IP addresses detected by your search. | string |
| Splunk.DetectedExternalIPs | External IP addresses detected by your search. | string |
| Splunk.DetectedInternalHosts | Internal host names detected based on the fields in your search. | string |
| Splunk.DetectedExternalHosts | External host names detected based on the fields in your search. | string |
| PANWHunting.DetectedUsers | User or array of users that were detected during hunting. | string |
| PANWHunting.DetectedInternalIPs | Internal IP addresses detected based on fields and inputs in your search. | string |
| PANWHunting.DetectedExternalIPs | External IP addresses detected based on fields and inputs in your search. | string |
| PANWHunting.DetectedInternalHosts | Internal host names detected based on fields and inputs in your search. | string |
| PANWHunting.DetectedExternalHosts | External host names detected based on fields and inputs in your search. | string |
| QRadar.DetectedUsers | Users detected based on the username field in your search. | string |
| QRadar.DetectedInternalIPs | Internal IP addresses detected based on fields and inputs in your search. | string |
| QRadar.DetectedExternalIPs | External IP addresses detected based on fields and inputs in your search. | string |
| QRadar.DetectedInternalHosts | Internal host names detected based on hosts in your assets table. Note that the data accuracy depends on how the Asset mapping is configured in QRadar. | string |
| QRadar.DetectedExternalHosts | External host names detected based on hosts in your assets table. Note that the data accuracy depends on how the Asset mapping is configured in QRadar. | string |

## Playbook Image
---
![Threat Hunting - Generic ](Insert the link to your image here)