# Work_Zone

Work zone code and documentation for WZDx, iCone, etc. 

| Build | Quality Gate | Code Coverage |
| :---- | :----------: | ------------: |
|       |              |               |

# WZDX Translator

## Project Description

This is an open source, proof of concept solution for translating work zone data in the form of COtrip/Salesforce, iCone, and NavJOY messages to the standardized WZDx 3.1 format. This project was developed for CDOT. A unique translator has been developed for each of these message types. These translators read in the source message, parse out specific fields, and generate a WZDx 3.1 message. For more information on these message formats and the data mappings between these messages and the WZDx format, see the [documentation](translator/docs). Sample files are located [here](translator/sample%20files). All these translators are built to run from the command line and from GCP cloud functions, hosted within the CDOT OIM WZDX environment, connected to the RTDH (real time data hub). For more information on cloud hosting, see [GCP_cloud_function](translator/GCP_cloud_function). 

## Prerequisites

Requires:

- Python 3.6 (or higher)
- All libraries present in requirement.txt

## Environment Setup

This code requires Python 3.6 or a higher version. If you haven’t already, download Python and pip. You can install the required packages by running the following command:

```
pip install -r requirements.txt
```

#### Environment variable

Please set up the following environment variable for your local computer before running the script.

Runtime Environment Variables:

| Name                 |          Value           |                                    Description |
| :------------------- | :----------------------: | ---------------------------------------------: |
| contact_name         |       Ashley Nylen       |                      name of WZDx feed contact |
| contact_email        | ashley.nylen@state.co.us |                     email of WZDx feed contact |
| issuing_organization |           CDOT           | name of the organization issuing the WZDx feed |

Example usage:
for mac computer run the following script to initialize the environment variable:

```
env_var.sh
```

### Execution for iCone translator

#### Run the translator script (from Work_Zone)

```
python -m translator.icone_translator inputfile.xml --outputFile outputfile.geojson
```

Example usage:

```
python -m translator.icone_translator 'translator/sample files/icone data/incidents_extended.xml' 
```

### Execution for COtrip translator

#### Run the translator script (from Work_Zone)

```
python -m translator.cotrip_translator inputfile.json --outputFile outputfile.geojson
```

Example usage:

```
python -m translator.cotrip_translator 'translator/sample files/cotrip_data/cotrip_1.json'
```

### Execution for NavJoy 568 translator
This translator reads in a NavJoy 568 speed reduction form and translates it into a WZDx message. Many of the 568 messages cover 2 directions of traffic, and are thus expanded into 2 WZDx messages, one for each direction. 

The NavJoy Work Zone feed is being translated into WZDx by NavJoy themselves, the source and WZDx example messages are located here: [Navjoy Sample Data](translator/sample%20files/navjoy_data)

#### Run the translator script (from Work_Zone)

```
python -m translator.navjoy_translator inputfile.json --outputFile outputfile.geojson
```

Example usage:

```
python -m translator.navjoy_translator 'translator/sample files/navjoy_data/568_data.json'
```

### Execution for Combine_wzdx

#### Run the translator script (from Work_Zone/translator)

```
python combine_wzdx.py icone_wzdx_output_message_file cotrip_wzdx_output_message_file --outputFile outputfile.geojson
```

Example usage:

```
python combine_wzdx.py '../sample files/Output Message/icone_wzdx_translated.geojson' '../sample files/Output Message/cotrip_wzdx_translated_output_message.geojson'
```

### Unit Testing

#### Run the unit test for translator script (from root directory)

```
python -m pytest 'tests/' -v
```

Ensure you have your environment configured correctly (as described above).

### Google Cloud Functions

iCone, COTrip, and NavJoy 568 message translators have been hosted in the GCP as cloud functions. All functions will publish generated messages to the wzdx_messages pub/sub topic in their respective environments, and will publish unsupported/invalid messages to a sepate topic, specified in the environment variables of each function. 

#### iCone
The iCone cloud function is triggered once per day by a pub/sub topic. The cloud function is located at [https://console.cloud.google.com/functions/details/us-central1/auto_icone_translator_ftp?project=cdot-oim-wzdx-dev](https://console.cloud.google.com/functions/details/us-central1/auto_icone_translator_ftp?project=cdot-oim-wzdx-dev)

A system was created in google cloud platform to automatically translate iCone data to WZDx message. This system consists of two pubsub topics and a cloud function. A cloud scheduler automatically sends a message to a pubsub topic which triggers the cloud function. The cloud function retrieves iCone data from an ftp server (ftp://iconetraffic.com:42663) and translates to WZDx message. It validates the WZDx message with json schema and publishes the message to a pubsub topic.

![alt text](translator/GCP_cloud_function/iCone%20Translator%20block%20diagram.png)

#### COTrip/SalesForce
The cotrip cloud function does not exist. It will be triggered when a new cotrip alert is placed in the CDOT RTDH cotrip-alerts-raw-oim-wzdx-integration pub/sub topic. The function will be located at [https://console.cloud.google.com/functions/details/us-central1/salesforce_data?folder=&organizationId=&project=cdot-oim-wzdx-prod](https://console.cloud.google.com/functions/details/us-central1/salesforce_data?folder=&organizationId=&project=cdot-oim-wzdx-prod)

#### NavJoy 568


### Message Combination Logic:

The `combine_wzdx` script file combines the output from the iCone and COtrip translators, based on overlapping geography, into a single improved WZDx message. The COtrip message set contains significantly more data, and is used as the base for this new combined message. The script then finds any geographically co-located messages from the iCone data set, pulls in the additional information (comprised of vehicle impact data and data sources) and publishes a new, combined WZDx message. Future state of this script will include additional data fields from the iCone data set as they become available.


# Google Cloud Hosting
All of the translators featured in this repo are hosted in the CDOT GCP Cloud as function apps. Each function is triggered by an event (either a message being generated in the RTDH or time of day), translates the given message to WZDx, and publishes that WZDx message to a pub/sub topic. The triggers for each GCP function are listed above, by translator. 

## Triggers

#### iCone
[https://console.cloud.google.com/functions/details/us-central1/auto_icone_translator_ftp?project=cdot-oim-wzdx-dev](https://console.cloud.google.com/functions/details/us-central1/auto_icone_translator_ftp?project=cdot-oim-wzdx-dev)

The iCone cloud function is triggered once per day by a pub/sub topic. The cloud function downloads the latest iCone incidents data from the iCone FTP server to translate.

![alt text](translator/docs/iCone%20Translator%20block%20diagram.png)

#### COTrip/SalesForce
[https://console.cloud.google.com/functions/details/us-central1/salesforce_data?folder=&organizationId=&project=cdot-oim-wzdx-prod](https://console.cloud.google.com/functions/details/us-central1/salesforce_data?folder=&organizationId=&project=cdot-oim-wzdx-prod)

The cotrip cloud function is triggered manually (for now) by an HTTP request. retrieves the most recent alert messages from the CDOT RTDH cotrip-alerts-raw-oim-wzdx-integration pub/sub topic.

#### NavJoy 568
[https://console.cloud.google.com/functions/details/us-central1/navjoy-568-translator?project=cdot-oim-wzdx-dev](https://console.cloud.google.com/functions/details/us-central1/navjoy-568-translator?project=cdot-oim-wzdx-dev)

The navjoy cloud function is triggered once per day by a pub/sub topic. The cloud function downloads the latest Navjoy 568 JSON data from the [NavJoy REST API](https://proxy.assetgov.com/napi/open-api/Form568?api_key=d0c2feba6d38df6fdd284d370cbd69636f337d48&limit=1000&skip=0).

## Deployment
To deploy to a function app, simply zip the entire solution (everything within Work_Zone, no sub folders), upload it to the function through the ZIP deployment process, set the build environment variables (described below), and deploy. 

## Environment

### Shared
Runtime Environment Variables
| Name                 |          Value           |                        Description |
| :------------------- | :----------------------: | ---------------------------------: |
| contact_name         |       Ashley Nylen       |         WZDx metadata contact name |
| contact_email        | ashley.nylen@state.co.us |        WZDx metadata contact email |
| issuing_organization |           CDOT           | WZDx metadata issuing organization |


### iCone: auto_icone_translator_ftp
Build Environment Variables
| Name                   |          Value          |                                   Description |
| :--------------------- | :---------------------: | --------------------------------------------: |
| GOOGLE_FUNCTION_SOURCE | gcp_icone_translator.py | GCP function script name at root of Work_Zone |

Runtime Environment Variables
| Name                           |           Value            |                                              Description |
| :----------------------------- | :------------------------: | -------------------------------------------------------: |
| icone_ftp_username_secret_name |     icone_ftp_username     |      name of secret containing iCone ftp server username |
| icone_ftp_password_secret_name |     icone_ftp_password     |      name of secret containing iCone ftp server password |
| ftp_server_address             |      iconetraffic.com      |                                 iCone ftp server address |
| ftp_port                       |           42663            |                             iCone ftp server port number |
| ftp_icone_file_path            |       incidents.xml        |                         The icone filename in ftp server |
| unsupported_messages_topic_id  | unsupported_messages_icone | pub/sub topic id to send unsupported/invalid messages to |
| project_id                     |     cdot-oim-wzdx-dev      |                                           GCP project ID |
| wzdx_topic_id                  |    wzdx_messages_icone     |                          Generated WZDx pub/sub topic ID |

### COTrip: salesforce_data
Build Environment Variables
| Name                   |          Value           |                                   Description |
| :--------------------- | :----------------------: | --------------------------------------------: |
| GOOGLE_FUNCTION_SOURCE | gcp_cotrip_translator.py | GCP function script name at root of Work_Zone |

Runtime Environment Variables
| Name                          |                                                        Value                                                        |                                              Description |
| :---------------------------- | :-----------------------------------------------------------------------------------------------------------------: | -------------------------------------------------------: |
| unsupported_messages_topic_id |                                             unsupported_messages_cotrip                                             | pub/sub topic id to send unsupported/invalid messages to |
| project_id                    |                                                 cdot-oim-wzdx-prod                                                  |                                           GCP project ID |
| wzdx_topic_id                 |                                                wzdx_messages_cotrip                                                 |                          Generated WZDx pub/sub topic ID |
| rtdh_project_id               |                                                   cdot-rtdh-prod                                                    |                    Real time data hub project identifier |
| rtdh_cotrip_alerts_topic_id   |                                     cotrip-alerts-standard-oim-wzdx-integration                                     |                   Cotrip alerts topic id within the RTDH |
| navjoy_568_endpoint           | https://proxy.assetgov.com/napi/open-api/Form568?api_key=d0c2feba6d38df6fdd284d370cbd69636f337d48&limit=1000&skip=0 |                     GCP script name at root of Work_Zone |

### NavJOY 568: navjoy-568-translator
Build Environment Variables
| Name                   |         Value         |                          Description |
| :--------------------- | :-------------------: | -----------------------------------: |
| GOOGLE_FUNCTION_SOURCE | gcp_568_translator.py | GCP script name at root of Work_Zone |

Runtime Environment Variables
| Name                          |                                                        Value                                                        |                                              Description |
| :---------------------------- | :-----------------------------------------------------------------------------------------------------------------: | -------------------------------------------------------: |
| unsupported_messages_topic_id |                                           unsupported_messages_navjoy_568                                           | pub/sub topic id to send unsupported/invalid messages to |
| project_id                    |                                                  cdot-oim-wzdx-dev                                                  |                                           GCP project ID |
| wzdx_topic_id                 |                                                wzdx_messages_navjoy                                                 |                          Generated WZDx pub/sub topic ID |
| navjoy_568_endpoint           | https://proxy.assetgov.com/napi/open-api/Form568?api_key=d0c2feba6d38df6fdd284d370cbd69636f337d48&limit=1000&skip=0 |                     GCP script name at root of Work_Zone |


### Documentation

documentation for iCone to WZDx translator is located here: [docs](translator/docs)

### Guidelines

- Issues
  - Create issues using the SMART goals outline (Specific, Measurable, Actionable, Realistic and Time-Aware)
- PR (Pull Requests)
  - Create all pull requests from the master branch
  - Create small, narrowly focused PRs
  - Maintain a clean commit history so that they are easier to review

## Contact Information

Contact Name: Ashley Nylen
Contact Information: [ashley.nylen@state.co.us]

## Abbreviations

WZDx: Workzone Data Exchange
