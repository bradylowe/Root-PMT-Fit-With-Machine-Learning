
# SET INPUT VALUE FOR ALL SELECTED RUNS
for data in $(ls r*.root) ; do

	filename=${data%.root}
	# Check for existence of info file
	info="${filename}.info"
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
	chan="12"
	gate="100"
	amp=1
	pmt=1

	echo "---------------------------------"
	echo "For ${data}"
	echo "---------------------------------"
	##################################################
	read -p "Enter hv: " hv
	# If the user sent something, grab it
        if [ ${#hv} -lt 1 ] ; then
		hv="0"
        fi
	##################################################
	read -p "Enter datarate: " datarate
	# If the user sent something, grab it
        if [ ${#datarate} -lt 1 ] ; then
		datarate="0"
        fi
	##################################################
	read -p "Enter pedrate: " pedrate
	# If the user sent something, grab it
        if [ ${#pedrate} -lt 1 ] ; then
		pedrate="0"
        fi
	##################################################
	read -p "Enter ll: " ll
	# If the user sent something, grab it
        if [ ${#ll} -lt 1 ] ; then
		ll="0"
        fi
	##################################################
	read -p "Enter filter: " filter
	# If the user sent something, grab it
        if [ ${#filter} -lt 1 ] ; then
		filter="0"
        fi
	##################################################
	read -p "Enter nevents: " nevents
	# If the user sent something, grab it
        if [ ${#nevents} -lt 1 ] ; then
		nevents="0"
        fi

	# WRITE LINE TO FILE
	line="run:${run} daq:${daq} adc:${adc} chan:${chan} gate:${gate} amp:${amp} pmt:${pmt} hv:${hv} datarate:${datarate} pedrate:${pedrate} ll:${ll} filter:${filter} nevents:${nevents}"
	echo ${line} > ${info}
	echo "${line} written to first line of ${info}"

	# Submit info to database
	query="USE gaindb; INSERT INTO exp_params (run, daq, adc, chan, gate, amp, pmt, hv, datarate, pedrate, ll, filter, nevents, filename) VALUES('${run}', '${daq}', '${adc}', '${chan}', '${gate}', '${amp}', '${pmt}', '${hv}', '${datarate}', '${pedrate}', '${ll}', '${filter}', '${nevents}', '${filename}');"
	mysql -u brady -pthesis -Bse "${query}"


done

