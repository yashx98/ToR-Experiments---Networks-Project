from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from collections import defaultdict
from prettytable import PrettyTable
import statistics
import subprocess
import os
import time
import signal
from stem import Signal, CircStatus
from stem.control import Controller, EventType
import matplotlib.pyplot as plt

# benchmarking/075-basic-website-performance-testing-backendperformance.png
# contains the different phases of a request
# navigationStart -> redirectStart -> redirectEnd -> fetchStart ->
# domainLookupStart -> domainLookupEnd -> connectStart ->
# secureConnectionStart -> connectEnd -> requestStart -> responseStart ->
# responseEnd
# More details at: https://www.go-euc.com/basic-website-performance-testing/
# Some observations:
# 1. redirect period doesn't get triggered
# 2. the diff b/w fetchStart and navigationStart becomes negligible after
# first website load
# 3. The diff b/w domainLookupStart and fetchStart i.e. the App Cache period
# becomes negligible after the first website load
# 4. The DNS lookup period becomes 0 after the first load(sometimes 0 even on
# the first website load)
# 5. There is negligible time difference b/w domainLookupEnd and connectStart
# 6. secureConnection seems to be needed to be established once and 0 time
# required to establish secure connection.

# benchmarking/popular_websites.txt contains the list of the top 50 popular
# websites(excluding adult websites).

ITERATIONS_PER_WEBPAGE = 100
website = "http://google.com"
timings = defaultdict(list)
WEBSITES_FILE_NAME = "popular_websites.txt"
HTTP_STR = "http://"
HTTPS_STR = "https://"
INDEX_NAME = "Index No."
BACKEND_PERF_NAME_CONST = "Backend Time(ms)"
BACKEND_PERF_CONST = "Backend"
FRONTEND_PERF_NAME_CONST = "Frontend Time(ms)"
FRONTEND_PERF_CONST = "Frontend"
TCP_HANDSHAKE_PERF_NAME_CONST = "TCP Handshake Time(ms)"
TCP_HANDSHAKE_PERF_CONST = "tcp_handshake"
RESPONSE_PERF_NAME_CONST = "Server Response Time(ms)"
RESPONSE_PERF_CONST = "Response"
STAT_NAME_STR = "Stat Name"
MEAN_STR = "Mean"
MEADIAN_STR = "Median"
STD_DEV_STR = "Standard Deviation"
COF_VAR_STR = "Coefficient of Variation"
DATA_DOWNLOADED_STR = "data_downloaded"
MAX_NUM_HOPS = 10
SOCKS_PORT = 9200
CONTROL_PORT = 9201

def perfMeasure(driver, website):
  driver.get(website)
  # TODO(Yash) This is deprecated. Update with the new api.
  navigationStart = driver.execute_script("return window.performance.timing.navigationStart")
  redirectStart = driver.execute_script("return window.performance.timing.redirectStart")
  redirectEnd = driver.execute_script("return window.performance.timing.redirectEnd")
  fetchStart = driver.execute_script("return window.performance.timing.fetchStart")
  domainLookupStart = driver.execute_script("return window.performance.timing.domainLookupStart")
  domainLookupEnd = driver.execute_script("return window.performance.timing.domainLookupEnd")
  connectStart = driver.execute_script("return window.performance.timing.connectStart")
  secureConnectionStart = driver.execute_script("return window.performance.timing.secureConnectionStart")
  connectEnd = driver.execute_script("return window.performance.timing.connectEnd")
  requestStart = driver.execute_script("return window.performance.timing.requestStart")
  responseStart = driver.execute_script("return window.performance.timing.responseStart")
  responseEnd = driver.execute_script("return window.performance.timing.responseEnd")
  domComplete = driver.execute_script("return window.performance.timing.domComplete")
  # domComplete = driver.execute_script("return window.performance.navigation.domComplete")
  # unloadEventEnd = driver.execute_script("return window.performance.timing.unloadEventEnd")

  backendPerformance_calc = responseStart - navigationStart
  frontendPerformance_calc = domComplete - responseStart
  response_diff = responseEnd - requestStart
  
  # print(website)
  # print("Back End: %s ms" % backendPerformance_calc)
  # print("Front End: %s ms" % frontendPerformance_calc)
  # print("Tcp Handshake: %s ms" % (connectEnd - connectStart))
  # print("response time: %s ms" % (responseEnd - requestStart))
  # network_data = driver.execute_script('return window.performance.getEntries();')
  # total_data_size = sum(entry['transferSize'] for entry in network_data if entry['transferSize'] > 0)
  size_in_bytes = driver.execute_script("return window.performance.getEntries().reduce((total, entry) => total + entry.transferSize, 0)")
  perfDict = {}
  perfDict[BACKEND_PERF_CONST] = backendPerformance_calc
  perfDict[FRONTEND_PERF_CONST] = frontendPerformance_calc
  perfDict[TCP_HANDSHAKE_PERF_CONST] = (connectEnd - connectStart)
  perfDict[RESPONSE_PERF_CONST] = (responseEnd - requestStart)
  # perfDict[DATA_DOWNLOADED_STR] = size_in_bytes
  # print("Data down %s" % size_in_bytes)
  return perfDict
  # print("Time to fetch: %s ms" % (responseEnd - fetchStart))
  # print("Navigantion Start: %s ms" % navigationStart)
  # print("Redirect Start: %s ms" % redirectStart)
  # timings[0].append(redirectStart - navigationStart)
  # timings[1].append(redirectEnd - redirectStart)
  # timings[2].append(fetchStart -  redirectEnd)
  # timings[3].append(domainLookupStart - fetchStart)
  # timings[4].append(domainLookupEnd - domainLookupStart)
  # timings[5].append(connectStart - domainLookupEnd)
  # timings[6].append(secureConnectionStart - connectStart)
  # timings[7].append(connectEnd - secureConnectionStart)
  # # Time diff in sending a request after establishing connection
  # timings[8].append(requestStart - connectEnd)
  # timings[9].append(responseStart - requestStart)
  # timings[10].append(responseEnd - responseStart)
  # timings[11].append(fetchStart - navigationStart)
  # timings[12].append(fetchStart - unloadEventEnd)
  # print("Different Phases output:")
  # print("B/w navStart redirectStart %s ms" % (redirectStart - navigationStart))
  # print("B/w redirectStart redirectEnd %s ms" % (redirectEnd - redirectStart))
  # print("B/w redirectEnd fetchStart %s ms" % (fetchStart -  redirectEnd))
  # print("B/w fetchStart domainLookupStart %s ms" % (domainLookupStart - fetchStart))
  # print("B/w domainLookupStart domainLookupEnd %s ms" % (domainLookupEnd - domainLookupStart))
  # print("B/w domainLookupEnd connectStart %s ms" % (connectStart - domainLookupEnd))
  # print("B/w connectStart secureConnectionStart %s ms" % (secureConnectionStart - connectStart))
  # print("B/w secureConnectionStart connectEnd %s ms" % (connectEnd - secureConnectionStart))
  # print("B/w connectEnd requestStart %s ms" % (requestStart - connectEnd))
  # print("B/w requestStart responseStart %s ms" % (responseStart - requestStart))
  # print("B/w responseStart responseEnd %s ms" % (responseEnd - responseStart))

def perfMeasureUpdated(driver, website):
  driver.get(website)

def initialiseWebDriver():
  # chrome_options = webdriver.ChromeOptions()
  # chrome_options.add_argument("--incognito")
  # driver =  webdriver.Chrome(chrome_options=chrome_options)
  # driver =  webdriver.Chrome()
  options = webdriver.ChromeOptions()
  options.add_argument('--headless')
  driver = webdriver.Chrome(chrome_options=options)
  return driver

def initialiseTorWebDriver():
  PROXY = "socks5://localhost:" + str(SOCKS_PORT) # IP:PORT or HOST:PORT
  options = webdriver.ChromeOptions()
  options.add_argument('--proxy-server=%s' % PROXY)
  options.add_argument('--headless')
  driver = webdriver.Chrome(chrome_options=options)
  return driver

def getWebDriver(use_tor):
  if use_tor:
    return initialiseTorWebDriver()
  else:
    return initialiseWebDriver()

def calculatePerfWebsite(website, use_tor = False):
  driver = getWebDriver(use_tor)
  print(website)
  table = PrettyTable()
  table.field_names = [INDEX_NAME, BACKEND_PERF_NAME_CONST,
                       FRONTEND_PERF_NAME_CONST, TCP_HANDSHAKE_PERF_NAME_CONST,
                       RESPONSE_PERF_NAME_CONST]
  # TODO(Yash): Add stats stat for the measurements
  stats_table = PrettyTable()
  stats_table.field_names = [STAT_NAME_STR, BACKEND_PERF_NAME_CONST,
                             FRONTEND_PERF_NAME_CONST,
                             TCP_HANDSHAKE_PERF_NAME_CONST,
                             RESPONSE_PERF_NAME_CONST]
  # stats_table.field_names = [STAT_NAME_STR, MEAN_STR]
  allStatsArr = []
  columnsArr = [BACKEND_PERF_CONST, FRONTEND_PERF_CONST,
                TCP_HANDSHAKE_PERF_CONST, RESPONSE_PERF_CONST]
  for i in range(ITERATIONS_PER_WEBPAGE):
    perfDict = perfMeasure(driver, website)
    table.add_row([i, perfDict[BACKEND_PERF_CONST],
                   perfDict[FRONTEND_PERF_CONST],
                   perfDict[TCP_HANDSHAKE_PERF_CONST],
                   perfDict[RESPONSE_PERF_CONST]])
    allStatsArr.append(perfDict)
  driver.quit()
  stats_dict = defaultdict(list)
  for perfDict in allStatsArr:
    for col in columnsArr:
      if perfDict[col] >= 0:
        stats_dict[col].append(perfDict[col])
  mean_row = []
  mean_row.append(MEAN_STR)
  std_dev_row = []
  std_dev_row.append(STD_DEV_STR)
  median_row = []
  median_row.append(MEADIAN_STR)
  cof_var_row = []
  cof_var_row.append(COF_VAR_STR)
  website_stats_dict = {}
  for col in columnsArr:
    mean = statistics.mean(stats_dict[col])
    std_dev = statistics.stdev(stats_dict[col])
    mean_row.append(mean)
    median = statistics.median(stats_dict[col])
    median_row.append(median)
    std_dev_row.append(std_dev)
    collected_stats_dict = {}
    collected_stats_dict[MEAN_STR] = mean
    collected_stats_dict[MEADIAN_STR] = median
    collected_stats_dict[STD_DEV_STR] = std_dev
    if mean == 0:
      cof_var_row.append(0)
      collected_stats_dict[COF_VAR_STR] = 0
    else:
      cof_var_row.append(std_dev * 100 / mean)
      collected_stats_dict[COF_VAR_STR] = std_dev * 100 / mean
    website_stats_dict[col] = collected_stats_dict
  stats_table.add_row(mean_row)
  stats_table.add_row(median_row)
  stats_table.add_row(std_dev_row)
  stats_table.add_row(cof_var_row)
  print(table)
  print(stats_table)
  return website_stats_dict

def perfOutput(perfDict):
  out_str = ""
  # 
  return out_str

def printTimingsDebug():
  print("Diffs")
  for i in range(len(timings)):
    st = str(i) + " "
    for j in timings[i]:
      st = st + str(j) + " "
    print(st)

def readPopularWebsites():
  with open(WEBSITES_FILE_NAME, 'r') as f:
    websites_list = f.readlines()
  f.close()
  return websites_list

def sanitizeWebsitesList(websites_list):
  websites_list_sanitized = []
  for website in websites_list:
    if website[0] == '#':
      continue
    if website[0] == '@':
      websites_list_sanitized.append(HTTPS_STR + website[1:])
      continue
    websites_list_sanitized.append(HTTP_STR + website)
  return websites_list_sanitized

def remakeTorWithChangedHops(num_hops):
  cmd_str = "sed -i '902s/.*/#define DEFAULT_ROUTE_LEN "+ str(num_hops) +"/' src/core/or/or.h"
  subprocess.run(cmd_str, cwd="/users/ys5608/code/tor/", shell=True)
  print("Uninstalling tor")
  subprocess.run("sudo make uninstall", cwd="/users/ys5608/code/tor/", shell=True)
  print("Reinstalling tor with " + str(num_hops) + " hops.")
  subprocess.run("sudo make install", cwd="/users/ys5608/code/tor/", shell=True)
  print("Starting tor with hops=" + str(num_hops))
  tor_process = subprocess.Popen("exec tor --controlport 9201", cwd="/users/ys5608/code/tor/", shell=True)
  time.sleep(30)
  return tor_process

def listCircuits():
  with Controller.from_port(port = CONTROL_PORT) as controller:
    controller.authenticate()

    for circ in sorted(controller.get_circuits()):
      if circ.status != CircStatus.BUILT:
        continue

      print("")
      print("Circuit %s (%s)" % (circ.id, circ.purpose))

      for i, entry in enumerate(circ.path):
        div = '+' if (i == len(circ.path) - 1) else '|'
        fingerprint, nickname = entry

        desc = controller.get_network_status(fingerprint, None)
        address = desc.address if desc else 'unknown'

        print(" %s- %s (%s, %s)" % (div, fingerprint, nickname, address))

def main():
  websites_list = readPopularWebsites()
  websites_list = sanitizeWebsitesList(websites_list)
  websites_stats_list = []
  for i in range(1, MAX_NUM_HOPS + 1):
    tor_process = None
    websites_stats_list.append([])
    if i != 1:
      tor_process = remakeTorWithChangedHops(i)
      listCircuits()
    for website in websites_list:
      if i == 1:
        website_stats = calculatePerfWebsite(website)
        websites_stats_list[i-1].append(website_stats)
        continue
      website_stats = calculatePerfWebsite(website, True)
      websites_stats_list[i-1].append(website_stats)
    if i != 1:
      tor_process.send_signal(signal.SIGINT)
  # Process and plot the collected websites stats
  percent_increases = []
  columnsArr = [BACKEND_PERF_CONST, FRONTEND_PERF_CONST, RESPONSE_PERF_CONST]
  stats_arr = [MEAN_STR, MEADIAN_STR]
  for i in range(len(websites_list)):
    percent_increases.append({})
    for col in columnsArr:
      percent_increases[i][col] = {}
      for stat in stats_arr:
        percent_increases[i][col][stat] = []
  for i in range(len(websites_list)):
    base = websites_stats_list[0][i]
    for num_hops in range(1, MAX_NUM_HOPS):
      next = websites_stats_list[num_hops][i]
      for col in columnsArr:
        for stat in stats_arr:
          inc_percent = (next[col][stat] - base[col][stat]) * 100 / base[col][stat]
          percent_increases[i][col][stat].append(inc_percent)
      # base = next
  x_axis = [0]
  for i in range(2, MAX_NUM_HOPS + 1):
    x_axis.append(i)
  proc_percent_increases = {}
  for col in columnsArr:
    proc_percent_increases[col] = {}
    fig, ax = plt.subplots()
    for stat in stats_arr:
      proc_percent_increases[col][stat] = [0]
      for i in range(len(percent_increases[0][col][stat])):
        sum = 0
        for j in range(len(percent_increases)):
          sum += percent_increases[j][col][stat][i]
        avg = sum / len(percent_increases)
        proc_percent_increases[col][stat].append(avg)
      ax.plot(x_axis, proc_percent_increases[col][stat], marker='o', markersize=4, label=stat + ' ' + col + ' Time')
    ax.set_ylabel('Time Increase %')
    ax.set_xlabel('Circuit Length')
    ax.set_title('Website ' + col + ' Times')
    ax.legend()
    plt.savefig(col + 'Time.png')


if __name__ == "__main__":
  main()
  # listCircuits()
  # driver = getWebDriver(True)