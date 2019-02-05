#!/bin/bash

PYTHON="python"
SCRIPT_FOLDER="./"

LOG_FOLDER="./logs/"

# Time Fields Enrichment
${PYTHON} "${SCRIPT_FOLDER}/enrich_time_fields.py"   --log-conf "../confs/logging.yaml" --batch-size 1000 > "${LOG_FOLDER}/enrich_time.out" 2> "${LOG_FOLDER}/enrich_time.err"

# Hashtags and Mentions Enrichment
${PYTHON} "${SCRIPT_FOLDER}/enrich_with_hashtags.py" --log-conf "../confs/logging.yaml" --batch-size 1000 > "${LOG_FOLDER}/enrich_hashtags.out" 2> "${LOG_FOLDER}/enrich_hashtags.err"
