#!/bin/bash

touch .lock

while [ -f ".lock" ]
do
go.py Run2018A.conf -G 
echo "rm .lock"
sleep 2
done
