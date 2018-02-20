#!/bin/bash
sleep 10 # make sure db starts
coverage run --branch --source=. ./manage.py test
coverage report
coverage xml
python-codacy-coverage -r coverage.xml
