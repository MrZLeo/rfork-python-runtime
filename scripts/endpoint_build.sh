#!/bin/bash
BUNDLE_PATH=~/.base/spin0

pushd .
cd ../spin-base-image
gcc spin.c -o spin -O2 -static && docker build -t mrzleo/spin-base-image .
sudo rm -rf $BUNDLE_PATH/rootfs
sudo mkdir -p $BUNDLE_PATH/rootfs
popd

if [[ ! -f "$BUNDLE_PATH/config.json" ]]; then
    echo "Cannot find config.json. Paste a new one"
    sudo cp configs/spin0/config.json $BUNDLE_PATH
fi
sudo docker export `docker create spin-base-image` | sudo tar -C $BUNDLE_PATH/rootfs -xf -
