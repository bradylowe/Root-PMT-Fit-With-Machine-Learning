
# If user sends in filename AND parameter
if [ $# -eq 2 ] ; then
	file=$1
	attrib=$2

	line=$(head -n 1 ${file})
	for item in ${line} ; do
	        name=$(echo ${item} | awk -F':' '{print $1}')
	        if [[ ${name} == ${attrib} ]] ; then
	                echo ${item} | awk -F':' '{print $2}'
	                exit
	        fi
	done
# Else, if user just sends in an attribute
elif [ $# -eq 1 ] ; then
	attrib=$1
	line=$(head -n 1 ${file})
        for item in ${line} ; do
                name=$(echo ${item} | awk -F':' '{print $1}')
                if [[ ${name} == ${attrib} ]] ; then
                        echo ${item} | awk -F':' '{print $2}'
                fi
        done
# Otherwise, just print out all info on all files
else
	for file in $(ls dir_processed_data/r*.info) ; do
		if [ -f ${file} ] ; then
			head -n 1 ${file}
		fi
	done
fi
