#!/usr/bin/bash
for p in {0..65535}
do
	v1=$(echo "$p + s($p-35000)*2000" | bc -l)
	v=$(printf "%.0f" $v1)
	BASECMD="cansend vcan0 450#"
	VAL=$(printf "%04X" $p)
	VAL2=$(printf "%04X" $v)
	CMD=${BASECMD}${VAL}${VAL2}
	eval $CMD
done
