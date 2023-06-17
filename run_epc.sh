#!/bin/sh

if [ $1 = "params" ]; then
	sudo ./build/srsepc/src/srsepc ~/.config/srsran/epc.conf
else
	sudo ./build/srsepc/src/srsepc ~/.config/srsran/epc.conf
fi

printf "%s " "Press enter to continue"
read ans