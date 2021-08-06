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

### Google Cloud Function

A system was created in google cloud platform to automatically translate iCone data to WZDx message. This system consists of two pubsub topics and a cloud function. A cloud scheduler automatically sends a message to a pubsub topic which triggers the cloud function. The cloud function retrieves iCone data from an ftp server (ftp://iconetraffic.com:42663) and translates to WZDx message. It validates the WZDx message with json schema and publishes the message to a pubsub topic.

![alt text](translator/GCP_cloud_function/iCone%20Translator%20block%20diagram.png)

### Message Combination Logic:

The `combine_wzdx` script file combines the output from the iCone and COtrip translators, based on overlapping geography, into a single improved WZDx message. The COtrip message set contains significantly more data, and is used as the base for this new combined message. The script then finds any geographically co-located messages from the iCone data set, pulls in the additional information (comprised of vehicle impact data and data sources) and publishes a new, combined WZDx message. Future state of this script will include additional data fields from the iCone data set as they become available.

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
