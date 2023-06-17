import os
import sys
import time

# Send commands to the terminal
def terminal(cmd):
	print(cmd)
	return os.popen(cmd).read()

if __name__ == "__main__":
	terminal('sudo ./set_network_namespace.sh')
	terminal('sudo gnome-terminal -t "SRS EPC Node" -- /bin/sh -c \'sudo ./build/srsepc/src/srsepc --config_file ./configs/epc.conf\'')
	terminal('gnome-terminal -t "SRS ENB Node" -- /bin/sh -c \'./build/srsenb/src/srsenb --config_file ./configs/enb.conf --rf.device_name=zmq --rf.device_args="fail_on_disconnect=true,tx_port=tcp://*:2000,rx_port=tcp://localhost:2001,id=enb,base_srate=23.04e6"\'')
	terminal('./build/srsue/src/srsue --config_file ./configs/ue.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1')
	terminal('sudo pkill -SIGTERM srsepc')
	terminal('pkill -SIGTERM srsenb')

	while terminal('ps -A | grep srsepc').strip() != '':
		print('Waiting for EPC to terminate...')
		time.sleep(1)

	while terminal('ps -A | grep srsenb').strip() != '':
		print('Waiting for eNB to terminate...')
		time.sleep(1)

	terminal('./clear_network_namespace.sh')
	print('Done!')