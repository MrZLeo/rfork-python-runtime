#!/bin/bash

## Note(DD): This script is used for performance isolation test case!
## 	     Please carefully read the code before you run!
source ./config
BUNDLE_PATH=~/.base/iotensive
cd $BUNDLE_PATH
sudo cp config-perf-iso.json config.json

## A loop to continuously run I/O intensive tasks
for (( i=0; i<10000; i++ ))
do
	sudo $RUNC run $1
done
