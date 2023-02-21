#!/bin/bash
source ./config
sudo $RUNC delete -f app-test
sudo $RUNC delete -f python-test

## FIXME: try 100 times to delete runc containers
#for i in {1..1000}
#do
#	sudo runc delete -f $(sudo runc list -q | head -n 1)
#done
