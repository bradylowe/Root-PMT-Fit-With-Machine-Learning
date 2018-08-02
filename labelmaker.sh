
labelfile="labels.txt"

for curimage in $(ls fit_pmt_nn__*.png) ; do
	switch=0
	name=${curimage%.png}
	echo "Enter label for ${name}"
	eog ${curimage}
	read -n 1 label
	echo "Do you want to switch your answer? (1 for yes)"
	read -n 1 switch
	if [ ${switch} -eq 1 ] ; then
		if [ ${label} -eq 1 ] ; then
			label=0
		else
			label=1
		fi
	fi
	outfile="${name}_label${label}.txt"
	echo ${outfile} >> ${labelfile}
	mv ${curimage} labeled/${name}_label${label}.png
done
