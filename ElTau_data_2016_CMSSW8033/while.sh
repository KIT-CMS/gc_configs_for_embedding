#!/bin/bash

touch .lock

while [ -f ".lock" ]
do
go.py Run2016B-v2.conf -Gc -m 4
echo "rm .lock"
sleep 2
done
