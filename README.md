# fit_pmt
A collection of code for fitting low-light PMT data to measure the PMT gain.

List of source files:
1)  fit_pmt.c -- hardcore math (Root) for fitting histograms to functions
2)  fit_pmt_wrapper.c -- human callable wrapper for using fit_pmt.c
3)  dataAnalyzer.c -- some additional functions for the .c files
4)  run_fit_pmt.sh -- shell script for easy use of the Root fitting functions
5)  fit_pmt_conv.ipynb -- Jupyter nb for defining ConvNet fit classifier
6)  fit_pmt_dense.ipynb -- Jupyter nb for defining dense NN fit classifier
7)  dataset_interface.ipynb -- Jupyter nb for evaluating/changing data set
8)  nn_utils.py -- custom python functions for dataset and other NN things 
9)  nn_diagnostics.py -- custom python functions for testing of code
10) labelmaker.sh -- shell script for labeling images for dataset

Saved models:
conv_model_success.h5/.json -- successfully trained ConvNet (model + weights)
dataset_interface_model.h5/.json -- similar to above

Additional files:
sort_data.sh -- shell script for rearranging files in directory
make_header_all.sh -- shell script for catalouging expt'l setup
pmt3_injstudy_conGain70_conInj0.png -- example output of fit algorithm
r410_v965ST_5.root -- example data file (filled histograms)
r410_v965ST_5.info -- example info file for expt'l setup information

Training images (in images directory)
  Training set 80%
  Dev set 10%
  Test set 10%
