#!/bin/bash

touch .lock

while [ -f ".lock" ]
do
go.py Run2018A.conf -G 
go.py Run2018B.conf -G 
go.py Run2018C.conf -G 
go.py Run2018D.conf -G 
echo "rm .lock"
sleep 2
done
