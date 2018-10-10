
# Check for input
if [ $# -eq 0 ] ; then
	echo No files selected
	exit
fi

# Query database for run_id's
runs=$(mysql --defaults-extra-file=~/.mysql.cnf -Bse "USE gaindb; SELECT run_id FROM run_params WHERE $1 ;")

# Loop over all returned runs and get all associated png files
ret1=""
for run in ${runs} ; do
	if [ ${#2} -gt 0 ] ; then
		png=$(mysql --defaults-extra-file=~/.mysql.cnf -Bse "USE gaindb; SELECT nn_png FROM fit_results WHERE run_id=${run} AND $2")
	else
		png=$(mysql --defaults-extra-file=~/.mysql.cnf -Bse "USE gaindb; SELECT nn_png FROM fit_results WHERE run_id=${run}")
	fi
	ret1="${ret1} ${png}"
done

# Loop over all png filenames and check for file existence
ret2=""
count=0
for item in ${ret1} ; do
	if [ -f ${item} ] ; then
		ret2="${ret2} ${item}"
		count=$((count + 1))
	else
		echo couldn\'t find ${item}
	fi
done

# Tell user how many found and which ones
echo ${count} pngs found
echo ${ret2} > selected_pngs.txt

