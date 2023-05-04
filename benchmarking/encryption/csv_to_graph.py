import numpy as np
import matplotlib.pyplot as plt
import csv

CSV_FILE = "websites_3h.csv"
FIG_FILE = "websites_3h.png"

def readCSVFile():
    column_3_values = []
    with open(CSV_FILE, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for row in csv_reader:
            column_3_values.append(round(float(row[2]), 2))
    return column_3_values

def generateCDF():
    data = readCSVFile()
    N = len(data)
    
    # sort the data in ascending order
    x = np.sort(data)
    
    # get the cdf values of y
    y = np.arange(N)/float(len(x))
    
    # plotting
    plt.xlabel('Total Time / Encryption Time')
    plt.ylabel('CDF')
    
    plt.title('CDF for Total Time / Encryption Time')
    
    plt.plot(x, y)
    plt.savefig(FIG_FILE)
    plt.show()
    # plt.savefig('websites_5h.png')

generateCDF()