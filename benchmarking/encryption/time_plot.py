import numpy as np
import matplotlib.pyplot as plt
import csv

MAX_NUM_HOPS = 8
FIG_FILE = 'enctime_plot.png'

def getAvgEncTime(fileNumber):
    CSV_FILE = "websites_" + str(fileNumber) + "h.csv"
    encTime = 0.0
    count = 0
    with open('./csv/' + CSV_FILE, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for row in csv_reader:
            encTime = encTime + float(row[0])
            count = count + 1
    return (encTime / count)

def plotEncTimes():
    encTimes, hops = [], []
    for i in range(2, MAX_NUM_HOPS + 1):
        hops.append(i)
        encTimes.append(getAvgEncTime(i))
    
    # plotting
    plt.xlabel('Hops')
    plt.ylabel('Encryption Time (ms)')
    
    plt.title('Variation in Encryption time with Hops')
    
    plt.plot(hops, encTimes)
    plt.savefig('./charts/' + FIG_FILE)
    plt.show()

plotEncTimes()