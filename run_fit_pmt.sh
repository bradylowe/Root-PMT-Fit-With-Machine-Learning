
# run_fit_pmt.sh
# Brady Lowe # lowebra2@isu.edu
#################################################################
# This executable is hard-coded for certain filenames, and
# it is designed for use in this directory. Upon execution of
# this code, all png's in the current directory are moved into
# a temporary directory while this script works. 

# This script will call a root analyzer for every data run in
# the current directory with a .info and .root file associated 
# with it. A png will be output for each data file, and all 
# the png's will be montaged together (single copies deleted).
##################################################################

#########################################################
# PREPARE ALL PARAMETERS FOR FITTING, LOOK FOR ERRORS 
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
	# Print summary of this fit (true/false)
	elif [[ ${name} == "printSum" ]] ; then
		printSum=${val}
	# Save png output
	elif [[ ${name} == "savePNG" ]] ; then
		savePNG=${val}
	# Save neural network output
	elif [[ ${name} == "saveNN" ]] ; then
		saveNN=${val}
	# Conditional statement for choosing which runs to evaluate
	elif [[ ${name} == "condition" ]] ; then
		condition=$(echo ${val} | sed -i "s/_/ /g")
	# Flag for printing all info 
	elif [[ ${name} == "diagnosticsMode" ]] ; then
		diagnosticsMode=${val}
	fi	
done

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
elif [ ${saveNN} ] ; then
	savePNG=false
fi
# Initialize condition
if [ ${#condition} -eq 0 ] ; then
	condition=true
fi
# Initialize diagnostics mode flag
if [ ${#diagnosticsMode} -eq 0 ] ; then
	diagnosticsMode=false
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

# Check the root file existence before processing
if [ ${#rootFile} -gt 0 ] ; then
	file=${rootFile}
	ext=$(echo ${file} | awk -F'.' '{print $NF}')
	if [ ${#ext} -eq 0 ] ; then
		echo "${file} has no extension"
		exit
	fi
	if [[ ${ext} != "root" ]] ; then
		echo "${file} does not end in .root"
		exit
	fi
	if [ ! -f ${file} ] ; then
		echo "cannot open ${file}"
		exit
	fi
	# If all is good, execute macro on this root file
	if ${diagnosticsMode} ; then
		root -l "fit_pmt_wrapper.c(\"${file}\", ${printSum}, ${conInj}, ${conGain}, ${conLL}, ${savePNG}, ${saveNN}, ${fitEngine})"
	else
		root -l -b -q "fit_pmt_wrapper.c(\"${file}\", ${printSum}, ${conInj}, ${conGain}, ${conLL}, ${savePNG}, ${saveNN}, ${fitEngine})"
	fi

	# Grab the output png
	curpng=$(ls fit_pmt*__run${runNum}_chi*_time*.png | tail -n 1)
	# Move into the proper folder
	echo eog ${curpng}
	exit
fi

########################################################################################
# If the user doesn't send in a root file, use all the root files in this directory 
# and make a montage. If there is no png filename, call it montage.png

# Label each image with filename, create tile for each image,
# use frame, and make appropriate size for viewing
montageOptions="-label '%f' -frame 5 -geometry 500x400+1+1"
if [ ${#tile} -gt 0 ] ; then
	montageOptions="${montageOptions} -tile ${tile}" 
fi

# Initialize lists of good pngs and bad pngs
goodpngs=""
badpngs=""
allpngs=""

# Loop through all files in this directory, run macro to create pngs
for file in $(ls r*.root) ; do
	# Grab runNum from file name
	if echo ${file} | grep _ ; then
		runNum=${file:1}
		runNum=$(echo ${runNum} | awk -F'_' '{print $1}')
	else
		runNum=${file:1}
		runNum=$(echo ${runNum} | awk -F'.' '{print $1}')
	fi
	# Run macro	fit_pmt_wrapper.c(...)
	# params: 	string rootFile, bool constrainInj, 
	#		bool saveResults, bool saveNN, int fitEngine,
	# returns: 	floor(chi squared per degree of freedom)
	chi2=$(root -l -b -q "fit_pmt_wrapper.c(\"${file}\", ${printSum}, ${conInj}, ${conGain}, ${conLL}, ${savePNG}, ${saveNN}, ${fitEngine})")
	chi2=$(echo ${chi2} | awk -F' ' '{print $NF}')
	# Get the filename of the png that was just created
	curpng=$(ls fit_pmt*__run${runNum}_chi*_time*.png | tail -n 1)
	allpngs="${allpngs} ${curpng}" 
	# If the chi2 value is good enough, then keep the image after
	if [ ${chi2} -lt 5 ] ; then
		goodpngs="${goodpngs} ${curpng}" 
	# Otherwise, delete it
	else
		badpngs="${badpngs} ${curpng}"
	fi
done

# Make montage from created pngs
if [ ${savePNG} ] ; then
	montage ${montageOptions} ${allpngs} ${pngFile}
	echo eog ${pngFile}
fi

# Move images
if [ ${saveNN} ] ; then
	mv ${allpngs} png_fit_nn/.
fi

