import os
import re
import sys
import time
TEST_TIMES = 10
TEST_INVOKETIME_PATTERN = {"baseline": "start run container", "fork": "start fork"}
USAGE="python3 test_baseline.py [test], test can be \"baseline\" or \"fork\"\nIf no test is specified, it runs all tests by default"

def test_fork_start():
    latencies = []
    ENDPOINT_BUNDLE="%s/.base/spin0/rootfs" %os.environ['HOME']
    print(ENDPOINT_BUNDLE)
    COMMAND_FORK = "./run_fork.sh"

    for i in range(TEST_TIMES):
        exec_ = os.popen(COMMAND_FORK)
        output_lines = exec_.read().strip().split('\n') # only contains parent output

        # Wait for the child to write the timestamp into the log
        time.sleep(0.05)

        output_line_child = open(ENDPOINT_BUNDLE + "/log.txt", "r").read()
        output_lines.append(output_line_child)
        # print(output_lines)
        invokeTime, startTime = parse_output_lines(output_lines, "fork")
        # print(invokeTime, startTime)
        start_latency = startTime - invokeTime
        latencies.append(start_latency)
    format_result(latencies, "fork")
    # print(latencies)

# pre-requisite: finish the building of the baseline container bundle, i.e., ~/.base/baseline/rootfs and ~/.base/baseline/config.json
def test_baseline_start():
    # PWD must be in scripts/tests
    latencies = []
    COMMAND_RUN = "./run_baseline.sh"

    for i in range(TEST_TIMES):
        exec_ = os.popen(COMMAND_RUN)
        output_lines = exec_.read().strip().split('\n')
        # print(output_lines)
        invokeTime, startTime = parse_output_lines(output_lines, "baseline")
        start_latency = startTime - invokeTime
        latencies.append(start_latency)
    format_result(latencies, "baseline")
    # print(latencies)


def parse_output_lines(output_lines, test):
    # print(test)
    invokeTime_pattern_line = TEST_INVOKETIME_PATTERN[test]
    startTime_pattern_line = "\'startTime\': 1[0-9]{12}"
    time_pattern = "1[0-9]{12}"

    # Find lines that contains the invokeTime and the startTime
    invokeTime_line = None
    startTime_line = None
    for line in output_lines:
        invokeTime_match = re.search(invokeTime_pattern_line, line)
        if invokeTime_match != None:
            # print(line)
            invokeTime_line = line
            continue

        startTime_match = re.search(startTime_pattern_line, line)
        if startTime_match != None:
            # print(line)
            startTime_line = line

    if startTime_line == None or invokeTime_line == None:
        print("error output: can't find the startTime or invokeTime")
        exit()
    # Find the time value in the lines
    invokeTime_search = re.search(time_pattern, invokeTime_line)
    startTime_search = re.search(startTime_pattern_line, startTime_line)

    invokeTime = invokeTime_line[invokeTime_search.span()[0]: invokeTime_search.span()[0] + 13]
    startTime = startTime_line[startTime_search.span()[1] - 13 : startTime_search.span()[1]]

    return int(invokeTime), int(startTime)

def format_result(latencies, test):
    request_num = len(latencies)
    print("=============== %s result ===============" %test)
    latencies.sort()
    latency_sum = 0
    for latency in latencies:
        latency_sum += latency
    averageLatency = latency_sum / request_num
    _50pcLatency = latencies[int(request_num * 0.5) - 1]
    _75pcLatency = latencies[int(request_num * 0.75) - 1]
    _90pcLatency = latencies[int(request_num * 0.9) - 1]
    _95pcLatency = latencies[int(request_num * 0.95) - 1]
    _99pcLatency = latencies[int(request_num * 0.99) - 1]
    print("latency (ms):\navg\t50%\t75%\t90%\t95%\t99%")
    print("%.2f\t%d\t%d\t%d\t%d\t%d" %(averageLatency,_50pcLatency,_75pcLatency,_90pcLatency,_95pcLatency,_99pcLatency))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == "fork":
            test_fork_start()
        elif sys.argv[1] == "baseline":
            test_baseline_start()
        else:
            print(USAGE)
    else:
        test_fork_start()
        test_baseline_start()
