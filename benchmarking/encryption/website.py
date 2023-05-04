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

ITERATIONS_PER_WEBPAGE = 10
website = "http://google.com"
timings = defaultdict(list)
WEBSITES_FILE_NAME = "../popular_websites.txt"
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
MAX_NUM_HOPS = 3
SOCKS_PORT = 9050
CONTROL_PORT = 9201

def perfMeasure(driver, website):
  driver.get(website)
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

  backendPerformance_calc = responseStart - navigationStart
  frontendPerformance_calc = domComplete - responseStart
  response_diff = responseEnd - requestStart
  
  size_in_bytes = driver.execute_script("return window.performance.getEntries().reduce((total, entry) => total + entry.transferSize, 0)")
  perfDict = {}
  perfDict[BACKEND_PERF_CONST] = backendPerformance_calc
  perfDict[FRONTEND_PERF_CONST] = frontendPerformance_calc
  perfDict[TCP_HANDSHAKE_PERF_CONST] = (connectEnd - connectStart)
  perfDict[RESPONSE_PERF_CONST] = (responseEnd - requestStart)
  return perfDict

def perfMeasureUpdated(driver, website):
  driver.get(website)

def initialiseTorWebDriver():
  PROXY = "socks5://localhost:" + str(SOCKS_PORT) # IP:PORT or HOST:PORT
  options = webdriver.ChromeOptions()
  options.add_argument('--proxy-server=' + PROXY)
  options.add_argument('--headless')
  driver = webdriver.Chrome(chrome_options=options)
  return driver

def getWebDriver():
  return initialiseTorWebDriver()

def calculatePerfWebsite(website):
  driver = getWebDriver()
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

def main():
  websites_list = readPopularWebsites()
  websites_list = sanitizeWebsitesList(websites_list)
  websites_stats_list = []
  for i in range(3, MAX_NUM_HOPS + 1):
    tor_process = None
    websites_stats_list.append([])
    for website in websites_list:
      website_stats = calculatePerfWebsite(website)
      websites_stats_list[i-3].append(website_stats)
    # if i != 1:
    #   tor_process.send_signal(signal.SIGINT)  


if __name__ == "__main__":
  main()
  # listCircuits()
  # driver = getWebDriver(True)