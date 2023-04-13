from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from collections import defaultdict
from prettytable import PrettyTable
import statistics

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

ITERATIONS_PER_WEBPAGE = 2
website = "http://google.com"
timings = defaultdict(list)
WEBSITES_FILE_NAME = "popular_websites.txt"
HTTP_STR = "http://"
HTTPS_STR = "https://"
INDEX_NAME = "Index No."
BACKEND_PERF_NAME_CONST = "Backend Time(ms)"
BACKEND_PERF_CONST = "backend"
FRONTEND_PERF_NAME_CONST = "Frontend Time(ms)"
FRONTEND_PERF_CONST = "frontend"
TCP_HANDSHAKE_PERF_NAME_CONST = "TCP Handshake Time(ms)"
TCP_HANDSHAKE_PERF_CONST = "tcp_handshake"
RESPONSE_PERF_NAME_CONST = "Server Response Time(ms)"
RESPONSE_PERF_CONST = "response"
STAT_NAME_STR = "Stat Name"
MEAN_STR = "Mean"
MEADIAN_STR = "Median"
STD_DEV_STR = "Standard Deviation"
COF_VAR_STR = "Coefficient of Variation"
DATA_DOWNLOADED_STR = "data_downloaded"

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
  PROXY = "socks5://localhost:9050" # IP:PORT or HOST:PORT
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
  for col in columnsArr:
    mean = statistics.mean(stats_dict[col])
    std_dev = statistics.stdev(stats_dict[col])
    mean_row.append(mean)
    median_row.append(statistics.median(stats_dict[col]))
    std_dev_row.append(std_dev)
    if mean == 0:
      cof_var_row.append(0)
    else:
      cof_var_row.append(std_dev * 100 / mean)
  stats_table.add_row(mean_row)
  stats_table.add_row(median_row)
  stats_table.add_row(std_dev_row)
  stats_table.add_row(cof_var_row)
  print(table)
  print(stats_table)

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
  for website in websites_list:
    # calculatePerfWebsite(website)
    calculatePerfWebsite(website, True)

if __name__ == "__main__":
  main()
  # driver = getWebDriver(True)