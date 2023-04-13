import matplotlib.pyplot as plt

OBSERVATIONS = 5
meanTime = [0.318, 0.536, 0.793, 1.044, 1.392]
medianTime = [0.301, 0.508, 0.767, 1.024, 1.404]
meanInc = [0.0]
medianInc = [0.0]
successRate = [99.009, 94.339, 86.206, 54.348, 43.668]
x = [2, 3, 4, 5, 6]

for i in range(1, OBSERVATIONS):
    meanInc.append((meanTime[i] - meanTime[0]) * 100 / meanTime[0])
    medianInc.append((medianTime[i] - medianTime[0]) * 100 / medianTime[0])

# Create 1st figure
fig, ax = plt.subplots()

ax.plot(x, meanTime, marker='o', markersize=4, label='Mean Build Time')
ax.plot(x, medianTime, marker='o', markersize=4, label='Median Build Time')
ax.set_ylabel('Time (ms)')
ax.set_xlabel('Circuit Length')
ax.set_title('Circuit Build Times')
ax.legend()
# plt.savefig('BuildTime.png')

# Create 2nd figure
plt.figure(2)

plt.plot(x, successRate, marker='o', markersize=6, label='Success Rates')
plt.ylabel('Success %')
plt.xlabel('Circuit Length')
plt.title('Circuit Build Success Rates %')
# plt.savefig('SuccessRate.png')

# Create 3rd figure
fig, ax = plt.subplots()

ax.plot(x, meanInc, marker='o', markersize=4, label='Increase % in Mean Time')
ax.plot(x, medianInc, marker='o', markersize=4, label='Increase % in Median Time')
ax.set_ylabel('Time Increase %')
ax.set_xlabel('Circuit Length')
ax.set_title('Increase in Circuit Build Times')
ax.legend()
# plt.savefig('BuildTimeIncrease.png')

plt.show()