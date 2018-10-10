
if [ $# -eq 0 ] ; then
	log="X"
else
	if [[ $1 == "both" ]] ; then
		log="X"
	elif [[ $1 == "log" ]] ; then
		log="1"
	elif [[ $1 == "nonlog" || $1 == "linear" ]] ; then
		log="0"
	else
		log=$1
	fi
fi


pngs=$(head -n 1 selected_pngs.txt | sed "s/log0/log${log}/g")
eog ${pngs}
