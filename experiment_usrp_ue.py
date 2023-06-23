import os
import shutil
import sys
import time

numSamples = 1000

# Send commands to the terminal
def terminal(cmd):
	print(cmd)
	return os.popen(cmd).read()

def startENB():
	os.system('sudo gnome-terminal -t "SRS ENB Node" -- /bin/sh -c "sudo ./build/srsenb/src/srsenb --config_file ./configs/enb.conf"')

def stopENB():
	while terminal('ps -A | grep srsenb').strip() != '':
		print('Waiting for srsenb to terminate...')
		time.sleep(2)
		terminal('sudo pkill -f -9 srsenb')


if __name__ == "__main__":
	startIndex = 0

	saveDirectory = 'automated_PCAP_logs_USRP'
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

	#terminal('cd ethereum_researcher;./run_with_redis.sh')

	i = startIndex
	while i < numSamples:
		while os.path.exists(f'{saveDirectory}/ue_mac_{i+1}.pcap'):
			print(f'Skipping sample {i + 1} of {numSamples}...')
			i += 1

		print(f'Sample {i + 1} of {numSamples}...')
		t1 = time.time()
		#output = terminal('./build/srsue/src/srsue --config_file ./configs_USRP/ue.conf')
		startENB()
		time.sleep(3)
		output = terminal('sudo timelimit -t45 ./build/srsue/src/srsue --config_file ./configs/ue.conf') # If it takes more than 300 seconds (5 minutes), then something must be wrong
		print(output)
		t2 = time.time()
		if (t2 - t1) <= 40:
			time.sleep(2)
			shutil.copy2('pcaps/ue_mac.pcap', f'{saveDirectory}/ue_mac_{i+1}.pcap')
			shutil.copy2('pcaps/enb_mac.pcap', f'{saveDirectory}/enb_mac_{i+1}.pcap')
			print(f'	Files saved to automated_PCAP_logs_USRP.')
			i += 1
		else:
			print(f'Five minute timeout reached, re-doing sample {i + 1}.')
			print('Re-starting in 10 seconds...')
			time.sleep(5)
		stopENB()
