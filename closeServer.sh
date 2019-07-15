#!/bin/bash
pids=`ps -ef | grep 'manage.py runserver' | grep -v "grep" | awk '{print $2}'`;
parentPids=`ps -ef | grep 'manage.py runserver' | grep -v "grep" | awk '{print $3}'`;
echo "${pids}";
echo "${parentPids}";
kill -9 ${pids};
kill -9 ${parentPids};
