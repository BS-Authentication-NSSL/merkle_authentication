import os
import shutil
import sys
import time
import random

numSamples = 10000
logPCAPs = False

sampleOrder = [8, 16, 32, 64, 128, 255]
minSize = 8
maxSize = 255

def setSizeCounter(value = None):
	print('Size set to', value)
	if value > maxSize or value < minSize: value = minSize
	with open('configs/size_experiment_overhead_bytes.txt', 'w') as file:
		file.write(str(value))
	return value

def terminal(cmd):
	print(cmd)
	return os.popen(cmd).read()

if __name__ == "__main__":
	startIndex = 0
	saveDirectory = 'automated_PCAP_logs'
	if os.path.exists(f'{saveDirectory}/ue_mac_1.pcap'):
		resume = input(f'Resume past session from "{saveDirectory}"? (y/n) ') in ['Y', 'y', 'yes']
		if resume:
			while os.path.exists(f'{saveDirectory}/ue_mac_{startIndex+1}.pcap'):
				startIndex += 1
			print(f'Resumed to sample {startIndex + 1} of {numSamples}')
		else:
			removeContents = input(f'Remove all contents from "{saveDirectory}" so that the experiment can start fresh? (y/n) ') in ['Y', 'y', 'yes']
			if removeContents:
				shutil.rmtree(saveDirectory)
				print('Experiment directory cleared.')
			else:
				sys.exit()
		
	if not os.path.exists(saveDirectory):
		os.makedirs(saveDirectory)

	i = startIndex
	sampleNumBytes = sampleOrder[i % len(sampleOrder)]
	currentSize = setSizeCounter(sampleNumBytes)
	while i < numSamples:
		while os.path.exists(f'{saveDirectory}/ue_mac_{currentSize}_bytes_{i+1}.pcap'):
			print(f'Skipping sample {i + 1} of {numSamples}...')
			i += 1
			sampleNumBytes = sampleOrder[i % len(sampleOrder)]
			currentSize = sampleNumBytes

		print(f'Sample {i + 1} of {numSamples}...')
		t1 = time.time()
		terminal('timelimit -t300 python3 start_then_stop.py') # If it takes more than 300 seconds (5 minutes), then something must be wrong
		t2 = time.time()
		if (t2 - t1) <= 290 and os.path.exists('pcaps/ue_mac.pcap'):
			time.sleep(2)
			if logPCAPs:
				shutil.copy2('pcaps/ue_mac.pcap', f'{saveDirectory}/ue_mac_{currentSize}_bytes_{i+1}.pcap')
				shutil.copy2('pcaps/enb_mac.pcap', f'{saveDirectory}/enb_mac_{currentSize}_bytes_{i+1}.pcap')
				os.remove('pcaps/ue_mac.pcap')
				os.remove('pcaps/enb_mac.pcap')
				print(f'	Files saved to automated_PCAP_logs.')
			i += 1
			sampleNumBytes = sampleOrder[i % len(sampleOrder)]
			currentSize = setSizeCounter(sampleNumBytes)
		else:
			print(f'Five minute timeout reached, re-doing sample {i + 1}.')

			count = 0
			while terminal('ps -A | grep srsepc').strip() != '':
				print('Waiting for EPC to terminate...')
				if count > 30:
					terminal('sudo pkill -SIGKILL srsepc')
				else:
					terminal('sudo pkill -SIGTERM srsepc')
				time.sleep(2)
				count += 1

			count = 0
			while terminal('ps -A | grep srsenb').strip() != '':
				print('Waiting for eNB to terminate...')
				if count > 30:
					terminal('pkill -SIGKILL srsenb')
				else:
					terminal('pkill -SIGTERM srsenb')
				time.sleep(2)
				count += 1

			terminal('./clear_network_namespace.sh')
			print('Re-starting in 10 seconds...')
			time.sleep(10)