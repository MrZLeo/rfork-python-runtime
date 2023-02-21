#!/bin/bash
BUNDLE_PATH=~/.base/baseline

pushd .
cd ../baseline-image
docker build -t mrzleo/baseline-image .
sudo rm -rf $BUNDLE_PATH/rootfs
sudo mkdir -p $BUNDLE_PATH/rootfs
popd
if [[ ! -f "$BUNDLE_PATH/config-base.json" ]]; then
    echo "Cannot find config.json. Paste a new one"
    sudo cp configs/baseline/config.json $BUNDLE_PATH/config-base.json
    sudo cp configs/baseline/config-loop.json $BUNDLE_PATH
fi
sudo docker export `docker create baseline-image` | sudo tar -C $BUNDLE_PATH/rootfs -xf -
