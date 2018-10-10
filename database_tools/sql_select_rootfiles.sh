


# Loop through input params to form condition statement
ret=$(mysql --defaults-extra-file=~/.mysql.cnf -Bse "USE gaindb; SELECT rootfile FROM run_params WHERE $1 ;")
echo ${ret} > selected_rootfiles.txt
echo "$(mysql --defaults-extra-file=~/.mysql.cnf -Bse "USE gaindb; SELECT COUNT(run_id) FROM run_params WHERE $1 ;") files selected"

