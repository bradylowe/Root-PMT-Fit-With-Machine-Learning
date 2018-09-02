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

Images directory (pngs):
All pngs are output from Root after it has fit the PMT response model to data.
The pngs do not have axes, words, numbers, or tick marks. 
The pngs have black data points, cyan pedestal fit, red photo-electron fits, and a blue total fit.
The pngs are labeled based on whether or not the images appears to represent a "good" fit to the data.
Image directories are:
  Training images (train)
  Development images (dev)
  Testing images (test)
