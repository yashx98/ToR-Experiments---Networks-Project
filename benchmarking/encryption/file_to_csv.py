import csv

FILE_PATH = "LOGS"
WRITE_FILE_NAME = "websites_3h.csv"
ENCRYPTS, INBUF = "Encrypt", "Inbuf"

def writeData(data):
    with open(WRITE_FILE_NAME, "w", newline="") as file:
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
    for line in read_file(filePath):
        if line.startswith(ENCRYPTS):
            # print("ENC: " + line)
            encTime = max(float(line.split(":")[1].strip()), encTime)
        elif line.startswith(INBUF):
            # print("INB: " + line + ", " + encTime)
            inbufTime = float(line.split(":")[1].strip())
            if encTime != 0:
                ratio = round(float((inbufTime / encTime)), 2)
                if ratio > 10:
                    encTime = 0
                    continue
                data.append([encTime, inbufTime, (inbufTime / encTime)])
                encTime = 0
    writeData(data)

def main():
    processFile(FILE_PATH)

if __name__ == "__main__":
  main()