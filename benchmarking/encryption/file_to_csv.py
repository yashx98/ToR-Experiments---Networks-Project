import csv

MAX_COUNT = 2
FILE_PATH = "./Logs/LOGS_" + str(MAX_COUNT)
WRITE_FILE_NAME = "websites_" + str(MAX_COUNT) + "h.csv"
ENCRYPTS, INBUF = "Encrypt", "Inbuf"
THRESHOLD = 10

def writeData(data):
    with open('./csv/' + WRITE_FILE_NAME, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Encrypt Time (ms)", "Inbuf Time (ms)", "Ratio"])
        writer.writerows(data)

def read_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            yield line.strip()

def processFile(filePath):
    data = []
    encTime = 0
    count = 0
    for line in read_file(filePath):
        if line.startswith(ENCRYPTS):
            # print("ENC: " + line)
            if count < MAX_COUNT:
                encTime = encTime + float(line.split(":")[1].strip())
                count = count + 1
        elif line.startswith(INBUF):
            # print("INB: " + line + ", " + encTime)
            inbufTime = float(line.split(":")[1].strip())
            if encTime != 0:
                ratio = round(float((inbufTime / encTime)), 2)
                if ratio < 1 or ratio > THRESHOLD:
                    encTime = 0
                    count = 0
                    continue
                data.append([encTime, inbufTime, (inbufTime / encTime)])
                encTime = 0
                count  = 0
    writeData(data)

def main():
    processFile(FILE_PATH)

if __name__ == "__main__":
  main()