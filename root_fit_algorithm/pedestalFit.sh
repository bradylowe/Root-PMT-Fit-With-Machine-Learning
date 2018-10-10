
runs=$(head selected_runs.txt)

if [ $# -eq 1 ] ; then
	savePNG=$1
else
	savePNG=0
fi

for run_id in ${runs} ; do
	rootfile=$(mysql --defaults-extra-file=~/.mysql.cnf -Bse "USE gaindb; SELECT rootfile FROM run_params WHERE run_id=${run_id};")
	root -l "pedestalFit.c(\"${rootfile}\", 12, ${savePNG})"
	echo "Continue? (y/n)"
	read -n 1 choice 
	if [[ ${choice} == "n" || ${choice} == "N" ]] ; then
		exit
	fi
done
