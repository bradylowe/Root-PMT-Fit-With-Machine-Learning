
for curimage in $(ls unlabeled/fit_pmt_nn__*.png) ; do
	name=${curimage%.png}
	name=${name#unlabeled/}
	echo "Enter label for ${name}"
	eog ${curimage}
	read -n 1 label
	outfile="${name}_label${label}.txt"
	mv ${curimage} labeled/${name}_label${label}.png
done
