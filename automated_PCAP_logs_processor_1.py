import csv
import datetime
import os
import platform
import pyshark
import re
import sys
import time

assert platform.system() == 'Linux', 'Sorry, but this script can only run in a debian-based linux machine (e.g. Ubuntu or Linux Mint).'

def terminal(cmd):
	return os.popen(cmd).read()

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
	line = 'Timestamp,'
	line += 'Timestamp (s),'
	line += 'File path,'
	line += 'Sample number,'
	line += 'Packet number,'
	line += 'Size (B),'
	line += 'Layers,'
	line += 'Packet Information Summary,'
	return line


def log(filePath, sampleNum, packetNum, packet, tsharkInfoColumn):
	timestamp = packet.sniff_time
	timestamp_seconds = (timestamp - datetime.datetime(1970, 1, 1)).total_seconds()
	packetSizeBytes = packet.length

	tsharkInfo = ''
	if packetNum < len(tsharkInfoColumn):
		tsharkInfo = tsharkInfoColumn[packetNum]
	
	# layer = None
	# for layer in packet.layers:
	# 	if layer._layer_name == 'mac-lte':
	# 		break

	# #if packetNum == 3:
	# print(layer._all_fields)
	# 	#print(layer._layer_name)
	# 	#print(layer)
	 	#for key in dir(layer):
	 	#	print(key, ':\t', eval(f'layer.{key}'))
	# 	print(dir(layer))
	# print('lte_rrc_schedulinginfosib1_br_r13' in dir(layer), layer.lte_rrc_c1 if 'lte_rrc_c1' in dir(layer) else 'N/A')
	# if packetNum >= 15:
	# 	pcap.close()
	# 	sys.exit()

	line = str(timestamp) + ','
	line += str(timestamp_seconds) + ','
	line += str(filePath) + ','
	line += str(sampleNum) + ','
	line += str(packetNum) + ','
	line += str(packetSizeBytes) + ','

	layers = ''
	for i, layer in enumerate(packet.layers):
		layers += layer._layer_name + ' '

	line += layers.strip() + ','
	line += '"' + tsharkInfo + '",'
	return line

def processSample(sampleNum, filePath):
	global pcap
	pcap = pyshark.FileCapture(filePath)
	running = True
	packetNum = 0
	tsharkInfoColumn = ''
	while running:
		try:
			packet = pcap[packetNum]
			if len(tsharkInfoColumn) == 0:
				tsharkInfoColumn = terminal(f'tshark -r {filePath} -T fields -e _ws.col.Info').splitlines()
			line = log(filePath, sampleNum, packetNum, packet, tsharkInfoColumn)
			outputFile.write(line + '\n')


		except (StopIteration, KeyError): # End of file
		 	running = False
		 	break
		# except Exception as e: # Corrupt packet? Skip
		# 	print('ERROR OCCURED, SKIPPING', e)
		# 	packetNum += 1
		# 	continue
		packetNum += 1

	pcap.close()
	if packetNum == 0:
		return 'blank'
	else:
		return 'success'

directory = selectDir('.*automated_PCAP_logs.*', True)

outputFilePath = f'{directory}_processed.csv'
outputFile = open(outputFilePath, 'w')
outputFile.write(header() + '\n')

sampleNum = 1
processing = True
prevStatus = 'success'
missedSamples = 1000

while processing:
	filePath = f'{directory}/ue_mac_{sampleNum}.pcap'
	if os.path.exists(filePath):
		print(f'Processing: {filePath}... ', end='')
		if prevStatus == 'blank':
			# This is a shortcut that saves a lot of time on blank files in sequence
			# If it saw 'blank' last, then before even opening the pcap, check its size and skip it if the size is zero.
			if os.path.getsize(filePath) == 0:
				print(prevStatus)
				sampleNum += 1
				continue
		missedSamples = 1000
		try:
			prevStatus = processSample(sampleNum, filePath)
			print(prevStatus)
		except KeyboardInterrupt:
			print('eof')
			processing = False
			break
		except:
			print('error')
			print('Unable to open PCAP for processing, skipping')
	else:
		print(f' Not found:     {filePath}.')
		missedSamples -= 1
		if missedSamples <= 0:
			print('Missed samples threshold exceeded. Stopping.')
			processing = False
	sampleNum += 1

outputFile.close()
print(f'Successfully wrote to {outputFilePath}. Have a nice day.')