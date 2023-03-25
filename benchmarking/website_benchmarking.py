from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from collections import defaultdict

iterations_per_webpage = 5
website = "http://google.com"
timings = defaultdict(list)

def perfMeasure(driver, website):
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
  # 7. 
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
  
  print("Back End: %s ms" % backendPerformance_calc)
  print("Front End: %s ms" % frontendPerformance_calc)
  print("Tcp Handshake: %s ms" % (connectEnd - connectStart))
  print("response time: %s ms" % (responseEnd - requestStart))
  print("Time to fetch: %s ms" % (responseEnd - fetchStart))
  # print("Navigantion Start: %s ms" % navigationStart)
  # print("Redirect Start: %s ms" % redirectStart)
  timings[0].append(redirectStart - navigationStart)
  timings[1].append(redirectEnd - redirectStart)
  timings[2].append(fetchStart -  redirectEnd)
  timings[3].append(domainLookupStart - fetchStart)
  timings[4].append(domainLookupEnd - domainLookupStart)
  timings[5].append(connectStart - domainLookupEnd)
  timings[6].append(secureConnectionStart - connectStart)
  timings[7].append(connectEnd - secureConnectionStart)
  # Time diff in sending a request after establishing connection
  timings[8].append(requestStart - connectEnd)
  timings[9].append(responseStart - requestStart)
  timings[10].append(responseEnd - responseStart)
  timings[11].append(fetchStart - navigationStart)
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

def initialiseWebDriver():
  # chrome_options = webdriver.ChromeOptions()
  # chrome_options.add_argument("--incognito")
  # driver =  webdriver.Chrome(chrome_options=chrome_options)
  driver =  webdriver.Chrome()
  return driver

def calculatePerfWebsite(website):
  driver = initialiseWebDriver()
  for i in range(iterations_per_webpage):
    perfMeasure(driver, website)
  driver.quit()
  printTimingsDebug()

def printTimingsDebug():
  print("Diffs")
  for i in range(len(timings)):
    st = str(i) + " "
    for j in timings[i]:
      st = st + str(j) + " "
    print(st)

calculatePerfWebsite(website)

