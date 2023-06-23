import datetime
import os
import pyshark
import re
import sys
import time
import csv
import platform

# Given a regular expression, list the files that match it, and ask for user input
def selectFile(regex, subdirs = False):
	files = []
	if subdirs:
		for (dirpath, dirnames, filenames) in os.walk('.'):
			for file in filenames:
				path = os.path.join(dirpath, file)
				if path[:2] == '.\\': path = path[2:]
				if bool(re.match(regex, path)):
					files.append(path)
	else:
		for file in os.listdir(os.curdir):
			if os.path.isfile(file) and bool(re.match(regex, file)):
				files.append(file)
	
	print()
	if len(files) == 0:
		print(f'No files were found that match "{regex}"')
		print()
		return ''

	print('List of files:')
	for i, file in enumerate(files):
		print(f'  File {i + 1}  -  {file}')
	print()

	selection = None
	while selection is None:
		try:
			i = int(input(f'Please select a file (1 to {len(files)}): '))
		except KeyboardInterrupt:
			sys.exit()
		except:
			pass
		if i > 0 and i <= len(files):
			selection = files[i - 1]
	print()
	return selection

# Given a regular expression, list the directories that match it, and ask for user input
def selectDir(regex, subdirs = False):
	dirs = []
	if subdirs:
		for (dirpath, dirnames, filenames) in os.walk('.'):
			if dirpath[:2] == '.\\': dirpath = dirpath[2:]
			if bool(re.match(regex, dirpath)):
				dirs.append(dirpath)
	else:
		for obj in os.listdir(os.curdir):
			if os.path.isdir(obj) and bool(re.match(regex, obj)):
				dirs.append(obj)

	print()
	if len(dirs) == 0:
		print(f'No directories were found that match "{regex}"')
		print()
		return ''

	print('List of directories:')
	for i, directory in enumerate(dirs):
		print(f'  Directory {i + 1}  -  {directory}')
	print()

	selection = None
	while selection is None:
		try:
			i = int(input(f'Please select a directory (1 to {len(dirs)}): '))
		except KeyboardInterrupt:
			sys.exit()
		except:
			pass
		if i > 0 and i <= len(dirs):
			selection = dirs[i - 1]
	print()
	return selection

# List the files with a regular expression
def listFiles(regex, directory = ''):
	path = os.path.join(os.curdir, directory)
	return [os.path.join(path, file) for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)) and bool(re.match(regex, file))]

def header():
	line = 'Sample number,'
	line += 'Total handshake duration (s),'
	line += 'Total handshake packets,'
	line += 'Total handshake size (B),'
	line += 'Time MasterInformationBlock (s),'
	line += 'Time SIB1 (s),'
	line += 'Time SIB2 SIB3 (s),'
	line += 'Time RRCConnectionRequest (s),'
	line += 'Time RRCConnectionSetup (s),'
	line += 'Time RRCConnectionSetupComplete (s),'
	line += 'Size MasterInformationBlock (B),'
	line += 'Size SIB1 (B),'
	line += 'Size SIB2 SIB3 (B),'
	line += 'Size RRCConnectionRequest (B),'
	line += 'Size RRCConnectionSetup (B),'
	line += 'Size RRCConnectionSetupComplete (B),'
	return line

inputFilePath = selectFile('.*_processed\.csv', True)

outputFilePath = inputFilePath[:-4] + '_handshakes.csv'
outputFile = open(outputFilePath, 'w')
outputFile.write(header() + '\n')

inputFile = open(inputFilePath, 'r')
reader = csv.reader(inputFile)
tempHeader = next(reader)

currentSampleNumber = 0
totalHandshakeNumPackets = 0
totalHandshakeSize = 0
firstMIBTime = 0
firstMIBNumPacketsSum = 0
firstMIBSize = 0
firstMIBSizeSum = 0
lastSIB1Time = 0
lastSIB1Size = 0
lastSIBXTime = 0
lastSIBXSize = 0
lastConnectionRequestTime = 0
lastConnectionRequestSize = 0
lastConnectionSetupTime = 0
lastConnectionSetupSize = 0
lastConnectionCompleteTime = 0
lastConnectionCompleteNumPacketsSum = 0
lastConnectionCompleteSize = 0
lastConnectionCompleteSizeSum = 0
handshakeVoided = False

for row in reader:
	timestamp = float(row[1])
	sampleNum = int(row[3])
	size = int(row[5])
	info = row[7]
	if currentSampleNumber != sampleNum:
		if not handshakeVoided and currentSampleNumber > 0 and firstMIBTime > 0 and lastConnectionCompleteTime > 0:
			handshakeDuration = lastConnectionCompleteTime - firstMIBTime
			diffNumPackets = lastConnectionCompleteNumPacketsSum - firstMIBNumPacketsSum
			diffSize = lastConnectionCompleteSizeSum - firstMIBSizeSum
			print('Found handshake', currentSampleNumber, 'duration =', handshakeDuration)
			line = str(currentSampleNumber) + ','
			line += str(handshakeDuration) + ','
			line += str(diffNumPackets) + ','
			line += str(diffSize) + ','
			line += str(firstMIBTime - firstMIBTime) + ','
			line += str(lastSIB1Time - firstMIBTime) + ','
			line += str(lastSIBXTime - firstMIBTime) + ','
			line += str(lastConnectionRequestTime - firstMIBTime) + ','
			line += str(lastConnectionSetupTime - firstMIBTime) + ','
			line += str(lastConnectionCompleteTime - firstMIBTime) + ','
			line += str(firstMIBSize) + ','
			line += str(lastSIB1Size) + ','
			line += str(lastSIBXSize) + ','
			line += str(lastConnectionRequestSize) + ','
			line += str(lastConnectionSetupSize) + ','
			line += str(lastConnectionCompleteSize) + ','
			outputFile.write(line + '\n')
		else:
			if currentSampleNumber > 0:
				print('Could not process handshake', currentSampleNumber, '| packets =', totalHandshakeNumPackets, 'MIB =', firstMIBTime, 'ConnectionComplete =', lastConnectionCompleteTime)
		totalHandshakeNumPackets = 0
		totalHandshakeSize = 0
		firstMIBTime = 0
		firstMIBNumPacketsSum = 0
		firstMIBSize = 0
		firstMIBSizeSum = 0
		lastSIB1Time = 0
		lastSIB1Size = 0
		lastSIBXTime = 0
		lastSIBXSize = 0
		lastConnectionRequestTime = 0
		lastConnectionRequestSize = 0
		lastConnectionSetupTime = 0
		lastConnectionSetupSize = 0
		lastConnectionCompleteTime = 0
		lastConnectionCompleteNumPacketsSum = 0
		lastConnectionCompleteSize = 0
		lastConnectionCompleteSizeSum = 0
		handshakeVoided = False
		currentSampleNumber = sampleNum

	#if firstMIBTime == 0 and 'MasterInformationBlock' in info:
	if 'MasterInformationBlock' in info:
		firstMIBTime = timestamp
		firstMIBNumPacketsSum = totalHandshakeNumPackets
		firstMIBSize = size
		firstMIBSizeSum = totalHandshakeSize

	elif 'SystemInformationBlockType1' in info:
		if lastSIB1Time != 0:
			print('Multiple SIB1s, terminating sample')
			handshakeVoided = True
		lastSIB1Time = timestamp
		lastSIB1Size = size
	elif 'SIB2 SIB3' in info:
		if lastSIBXTime != 0:
			print('Multiple SIBXs, terminating sample')
			handshakeVoided = True
		lastSIBXTime = timestamp
		lastSIBXSize = size
	elif 'RRCConnectionRequest' in info:
		lastConnectionRequestTime = timestamp
		lastConnectionRequestSize = size
	elif 'RRCConnectionSetupComplete' in info:
		lastConnectionCompleteTime = timestamp
		lastConnectionCompleteNumPacketsSum = totalHandshakeNumPackets + 1
		lastConnectionCompleteSize = size
		lastConnectionCompleteSizeSum = totalHandshakeSize + size
	elif 'RRCConnectionSetup' in info:
		lastConnectionSetupTime = timestamp
		lastConnectionSetupSize = size

	totalHandshakeNumPackets += 1
	totalHandshakeSize += size

inputFile.close()
outputFile.close()
print(f'Successfully wrote to {outputFilePath}. Have a nice day.')
