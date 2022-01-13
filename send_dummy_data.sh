#!/usr/bin/bash
for i in {0..65535}
do
	# yes this is trigonometric functions in BASH
	# I didnt know this was possible
	v1=$(echo "s(2*3.1415*$i/15535)*60000" | bc -l)
	v=$(printf "%.0f" $v1)
        p1=$(echo "s(2*3.1415*$i/25535)*20000" | bc -l)
        p=$(printf "%.0f" $p1)
	BASECMD="cansend vcan0 450#"
	VAL=$(printf "%04X" $p)
	VAL2=$(printf "%04X" $v)
	CMD=${BASECMD}${VAL}${VAL2}
	eval $CMD
done
