#! /bin/bash
source ./config
RUNNING_CONTAINERS=`expr $(sudo $RUNC list | wc -l) - 1`
# if no container is running, run the template and the endpoint container
if (( $RUNNING_CONTAINERS == 0 )); then
    pushd .
    cd ~/.base/container0
    sudo cp config-base.json config.json
    sudo $RUNC run -d python-test
    echo "run python-test complete"
    cd ~/.base/spin0
    sudo $RUNC run -d app-test
    echo "run app-test complete"
    echo "ready to fork..."
    popd
    sleep 1s # wait for containers to complete startup
else
    sudo $RUNC fork2container --zygote python-test --target app-test
fi
