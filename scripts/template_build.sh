#!/bin/bash
BUNDLE_PATH=~/.base/container0

pushd .
cd ../python-base-image
docker build -t mrzleo/python-base-image .
sudo rm -rf $BUNDLE_PATH/rootfs
sudo mkdir -p $BUNDLE_PATH/rootfs
popd
if [[ ! -f "$BUNDLE_PATH/config-base.json" ]]; then
    echo "Cannot find config.json. Paste a new one"
    sudo cp configs/container0/config.json $BUNDLE_PATH/config-base.json
    sudo cp configs/container0/config-loop.json $BUNDLE_PATH/config-loop.json
fi
sudo docker export `docker create python-base-image` | sudo tar -C $BUNDLE_PATH/rootfs -xf -
