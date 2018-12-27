#!/bin/bash

python metrics_communities.py --start "2017-01-01" --end "2017-02-01" > logs.out.20170101 2> logs.err.20170101
python metrics_communities.py --start "2017-02-01" --end "2017-03-01" > logs.out.20170201 2> logs.err.20170201
python metrics_communities.py --start "2017-03-01" --end "2017-04-01" > logs.out.20170301 2> logs.err.20170301
python metrics_communities.py --start "2017-04-01" --end "2017-05-01" > logs.out.20170401 2> logs.err.20170401
python metrics_communities.py --start "2017-05-01" --end "2017-06-01" > logs.out.20170501 2> logs.err.20170501
python metrics_communities.py --start "2017-06-01" --end "2017-07-01" > logs.out.20170601 2> logs.err.20170601
python metrics_communities.py --start "2017-07-01" --end "2017-08-01" > logs.out.20170701 2> logs.err.20170701
python metrics_communities.py --start "2017-08-01" --end "2017-09-01" > logs.out.20170801 2> logs.err.20170801
python metrics_communities.py --start "2017-09-01" --end "2017-10-01" > logs.out.20170901 2> logs.err.20170901
python metrics_communities.py --start "2017-10-01" --end "2017-11-01" > logs.out.20171001 2> logs.err.20171001
python metrics_communities.py --start "2017-11-01" --end "2017-12-01" > logs.out.20171101 2> logs.err.20171101
python metrics_communities.py --start "2017-12-01" --end "2018-01-01" > logs.out.20171201 2> logs.err.20171201

