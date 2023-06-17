#!/bin/sh

if [ $1 = "params" ]; then
	./build/srsue/src/srsue --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1
else
    ./build/srsue/src/srsue
fi

printf "%s " "Press enter to continue"
read ans