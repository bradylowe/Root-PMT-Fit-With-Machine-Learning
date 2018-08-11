
# run_fit_pmt.sh
# Brady Lowe # lowebra2@isu.edu
#
#################################################################
# This script will call a root analyzer for every data run in
# the current directory with a .root file associated 
# with it. A png will be output for each data file, and all 
# the png's will be montaged together (single copies deleted).
##################################################################

########################
# Define constants ###
######################

# Directory where data files are stored
data_dir="dir_processed_data"
# This is a file used to pass data back from the Root
# macro to this script
sqlfile="sql_output.txt"


#######################################################
# Decode input parameters
######################################################
#  ## Should have the form:  optionName=optionValue
#  ## Example:               conGain=90
#  ## This means we will constrain the gain to within
#  ## 90% of what we think it really is.
#######################################################

# Loop through input parameters
for item in $* ; do
	# Grab name of input param
	name=$(echo ${item} | awk -F'=' '{print $1 }')
	# Grab value
	val=$(echo ${item} | awk -F'=' '{print $2 }')
	# Initial gain guess
	if [[ ${name} == "gain" ]] ; then
		gain=${val}
	# Percent gain is allowed to vary
	elif [[ ${name} == "conGain" ]] ; then
		conGain=${val}
	# Initial light level guess
	elif [[ ${name} == "ll" ]] ; then
		ll=${val}
	# Percent ll is allowed to vary
	elif [[ ${name} == "conLL" ]] ; then
		conLL=${val}
	# Initial ped injection guess
	elif [[ ${name} == "pedInj" ]] ; then
		pedInj=${val}
	# Percent pedInj is allowed to vary
	elif [[ ${name} == "conInj" ]] ; then
		conInj=${val}
	# PNG Filename
	elif [[ ${name} == "pngFile" ]] ; then
		pngFile=${val}
	# Root Filename (if null, all will be used)
	elif [[ ${name} == "rootFile" ]] ; then
		rootFile=${val}
	# Fit engine option choice (integer)
	elif [[ ${name} == "fitEngine" ]] ; then
		fitEngine=${val}
	# Tile option to use for montage
	elif [[ ${name} == "tile" ]] ; then
		tile=${val}
	# Print summary of this fit to screen (true/false)
	elif [[ ${name} == "printSum" ]] ; then
		printSum=${val}
	# Save png output (human format)
	elif [[ ${name} == "savePNG" ]] ; then
		savePNG=${val}
	# Save png output (neural network format)
	elif [[ ${name} == "saveNN" ]] ; then
		saveNN=${val}
	fi	
done

##########################################################
# Check all necessary input values, initialize if needed
# Correct errors
##########################################################

# Initialize no gain constrain
if [ ${#conGain} -eq 0 ] ; then
	conGain=0
fi
# Initialize full ped injection rate constrain
if [ ${#conInj} -eq 0 ] ; then
	conInj=100
fi
# Initialize no light level constraint
if [ ${#conLL} -eq 0 ] ; then
	conLL=0
fi
# Initialize printSum 
if [ ${#printSum} -eq 0 ] ; then
	printSum=true
fi
# Initialize savePNG
if [ ${#savePNG} -eq 0 ] ; then
	savePNG=true
fi
# Initialize saveNN
if [ ${#saveNN} -eq 0 ] ; then
	saveNN=false
fi
# Make sure this file ends in .png
if [ ${#pngFile} -gt 0 ] ; then
	ext=$(echo ${pngFile} | awk -F'.' '{print $NF}')
	if [ ${#ext} -eq 0 ] ; then
		echo "${pngFile} has no extension"
		exit
	fi
	if [[ ${ext} != "png" ]] ; then
		echo "${pngFile} does not end in .png"
		exit
	fi
else
	# Initialize value, if need be
	echo "Using pngFile = montage.png"
	pngFile="montage.png"
fi
# Initialize fitEngine selection
if [ ${#fitEngine} -eq 0 ] ; then
	fitEngine=0
fi

###########################################
# EXECUTE FITTING ALGORITHM WITH PARAMETERS
# FOUND IN THE ABOVE PROCESSES
##############################

# If user sends in a root filename, just process the one file
###############################################################
if [ ${#rootFile} -gt 0 ] ; then

	# Check for file existence
	if [ ! -f ${rootFile} ] ; then
		echo "${rootFile} doesn't exist. Exiting..."
		exit
	fi

	# Remove the .root suffix and dir_.../ prefix
	filename=${rootFile%.root}
	filename=${filename#dir_*/}

	# Grab the run parameters from the database
	allitems=$(mysql --defaults-extra-file=~/.mysql.cnf -Bse "USE gaindb; SELECT * FROM exp_params WHERE run_id = '${runID}';")
	set -- ${allitems}

	# If all is good, execute macro on this root file
	root -l -b -q "fit_pmt_wrapper.c(\"${rootFile}\", $1, $2, $3, $11, $10, $5, $7, $8, $9, $12, $13, ${printSum}, ${conInj}, ${conGain}, ${conLL}, ${savePNG}, ${saveNN}, ${fitEngine})"

	# Grab the output pngs
	if [ ${savePNG} ] ; then
		humanpng=$(ls fit_pmt__run$2_chi*_time*.png | tail -n 1)
		mv ${humanpng} png_fit/.
		echo eog png_fit/${humanpng}
		eog png_fit/${humanpng}
	fi
	if [ ${saveNN} ] ; then
		nnpng=$(ls fit_pmt_nn__run$2_chi*_time*.png | tail -n 1)
		mv ${nnpng} png_fit_nn/.
		echo eog png_fit_nn/${nnpng}
		eog png_fit_nn/${nnpng}
	fi

	# Query the database to store all output info from this fit
	if [ -f ${sqlfile} ] ; then
		# The query was created by the root macro and written to file
		query=$(head -n 1 ${sqlfile})
		# We don't want anything that is "not a number"
		query=$(echo ${query} | sed "s/nan/-1.0/g")
		res=$(mysql --defaults-extra-file=~/.mysql.cnf -Bse "${query}")
		if [[ ${res:0:5} != "ERROR" ]] ; then
			# Delete file after query submission to avoid double submission
			rm ${sqlfile}
			# Alert user and exit
			echo Run output successfully saved.
			exit
		fi
	fi

	# Alert user and exit
	echo Unable to find SQL query. Run output NOT SAVED.
	exit
fi
######################################
# exit after executing fit on file
##################################################################################

###############################################################################
# If the user doesn't send in a root file, read the numbers in run_list.txt
#
#  ## You can set the values in run_list.txt via the script sql_select_data.sh.

# Initialize lists of good pngs and bad pngs
goodpngs=""
badpngs=""
humanpngs=""
nnpngs=""


# If the run_list.txt file doesn't exist, just exit
if [ ! -f run_list.txt ] ; then
	echo "No files to process. Exiting..."
	exit
fi
# Loop through all files in list, run macro to create png and numbers each time
for runID in $(head -n 1 run_list.txt) ; do

	# Grab the run parameters from the database
	allitems=$(mysql --defaults-extra-file=~/.mysql.cnf -Bse "USE gaindb; SELECT * FROM exp_params WHERE run_id = '${runID}';")
	set -- ${allitems}
	# Setup root file from base name and directory
	rootfile="${data_dir}/${15}.root"

	# Run fitting algorithm
	chi2=$(root -l -b -q "fit_pmt_wrapper.c(\"${rootfile}\", ${runID}, $2, $3, ${11}, ${10}, $5, $7, $8, $9, ${12}, ${13}, ${printSum}, ${conInj}, ${conGain}, ${conLL}, ${savePNG}, ${saveNN}, ${fitEngine})")
	chi2=$(echo ${chi2} | awk -F' ' '{print $NF}')
	echo chi2 ${chi2}
	
	# Grab the output pngs
	humanpng=""
	if [ ${savePNG} ] ; then
		humanpng=$(ls fit_pmt__run$2_chi*_time*.png | tail -n 1)
		humanpngs="${humanpngs} ${humanpng}" 
		mv ${humanpng} png_fit/.
		echo eog png_fit/${humanpng}
		eog png_fit/${humanpng}
	fi
	if [ ${saveNN} ] ; then
		nnpng=$(ls fit_pmt_nn__run$2_chi*_time*.png | tail -n 1)
		nnpngs="${nnpngs} ${nnpng}"
		mv ${nnpng} png_fit_nn/.
		echo eog png_fit_nn/${nnpng}
		eog png_fit_nn/${nnpng}
	fi

	# If the chi squared value is good enough, keep the image
	if [ ${chi2} -lt 10 ] ; then
		goodpngs="${goodpngs} ${humanpng}"
	# Otherwise, delete it
	else
		badpngs="${badpngs} ${humanpng}"
	fi

	# Query the database to store all output info from this fit
	if [ -f ${sqlfile} ] ; then
		# The query was created by the root macro and written to file
		query=$(head -n 1 ${sqlfile})
		# We don't want anything that is "not a number"
		query=$(echo ${query} | sed "s/nan/-1.0/g")
		res=$(mysql --defaults-extra-file=~/.mysql.cnf -Bse "${query}")
		# Delete file after query submission to avoid double submission
		if [[ ${res:0:5} != "ERROR" ]] ; then
			rm ${sqlfile}
		fi
	fi
done

# Label each image with filename, create tile for each image,
# use frame, and make appropriate size for viewing
montageOptions="-label '%f' -frame 5 -geometry 500x400+1+1"
if [ ${#tile} -gt 0 ] ; then
	montageOptions="${montageOptions} -tile ${tile}" 
fi

# Make montage from created pngs (default montage.png)
if [ ${savePNG} ] ; then
	montage ${montageOptions} ${humanpngs} images/${pngFile}
	echo eog images/${pngFile}
	eog images/${pngFile}
fi

# Move images
if [ ${savePNG} ] ; then
	mv ${goodpngs} png_fit/.
	rm ${badpngs}
fi
if [ ${saveNN} ] ; then
	mv ${nnpngs} png_fit_nn/.
fi

