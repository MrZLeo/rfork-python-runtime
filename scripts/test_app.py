import os
import re
import sys
import time
TEST_TIMES = 10
TEST_INVOKETIME_PATTERN = {"baseline": "start run container", "fork": "start fork"}
USAGE="python3 test_baseline.py [test], test can be \"baseline\" or \"fork\"\nIf no test is specified, it runs all tests by default"

def test_fork_start():
    latencies = []
    all_latencies = []
    e2e_latencies = []
    e2e_all_latencies = []
    warm_latencies = []
    ENDPOINT_BUNDLE="%s/.base/spin0/rootfs" %os.environ['HOME']
    COMMAND_FORK = "./run_fork.sh"
    #COMMAND_LOOP_RUN = "./run_baseline_loop.sh %d"

    for _ in range(TEST_TIMES):
        exec_ = os.popen(COMMAND_FORK)
        output_lines = exec_.read().strip().split('\n') # only contains parent output

        # Wait for the child to write the timestamp into the log
        time.sleep(15)

        output_line_child = open(ENDPOINT_BUNDLE + "/log.txt", "r").read()
        output_lines.append(output_line_child)
        # print(output_lines)
        invokeTime, startTime, retTime = parse_output_lines(output_lines, "fork")
        # print(invokeTime, startTime)
        start_latency = startTime - invokeTime
        e2e_latency = retTime - invokeTime # End2End latency
        warm_latency = retTime - startTime # End2End latency

        latencies.append(start_latency)
        warm_latencies.append(warm_latency)
        all_latencies.append(start_latency)
        e2e_latencies.append(e2e_latency)
        e2e_all_latencies.append(e2e_latency)

        #format_result(latencies, "fork-startup")
        #format_result(e2e_latencies, "fork-end2end")
        #format_result(warm_latencies, "warm-startup")
        #os.system(COMMAND_LOOP_RUN % i)
        #latencies = []
        #format_scale_result(all_latencies, "fork-startup")
        #e2e_latencies = []
        #format_scale_result(e2e_all_latencies, "fork-end2end")
    #print(latencies)
    print("")
    format_result(latencies, "fork-startup")
    format_result(e2e_latencies, "fork-end2end")
    #format_result(warm_latencies, "fork-warm")

# pre-requisite: finish the building of the baseline container bundle, i.e., ~/.base/baseline/rootfs and ~/.base/baseline/config.json
def test_baseline_start():
    # PWD must be in scripts/tests
    latencies = []
    all_latencies = []
    e2e_latencies = []
    e2e_all_latencies = []
    warm_latencies = []
    COMMAND_RUN = "./run_baseline.sh %d"

    for i in range(TEST_TIMES):
        exec_ = os.popen(COMMAND_RUN %i)
        output_lines = exec_.read().strip().split('\n')
        # print(output_lines)
        invokeTime, startTime, retTime = parse_output_lines(output_lines, "baseline")
        start_latency = startTime - invokeTime
        e2e_latency = retTime - invokeTime # End2End latency
        warm_latency = retTime - startTime # End2End latency

        latencies.append(start_latency)
        all_latencies.append(start_latency)

        e2e_latencies.append(e2e_latency)
        warm_latencies.append(warm_latency)
        e2e_all_latencies.append(e2e_latency)
        #format_result(latencies, "baseline-startup")
        #format_result(warm_latencies, "warm-startup")
        #format_result(e2e_latencies, "baseline-end2end")

        #format_scale_result(all_latencies, "baseline-startup")
        #format_scale_result(e2e_all_latencies, "baseline-end2end")
        #print(start_latency, e2e_latency)
    # print(latencies)
    print("")
    format_result(latencies, "baseline-startup")
    format_result(e2e_latencies, "baseline-end2end")
    #format_result(warm_latencies, "baseline-warm")


def parse_output_lines(output_lines, test):
    invokeTime_pattern_line = TEST_INVOKETIME_PATTERN[test]
    startTime_pattern_line = "\'startTime\': 1[0-9]{12}"
    retTime_pattern_line = "\'retTime\': 1[0-9]{12}"
    time_pattern = "1[0-9]{12}"

    # Find lines that contains the invokeTime and the startTime
    invokeTime_line = None
    startTime_line = None
    retTime_line = None
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

        retTime_match = re.search(retTime_pattern_line, line)
        if retTime_match != None:
            # print(line)
            retTime_line = line


    if startTime_line == None or invokeTime_line == None or retTime_line == None:
        print("error output: can't find the startTime or invokeTime")
        exit()
    # Find the time value in the lines
    invokeTime_search = re.search(time_pattern, invokeTime_line)
    startTime_search = re.search(startTime_pattern_line, startTime_line)
    retTime_search = re.search(retTime_pattern_line, retTime_line)

    invokeTime = invokeTime_line[invokeTime_search.span()[0]: invokeTime_search.span()[0] + 13]
    startTime = startTime_line[startTime_search.span()[1] - 13 : startTime_search.span()[1]]
    retTime = startTime_line[retTime_search.span()[1] - 13 : retTime_search.span()[1]]

    #print(startTime, retTime)

    return int(invokeTime), int(startTime), int(retTime)

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

def format_scale_result(latencies, test):
    request_num = len(latencies)
    print("=============== %s Scale result ===============" %test)
    latencies.sort()
    latency_sum = 0
    i = 0
    for latency in latencies:
        print("%d\t%d" % (i, latency))
        i += 1

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
