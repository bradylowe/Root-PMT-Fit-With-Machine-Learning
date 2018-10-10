# fit_pmt
A collection of code for fitting low-light PMT data to measure the PMT gain.

This project uses Cern Root C++ program suite for very rigorous mathematical fitting
of functions to data points, mysql for storing and managing all collected data as 
well as results of all data analysis performed, shell scripts for managing files and
mysql database, and python code for neural network models used in data analysis.

The *.c and *.root files are Root (c++ interpreter) code.
The *.sh files are Linux shell scripts.
The *.ipynb are Jupyter notebook files.
The gaindb.sql file is a backup of the mysql database used.

## List of directories and their contents:
1)  database_tools -- Shell scripts and other code for looking at all collected info
	1)  labelmaker.sh -- shell script for labeling fit_pmt output images (good/bad)
	2)  enter_run_params.sh -- script for inserting run parameters of new data
	3)  make_plot* -- collection of files used for making plots from mysql database
	4)  sql_select* -- collection of files for querying mysql database
	5)  *.txt -- files output from macros (only macros look at these files)
2)  docs -- Contains some pdfs explaining PMT gain measurements and analysis
	1)  new_pmt_response_jlab.pdf -- multi-stage fit_pmt model
	2)  NIM_A339_468_PMT_Calibration.pdf -- this defines fit_pmt algorithm
	3)  pmt_sim_tilecal-99-012.pdf -- monte carlo simulation of pmt stages
	4)  recent_1-s2.0-S016890021730311X-main.pdf -- pmt-independent model
	5)  rpp2014-rev-probability.pdf -- this gives detailed statistics explanation
3)  nn_models -- Contains jupyter notebook for implementing neural nets
	1)  fit_pmt_conv* -- jupyter notebooks for defining and training conv nets
	2)  nn_utils.py -- custom python functions for loading dataset and other NN things 
	3)  dataset_interface.ipynb -- jupyter nb for evaluating/changing data sets
	4)  trained -- directory containing trained models
4)  root_fit_algorithm -- This is where Root macros live and work.
	1)  fit_pmt.c -- hardcore math (Root) for fitting histograms to functions
	2)  fit_pmt_wrapper.c -- human callable wrapper for using fit_pmt.c
	3)  run_fit_pmt.sh -- shell script for easy use of the fit_pmt algorithm
	4)  run_batch.sh -- shell script for running run_fit_pmt many times
	5)  dataAnalyzer.c -- some user-defined functions for fit_pmt algorithm and other
	6)  pedestalFit* -- files for analyzing the background noise of our setup
5)  images -- Here we store a few images for you to use for testing code
6)  data -- Here we store a few data runs for you to use for testing code


## Images explanation:
All pngs are output from Root after it has fit the PMT response model to data.
The pngs do not have axes, words, numbers, or tick marks. 
The pngs have black data points, cyan pedestal fit, red photo-electron fits, and a blue total fit.
The pngs are labeled based on whether or not the images appears to represent a "good" fit to the data.
Some pngs are linear scale on y axis, some are log scale (log0 or log1 in filename)
Separation of images (train, dev, test):
	** Development set images are images where run_id % 10 == 0
	** Testing set images have run_id % 10 == 1
	** Training set images have run_id % 10 > 1

