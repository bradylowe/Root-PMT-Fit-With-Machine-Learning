
# Loop through input params to form condition statement
if [ $# -eq 0 ] ; then
        # Query database
        ret=$(mysql --defaults-extra-file=~/.mysql.cnf -Bse "USE gaindb; SELECT run_id FROM run_params ;")
	# Make values comma-separated
	ret=$(echo ${ret} | sed "s/ /,/g")
        echo ${ret} > run_list.txt
        echo ${ret}
	echo "$(mysql --defaults-extra-file=~/.mysql.cnf -Bse "USE gaindb; SELECT COUNT(run_id) FROM run_params ;") files selected"
else
        # Query database
        ret=$(mysql --defaults-extra-file=~/.mysql.cnf -Bse "USE gaindb; SELECT run_id FROM run_params WHERE $1 ;")
	# Make values comma-separated
	ret=$(echo ${ret} | sed "s/ /,/g")
        echo ${ret}
	echo ${ret} > run_list.txt
	echo "$(mysql --defaults-extra-file=~/.mysql.cnf -Bse "USE gaindb; SELECT COUNT(run_id) FROM run_params WHERE $1 ;") files selected"
fi

