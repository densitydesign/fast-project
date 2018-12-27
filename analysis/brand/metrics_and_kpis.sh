#!/bin/bash

PYTHON="python"
SCRIPT_FOLDER="./"

LOG_FOLDER="./logs/"

# User-Activity
${PYTHON} "${SCRIPT_FOLDER}/enrich_with_user_activity.py" --log-conf "../confs/logging.yaml" --batch-size 1000 > "${LOG_FOLDER}/user_activity.out" 2> "${LOG_FOLDER}/user_activity.err"

# Brand Daily Metrics
${PYTHON} "${SCRIPT_FOLDER}/metrics.py" --log-conf "../confs/logging.yaml" --batch-size 1000 > "${LOG_FOLDER}/metrics.out" 2> "${LOG_FOLDER}/metrics.err"

# Community Daily Metrics
${PYTHON} "${SCRIPT_FOLDER}/metrics_communities.py" --log-conf "../confs/logging.yaml" --start "2017-02-01" --end "2017-03-01" > "${LOG_FOLDER}/metrics_community.out.20170201" 2> "${LOG_FOLDER}/metrics_community.err.20170201"
${PYTHON} "${SCRIPT_FOLDER}/metrics_communities.py" --log-conf "../confs/logging.yaml" --start "2017-01-01" --end "2017-02-01" > "${LOG_FOLDER}/metrics_community.out.20170101" 2> "${LOG_FOLDER}/metrics_community.err.20170101"
${PYTHON} "${SCRIPT_FOLDER}/metrics_communities.py" --log-conf "../confs/logging.yaml" --start "2017-03-01" --end "2017-04-01" > "${LOG_FOLDER}/metrics_community.out.20170301" 2> "${LOG_FOLDER}/metrics_community.err.20170301"
${PYTHON} "${SCRIPT_FOLDER}/metrics_communities.py" --log-conf "../confs/logging.yaml" --start "2017-04-01" --end "2017-05-01" > "${LOG_FOLDER}/metrics_community.out.20170401" 2> "${LOG_FOLDER}/metrics_community.err.20170401"
${PYTHON} "${SCRIPT_FOLDER}/metrics_communities.py" --log-conf "../confs/logging.yaml" --start "2017-05-01" --end "2017-06-01" > "${LOG_FOLDER}/metrics_community.out.20170501" 2> "${LOG_FOLDER}/metrics_community.err.20170501"
${PYTHON} "${SCRIPT_FOLDER}/metrics_communities.py" --log-conf "../confs/logging.yaml" --start "2017-06-01" --end "2017-07-01" > "${LOG_FOLDER}/metrics_community.out.20170601" 2> "${LOG_FOLDER}/metrics_community.err.20170601"
${PYTHON} "${SCRIPT_FOLDER}/metrics_communities.py" --log-conf "../confs/logging.yaml" --start "2017-07-01" --end "2017-08-01" > "${LOG_FOLDER}/metrics_community.out.20170701" 2> "${LOG_FOLDER}/metrics_community.err.20170701"
${PYTHON} "${SCRIPT_FOLDER}/metrics_communities.py" --log-conf "../confs/logging.yaml" --start "2017-08-01" --end "2017-09-01" > "${LOG_FOLDER}/metrics_community.out.20170801" 2> "${LOG_FOLDER}/metrics_community.err.20170801"
${PYTHON} "${SCRIPT_FOLDER}/metrics_communities.py" --log-conf "../confs/logging.yaml" --start "2017-09-01" --end "2017-10-01" > "${LOG_FOLDER}/metrics_community.out.20170901" 2> "${LOG_FOLDER}/metrics_community.err.20170901"
${PYTHON} "${SCRIPT_FOLDER}/metrics_communities.py" --log-conf "../confs/logging.yaml" --start "2017-10-01" --end "2017-11-01" > "${LOG_FOLDER}/metrics_community.out.20171001" 2> "${LOG_FOLDER}/metrics_community.err.20171001"
${PYTHON} "${SCRIPT_FOLDER}/metrics_communities.py" --log-conf "../confs/logging.yaml" --start "2017-11-01" --end "2017-12-01" > "${LOG_FOLDER}/metrics_community.out.20171101" 2> "${LOG_FOLDER}/metrics_community.err.20171101"
${PYTHON} "${SCRIPT_FOLDER}/metrics_communities.py" --log-conf "../confs/logging.yaml" --start "2017-12-01" --end "2018-01-01" > "${LOG_FOLDER}/metrics_community.out.20171201" 2> "${LOG_FOLDER}/metrics_community.err.20171201"

