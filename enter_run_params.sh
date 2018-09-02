
#  BRADY LOWE  #  LOWEBRA2@ISU.EDU  #  9/1/2018
###################################################################
# USAGE:  ./enter_run_params.sh
#         ./enter_run_params.sh 2044
#         ./enter_run_params.sh 2012 2014 2017-2022 2029 2033-2039
#
# RESULTS:
#        Decodes all selected files using evio2nt_v965
#        Outputs a .root file for each input data file
#
# NOTES:
#        YOU MUST FIRST SOURCE ~/coda/3.06/.setup
#
####################################################################



# SELECT FILES TO USE

# Initialize
selected_runs=""
# If no arguments, just do all the files in the directory
if [ $# -eq 0 ] ; then
	selected_files=$(ls r*.root)
# Loop through all the input run numbers
else
	for run in $* ; do
		# If the arg has a dash, decompose the list
		val=$(echo ${run} | grep "-")
		if [ ${#val} -gt 0 ]; then
			# Grab begin and end values
			cur=$(echo ${run} | awk -F'-' '{print $1}')
			end=$(echo ${run} | awk -F'-' '{print $2}')
			# Loop from begin to end
			while [ ${cur} -le ${end} ] ; do
				# Grab the root file and append
				file=$(ls r${cur}*.root)
				selected_files="${selected_files} ${file}"
				# Increment current run
				cur=$((cur + 1))
			done
		# If no dash, should just be a number. Run it.
		else
			# Grab root file for this run and append it
			file=$(ls r${run}*.root)
			selected_files="${selected_files} ${file}"
		fi
	done
fi


# SET INPUT VALUE FOR ALL SELECTED RUNS
for filename in ${selected_files} ; do

	# Initialize values that might be read from the filename
	adc="v965ST"
	daq=3

	# Remove leading 'r' and '.root'
	run=${filename:1}
	run=${run%.root}
	# Filename is of style r123_v965ST_5.root
	if [ $(echo ${run} | grep v965ST) ] ; then	
		# Grab the run number
		run=$(echo ${run} | awk -F'_' '{print $1}')
		# Grab the adc value
		adc=$(echo ${filename} | awk -F'_' '{print $2}')
		# Grab the daq value
		daq=$(echo ${filename} | awk -F'_' '{print $3}')
		daq=$(echo ${daq} | awk -F'.' '{print $1}') 
	# Filename is of style r123_5.root 
	elif echo ${run} | grep _ ; then
		# Grab the run number
		run=$(echo ${run} | awk -F'.' '{print $1}')
		# Grab the daq value
		daq=$(echo ${filename} | awk -F'_' '{print $2}')
		daq=$(echo ${daq} | awk -F'.' '{print $1}') 
	# Filename is of style r123.dat
	else
		# Grab the run number
		run=$(echo ${run} | awk -F'.' '{print $1}')
	fi

	# Initialize values to common defaults
	chan="12"
	gate="100"
	amp=1
	pmt=1
	hv=2000
	datarate=3000
	pedrate=400
	filter=7
	nevents=500000
	ll=0

	echo "---------------------------------"
	echo "For ${filename}"
	echo "---------------------------------"
	##################################################
	read -p "Enter hv (${hv}): " val
	# If the user sent something, grab it
        if [ ${#val} -gt 0 ] ; then
		hv=${val}
        fi
	##################################################
	read -p "Enter channel (${chan}): " val
	# If the user sent something, grab it
        if [ ${#val} -gt 0 ] ; then
		chan=${val}
        fi
	##################################################
	read -p "Enter gate (${gate}): " val
	# If the user sent something, grab it
        if [ ${#val} -gt 0 ] ; then
		gate=${val}
        fi
	##################################################
	read -p "Enter pmt (${pmt}): " val
	# If the user sent something, grab it
        if [ ${#val} -gt 0 ] ; then
		pmt=${val}
        fi
	##################################################
	read -p "Enter daq (${daq}): " val
	# If the user sent something, grab it
        if [ ${#val} -gt 0 ] ; then
		daq=${val}
        fi
	##################################################
	read -p "Enter datarate (${datarate}): " val
	# If the user sent something, grab it
        if [ ${#val} -gt 1 ] ; then
		datarate=${val}
        fi
	##################################################
	read -p "Enter pedrate (${pedrate}): " val
	# If the user sent something, grab it
        if [ ${#val} -gt 1 ] ; then
		pedrate=${val}
        fi
	##################################################
	read -p "Enter ll (${ll}): " val
	# If the user sent something, grab it
        if [ ${#val} -gt 1 ] ; then
		ll=${val}
        fi
	##################################################
	read -p "Enter filter (${filter}): " val
	# If the user sent something, grab it
        if [ ${#val} -gt 1 ] ; then
		filter=${val}
        fi
	##################################################
	read -p "Enter nevents (${nevents}): " val
	# If the user sent something, grab it
        if [ ${#val} -gt 1 ] ; then
		nevents=${val}
        fi
	##################################################

	# Create query
	query="USE gaindb; INSERT INTO run_params (run, daq, adc, chan, gate, amp, pmt, hv, datarate, pedrate, ll, filter, nevents, filename) VALUES('${run}', '${daq}', '${adc}', '${chan}', '${gate}', '${amp}', '${pmt}', '${hv}', '${datarate}', '${pedrate}', '${ll}', '${filter}', '${nevents}', '${filename}');"
	# Submit info to database
	mysql --defaults-extra-file=~/.mysql.cnf -Bse "${query}"

	# Echo line to check query for ease of use
	echo mysql --defaults-extra-file=~/.mysql.cnf -e \"USE gaindb \; SELECT \* FROM run_params ORDER BY run_id DESC LIMIT 1\"

	# Move file into processed data director
	mv ${filename} dir_processed_data/.

done

