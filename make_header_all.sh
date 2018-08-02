
# DEFINE STRUCTURE OF HEADER OF INFO FILE
attribs="pmt hv datarate pedrate ll filter nevents"

# SET INPUT VALUE FOR ALL SELECTED RUNS
for data in $(ls r*.root) ; do

	# Check for existence of info file
	info=$(echo ${data} | awk -F'.' '{print $1 }')
	info="${info}.info"
	if [ -f ${info} ] ; then
		continue
	fi

	# Initialize values that might be read from the filename
	adc="v965ST"
	daq=5

	# Decompose filename
	run=${data:1}
	if [ $(echo ${run} | grep v965ST) ] ; then	
		# Grab the run number
		run=$(echo ${run} | awk -F'_' '{print $1}')
		# Grab the adc value
		adc=$(echo ${data} | awk -F'_' '{print $2}')
		# Grab the daq value
		daq=$(echo ${data} | awk -F'_' '{print $3}')
		daq=$(echo ${daq} | awk -F'.' '{print $1}') 
	elif echo ${run} | grep _ ; then
		# Grab the run number
		run=$(echo ${run} | awk -F'.' '{print $1}')
		# Grab the daq value
		daq=$(echo ${data} | awk -F'_' '{print $2}')
		daq=$(echo ${daq} | awk -F'.' '{print $1}') 
	else
		# Grab the run number
		run=$(echo ${run} | awk -F'.' '{print $1}')
	fi
	# Define constants
	user="brady"
	roc=${daq}
	chan="12"
	gate="100"
	amp=1

	# Initialize info file line
	line="user:${user} run:${run} daq:${daq} roc:${roc} adc:${adc} chan:${chan} gate:${gate} amp:${amp}"

	# LOOP THROUGH ALL ATTRIBUTES IN FILE, BUILD OUTPUT
	echo "---------------------------------"
	echo "For ${data}"
	echo "---------------------------------"
	for attrib in ${attribs} ; do
		# Handle the light level differently
		if [[ ${attrib} == "ll" ]] ; then
			# Light level has two parts separated by a comma
			newval="empty"
			newval2="empty"
			val="empty"
			read -p "Enter ${attrib}: " newval
			read -p "Enter ${attrib}: " newval2
			# If the user sent something, grab it
                	if [ ${#newval} -ge 1 ] ; then
                	        val=${newval}
			fi
			# If the user sent a 2nd value, grab it
			if [[ ${val} != "empty" ]] ; then
				if [ ${#newval2} -ge 1 ] ; then
					val="${val},${newval2}"
				# Otherwise, append a zero (if not empty)
				else
					val="${val},0"
                		fi
			fi
			line="${line} ${attrib}:${val}"
		else
			newval="empty"
			read -p "Enter ${attrib}: " newval
			# If the user sent back a value, grab it
                	if [ ${#newval} -ge 1 ] ; then
                	        val=${newval}
			else
				val="empty"
                	fi
			line="${line} ${attrib}:${val}"
		fi
	done

	# WRITE LINE TO FILE
	echo ${line} > ${info}
	echo "${line} written to first line of ${info}"

done

