# Copyright 2020 Google LLC. This software is provided as is, without warranty or representation for any use or
# purpose. Your use of it is subject to your agreement with Google.

import os

PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT', 'cdot-rtdh-dev')

ENVIRONMENT = PROJECT.split('-')[-1]  # ['cdot', 'rtdh', 'dev' <-- this one ]

REGION = os.environ.get('GOOGLE_CLOUD_REGION', 'us-central1')

BUCKET = os.environ.get(
    'BUCKET', f'cdot-rtdh-{ENVIRONMENT}-wzdx-planned-events-raw')

QUERY_INTERVAL_MINUTES = os.environ.get('QUERY_INTERVAL_MINUTES', '30')

EXPERIMENTAL_TOPIC = os.environ.get(
    'TOPIC', 'wzdx-planned-events-experimental')

GEOTAB_AUTOMATED_ATTENUATOR_IDS = os.environ.get(
    'GEOTAB_AUTOMATED_ATTENUATOR_IDS', 'G9NSJ6703F6J;G90N60BYJT18')