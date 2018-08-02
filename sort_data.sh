
# Check for existence of inactive data folder
if [ ! -f dir_inactive_data ] ; then
	mkdir dir_inactive_data
fi

# Move all data into this folder for analyzing 
mv r*.info r*.root dir_inactive_data/.

# Loop over all info files in this directory
for file in $(ls dir_inactive_data/*.info) ; do
	# Read info file
	line=$(head -n 1 ${file})
	for item in ${line} ; do
		# Decompose item (name:val)
		name=$(echo ${item} | awk -F':' '{print $1 }')
		val=$(echo ${item} | awk -F':' '{print $2}')
		# Set variable values
		if [[ ${name} == "hv" ]] ; then
			hv=${val}
		elif [[ ${name} == "nevents" ]] ; then
			nevents=${val}
		elif [[ ${name} == "filter" ]] ; then
			filter=${val}
		elif [[ ${name} == "amp" ]] ; then
			amp=${val}
		elif [[ ${name} == "run" ]] ; then
			run=${val}
		fi
	done
	# Remove prefix and suffix from name
	file=${file#*/}
	file=${file%.info}
	# Select which files to grab
	condition="true"
	condition="${condition} -a ${hv} -ge 1850"
	condition="${condition} -a ${amp} -eq 1"
	condition="${condition} -a ${nevents} -ge 100000"
	condition="${condition} -a ${run} -ge 403"
	if [ ${condition} ] ; then
		mv dir_inactive_data/${file}* .
	fi 
done
