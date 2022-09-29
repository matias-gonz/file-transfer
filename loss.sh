#!/usr/bin/env bash

usage() {
	echo "Usage: loss [options] (up|down)"
	echo "  -d, --device"
	echo "  -l, --latency"
	echo "  -b, --bandwidth"
	echo "  -p, --packet-loss"
}

unknown() {
	echo "Error: Unknown parameter: $1"
	echo
	usage $1
}

exe() {
	echo $1
	if ! $1; then
    	exit 1
	fi
}


device=lo      # interface
latency=100    # ms of latency
bandwidth=1000 # Kbps of bandwidth
packetloss=10  # percentage of packets to drop
up=0
down=0


while [[ "$#" -gt 0 ]]; do
    case $1 in
        -d|--device) device="$2"; shift ;;
        -l|--latency) latency="$2" ; shift ;;
        -b|--bandwidth) bandwidth="$2" ; shift ;;
        -p|--packet-loss) packetloss="$2" ; shift ;;
        up) up=1 ; shift ;;
        down) down=1 ; shift ;;
        *) unknown $1; exit 1 ;;
    esac
    shift
done


if [ $up == $down ]
then
	usage
	exit
fi


options="latency ${latency}ms  rate ${bandwidth}kbit loss ${packetloss}"


if [ $up == 1 ]
then
	exe "sudo tc qdisc add dev ${device} root netem ${options}"
	exe "sudo tc qdisc show dev ${device}"
else
	exe "sudo tc qdisc del dev ${device} root netem ${options}"
	exe "sudo tc qdisc show dev ${device}"
fi

