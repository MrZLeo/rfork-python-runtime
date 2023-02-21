set RUNC ~/runc/runc
set -l RUNNING_CONTAINER $(math $(sudo $RUNC list | wc -l) - 1)
if test $RUNNING_CONTAINER -eq 0
    cd ~/.base/container0
    sudo cp config-base.json config.json
    sudo $RUNC run -d python-test
    echo "run python-test complete"
    cd ~/.base/spin0
    sudo $RUNC run -d app-test
    echo "run app-test complete"
    echo "ready to fork..."
    sleep 1s # wait for containers to complete startup
else
    sudo $RUNC fork2container --zygote python-test --target app-test
end
