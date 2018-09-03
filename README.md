# fit_pmt
A collection of code for fitting low-light PMT data to measure the PMT gain.

The *.c files are Root (c++ interpreter) code.
The *.sh files are Linux shell scripts.
The *.ipynb are Jupyter notebook files.

List of source files:
1)  fit_pmt.c -- hardcore math (Root) for fitting histograms to functions
2)  fit_pmt_wrapper.c -- human callable wrapper for using fit_pmt.c
3)  dataAnalyzer.c -- some additional functions for the .c files
4)  run_fit_pmt.sh -- shell script for easy use of the Root fitting functions
5)  fit_pmt_conv.ipynb -- Jupyter nb for defining and training ConvNet fit classifier
6)  fit_pmt_dense.ipynb -- Jupyter nb for defining and training dense NN fit classifier
7)  dataset_interface.ipynb -- Jupyter nb for evaluating/changing data sets
8)  nn_utils.py -- custom python functions for loading dataset and other NN things 
9)  nn_diagnostics.py -- custom python functions for testing of code
10) labelmaker.sh -- shell script for labeling images for dataset

Saved models:
conv_model_success.h5/.json -- successfully trained ConvNet (model + weights)
dataset_interface_model.h5/.json -- similar to above

Additional files:
sql_select_runs.sh -- shell script for sorting runs by expt'l params
enter_run_params.sh -- shell script for catalouging expt'l setup
pmt3_injstudy_conGain70_conInj0.png -- example output of fit algorithm
r410_v965ST_5.root -- example data file (filled histograms)
run_batch.sh -- shell script for running a batch of instances of run_fit_pmt.sh

Images directory (pngs):
All pngs are output from Root after it has fit the PMT response model to data.
The pngs do not have axes, words, numbers, or tick marks. 
The pngs have black data points, cyan pedestal fit, red photo-electron fits, and a blue total fit.
The pngs are labeled based on whether or not the images appears to represent a "good" fit to the data.
Image directories are:
  Training images (train)
  Development images (dev)
  Testing images (test)


##  MORE DETAILS ABOUT FILES

fit_pmt.c  -  This Root macro defines a 9-parameter mathematical model of a PMT response.
----------------------------------------------------------------------------------------------
           -  This macro takes in around 50 input parameters which gives the user immense
              control over the parameter-space search, and also allows for highly detailed
              recording of past search attempts and results.
           -  The algorithm in this macro was defined in a NIM publication in 1992 and
              written in Root by YuXiang Zhao, then passed onto Dustin McNulty, and
              then finally to me. I have made many changes, but very few to the
              underlying mathematics.
           -  This macro outputs a png for either a human to view or a neural network.
              This allows for creating and studying of all data as well as applying
              machine learning to the same task. This macro also outptus an SQL query
              into a text file which a shell script (run_fit_pmt.sh) uses to store
              fit input and output in an SQL database.
              

fit_pmt_wrapper.c  -  This Root macro is a little more user-friendly, and it calls fit_pmt.c
----------------------------------------------------------------------------------------------
                   -  This macro serves as a bridge between the immense power and detail
                      of fit_pmt.c and the ease of use of run_fit_pmt.sh (described next).
                   -  This macro takes in only 22 parameters that are much more aligned with
                      human concerns such as which run number to use, how much to constrain
                      our varaibles during fitting, which types of outputs to save, and
                      any initial conditions we would like considered.
                   -  This macro also contains hard-coded into it all of our currently
                      accepted PMT, light source, and filter calibration values measured
                      and set by me personally. Unfortunately, some of these values are
                      subject to change (though the gains of the tubes shouldn't change).
                   -  This macro has an option to print a thorough summary of the settings
                      that went into producing this fit.
                      

run_fit_pmt.sh  -  This script is built for user interface with the fit_pmt_wrapper.c code
----------------------------------------------------------------------------------------------
                -  This script takes in an optional 15 input parameters that do not need to
                   be in any certain order.
                -  This script is a Cadillac compared to the above C-code
                -  The input param list:
                     gain (initial guess)
                     conGain (constrain gain param 0-100 percent to accepted value)
                     ll (initial light level guess)
                     conLL (constrain ll)
                     pedInj (initial pedestal injection rate guess)
                     conInj (constrain)
                     pngFile (output montage name [for multiple files])
                     rootFile (source data filename)
                     fitEngine (Root fit engine options)
                     tile (for custom montage tiling)
                     printSum (boolean for printing summary box)
                     savePNG (boolean for saving human style png)
                     saveNN (boolean for saving neural network output png)
                     runs (list of run id's to fit)
                     run_id (single run id to fit)
                -  If the user sends in either a "rootFile" or a single "run_id", then the
                   script will allow Root to remain open for the user to interact with.
                   Otherwise, Root will be ran in batch mode and only saved output will remain.
                -  After the root macro has performed the fit and saved its output pngs
                   and SQL query textfile, this script may use the png in creating
                   a montage, then it will put the png in its correct directory or delete it,
                   and then the script will grab the SQL query from the text file and
                   submit it to save the fit output to the gaindb database.
                -  Example usage:
                     ./run_fit_pmt.sh fitEngine=1 printSum=true ll=47 conGain=90 savePNG=true
                                      pngFile="nice_montage.png" runs="17 29 49 50 51"
                                      

enter_run_params.sh  -  This script is used to input expt'l parameters into the SQL database
----------------------------------------------------------------------------------------------
                     -  Database is gaindb, table is run_params
                     -  Having all the run parameters recorded in a database is necessary for
                        a sophisticated ananlysis of tons of data.
                     -  Simply execute this shell script and send in run numbers as input
                        parameters (can use hyphens). The script will prompt you to enter
                        the input params one by one and show a default value in parentheses.
                        

sql_select_runs.sh  -  This script allows the user to take advantage of the run_params table
----------------------------------------------------------------------------------------------
                       in the gaindb database.
                    -  This script takes in SQL-style conditional arguments and uses them to
                       select a list of run id's from the database that match the conditions.
                    -  Example usage:
                         ./sql_select_runs.sh "hv=2000 AND ll>=45 AND ll<=50 AND amp=1"
                    -  For a list of parameters to use in the conditions, type:
                         ./make_plot.sh help
                         

run_batch.sh  -  This script executes a batch of run_fit_pmt.sh instances
----------------------------------------------------------------------------------------------
              -  This script is simply executed as ./run_batch.sh (no input arguments)
              -  This script runs the run_fit_pmt.sh script on a predefined list of run_id's
                 with predefined input arguments. This is a way to make many different fits
                 to many different data runs at once.
                 
