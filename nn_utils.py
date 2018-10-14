import numpy as np
import glob
from pathlib import Path
from scipy import misc
from PIL import Image

####################################################################################
# Because we have to invert and normalize our images for our networks to learn
# from them, we must undo these changes to the images if we want to view the 
# images ourselves.

def get_printable_image(this_image):
    this_image = 255 - this_image * 255
    this_image = misc.toimage(this_image)
    return this_image

####################################################################################
# This function takes in a model along with datasets, uses the model to make
# predictions on the data sets, uses the labels to check its predictions, computes
# statistics describing performance, and returns these values.

def get_stats(model, train_x, train_y, test_x = '', test_y = ''):
    # Calculate predictions
    predictions = model.predict(x=train_x)
    predictions = np.floor(predictions + 0.5)
    # Get vector mask for good and bad fits and right and wrong answers
    good_fits = train_y
    bad_fits = 1 - good_fits
    wrong_answers = np.abs(np.subtract(predictions, good_fits))
    right_answers = np.subtract(1, wrong_answers)
    # Calculate true positives (tp), as well as (tn) (fp) (fn)
    true_positives = np.multiply(right_answers, good_fits)
    true_negatives = np.multiply(right_answers, bad_fits)
    false_positives = np.multiply(wrong_answers, good_fits)
    false_negatives = np.multiply(wrong_answers, bad_fits)
    # Calculate additional metrics
    train_acc = np.sum(right_answers) / np.sum(right_answers + wrong_answers)
    train_prec = np.sum(true_positives) / np.sum(true_positives + false_positives)
    train_rec = np.sum(true_positives) / np.sum(true_positives + false_negatives)
    if test_x == '':
        return train_acc, train_prec, train_rec

    # Do it again for testing set
    predictions = model.predict(x=test_x)
    predictions = np.floor(predictions + 0.5)
    good_fits = test_y
    bad_fits = 1 - good_fits
    wrong_answers = np.abs(np.subtract(predictions, good_fits))
    right_answers = np.subtract(1, wrong_answers)
    true_positives = np.multiply(right_answers, good_fits)
    true_negatives = np.multiply(right_answers, bad_fits)
    false_positives = np.multiply(wrong_answers, good_fits)
    false_negatives = np.multiply(wrong_answers, bad_fits)
    test_acc = np.sum(right_answers) / np.sum(right_answers + wrong_answers)
    test_prec = np.sum(true_positives) / np.sum(true_positives + false_positives)
    test_rec = np.sum(true_positives) / np.sum(true_positives + false_negatives)

    # Return all
    return train_acc, train_prec, train_rec, test_acc, test_prec, test_rec

####################################################################################
# This function loads images of an attempt to fit some data points to a curve. 
# These images are used to train convolutional models hwo to classify fits as
# either good or bad. Information on which files to load and where to get them is
# stored in the MySQL database gaindb.


def load_dataset_cnn(m=-1, return_filenames=False, im_dir="train", log=False):

    # Define condition for selecting train, dev, test set.
    # For dev, fit_id % 10 == 0
    # For test, fit_id % 10 == 1
    if (im_dir == "train"):
        im_dir = "MOD(run_id, 10) > 1;"
    elif (im_dir == "dev"):
        im_dir = "MOD(run_id, 10) = 0;"
    elif (im_dir == "test"):
        im_dir = "MOD(run_id, 10) = 1;"
    else:
        print("im_dir entry not valid")
        return 0

    # DEFINE IMAGE DIMENSIONS
    scale = 4
    wpx, hpx = 87 * scale, 59 * scale

    # Connect to mysql database
    import mysql.connector
    gaindb = mysql.connector.connect(
        host='localhost', user='brady',
        password='thesis', database='gaindb'
    )

    # Query database
    data = gaindb.cursor()
    data.execute("SELECT nn_png, label FROM fit_results WHERE nn_png IS NOT NULL AND label IS NOT NULL AND label<2 AND " + im_dir)

    # Grab pngs from file, create lists
    images = []
    labels = []
    filenames = []
    for (filename, label) in data:
        # Change the filename if log plot
        if log:
            filename = filename.replace("log0", "log1")
        # Save the filename
        filenames.append(filename)
        # Read in image to array
        cur_png = misc.imread(filename)
        # Reduce resolution and append to list
        images.append(misc.imresize(cur_png, (hpx, wpx)))
        # Grab the label off the end of the filename
        labels.append(label)
        # Exit the loop if we hit the limit
        if m != -1 and len(labels) >= m:
            break

    # Convert all gathered info into arrays
    images = np.asarray(images)
    labels = np.asarray(labels)

    # Find out how many images were loaded
    m = images.shape[0]

    # Invert and normalize images
    images = (255. - images) / 255.

    # Reshape labels
    labels = labels.reshape(labels.shape[0], 1)

    # Return values
    if return_filenames:
        return images, labels, filenames
    else:
        return images, labels

####################################################################################
# This function loads all the information available about the labeled Root fits for
# the purpose of achieving the highest possible accuracy on neural net 
# classification of Root fits. This includes loading PNG images as well as values
# from MySQL database gaindb.

def load_dataset_all(m=-1, im_dir="train", log=False, im_path=""):

    # Define condition for selecting train, dev, test set.
    # For dev, fit_id % 10 == 0
    # For test, fit_id % 10 == 1
    if (im_dir == "train"):
        im_dir = "MOD(run_id, 10) > 1;"
    elif (im_dir == "dev"):
        im_dir = "MOD(run_id, 10) = 0;"
    elif (im_dir == "test"):
        im_dir = "MOD(run_id, 10) = 1;"
    else:
        print("im_dir entry not valid")
        return 0

    # DEFINE IMAGE DIMENSIONS
    scale = 4
    wpx, hpx = 87 * scale, 59 * scale

    # Connect to mysql database
    import mysql.connector
    gaindb = mysql.connector.connect(
        host='localhost', user='brady',
        password='thesis', database='gaindb'
    )

    # Query database
    data = gaindb.cursor()
    data.execute("SELECT * FROM fit_results WHERE nn_png IS NOT NULL AND label IS NOT NULL AND label<2 AND " + im_dir)

    # Grab pngs from file, create lists
    images = []
    labels = []
    filenames = []
    params=[]
    for (fit_id, run_id, fit_engine, fit_low, fit_high, min_pe, max_pe, w_0, ped_0, ped_rms_0, alpha_0, mu_0, sig_0, sig_rms_0, inj_0, real_0, w_min, ped_min, ped_rms_min, alpha_min, mu_min, sig_min, sig_rms_min, inj_min, real_min, w_max, ped_max, ped_rms_max, alpha_max, mu_max, sig_max, sig_rms_max, inj_max, real_max, w_out, ped_out, ped_rms_out, alpha_out, mu_out, sig_out, sig_rms_out, inj_out, real_out, w_out_error, ped_out_error, ped_rms_out_error, alpha_out_error, mu_out_error, sig_out_error, sig_rms_out_error, inj_out_error, real_out_error, chi, gain, gain_error, gain_percent_error, _, filename, label) in data:
        # Change the filename if log plot
        if log:
            filename = filename.replace("log0", "log1")
	# Append path
        filename = im_path + filename
        # Save the filename
        filenames.append(filename)
        # Read in image to array
        cur_png = misc.imread(filename)
        # Reduce resolution and append to list
        images.append(misc.imresize(cur_png, (hpx, wpx)))
        # Append other values to their lists
        labels.append(label)
        # Grab parameters into a list and append it to list
        param=[fit_engine, fit_low, fit_high, min_pe, max_pe, w_0, ped_0, ped_rms_0, alpha_0, mu_0, sig_0, sig_rms_0, inj_0, real_0, w_min, ped_min, ped_rms_min, alpha_min, mu_min, sig_min, sig_rms_min, inj_min, real_min, w_max, ped_max, ped_rms_max, alpha_max, mu_max, sig_max, sig_rms_max, inj_max, real_max, w_out, ped_out, ped_rms_out, alpha_out, mu_out, sig_out, sig_rms_out, inj_out, real_out, w_out_error, ped_out_error, ped_rms_out_error, alpha_out_error, mu_out_error, sig_out_error, sig_rms_out_error, inj_out_error, real_out_error, chi, gain, gain_error, gain_percent_error]
        params.append(param)
	
        # Exit the loop if we hit the limit
        if m != -1 and len(labels) >= m:
            break

    # Convert all gathered info into arrays
    images = np.asarray(images)
    labels = np.asarray(labels)
    params = np.asarray(params)

    # Find out how many images were loaded
    m = images.shape[0]

    # Invert and normalize images
    images = (255. - images) / 255.

    # Reshape labels
    labels = labels.reshape(m, 1)

    # Return values
    return images, labels, params

####################################################################################
# This function creates PNG images from histograms stored locally as well as 
# the 9 fit parameters found during a Root fit. After it creates the PNGs, it 
# converts them to numpy arrays of numbers, normalizes them, and returns them for
# the purpose of training or using neural networks to classify fits (good/bad).

def load_images_from_scratch():
    return 0

####################################################################################
# This function loads PNG images from file, converts them to numpy arrays of 
# numbers, inverts and normalizes them for the purpose of training nerual networks.

def load_images_from_file():
    return 0

####################################################################################
# This function loads from mysql the input values of the fit_pmt algorithm such as 
# high voltage, light level, parameter constraints, param initial guesses, etc.
# These values are used to train neural networks on how to use the fit algorithm.

def load_fit_inputs(): 
    return 0

####################################################################################
# This function loads from mysql the output values of the fit_pmt algorithm such as 
# gain error, chi squared, alpha, mu, alpha error, mu error, pedestal mean, etc.
# These values are used to train neural networks on good/bad fits

def load_fit_outputs():
    return 0

####################################################################################
# This function takes in 9 parameters from the fit_pmt 9-parameter fit algorithm 
# as well as a list of 4096 histogram bin contents (4096 integers) and from this
# creates a PNG image of a fit to a collection of data points.
#
# This png can then be used for display purposes or input into neural networks.

def make_image_from_numbers(parameters, histogram):
    return 0

####################################################################################
# Peronally defined factorial function (only works with integers) for fit_pmt

def my_factorial(n):
    value = 1
    while n > 1:
        value *= n
        n -= 1
    return value

####################################################################################
# Personally defined error function (integral of gaussian) for use with fit_pmt.

def my_erf(x):
    if x == 0:
        return 0
    
    sign = 1 if x > 0 else -1
    x = np.abs(x)

    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911

    t = 1.0 / (1.0 + p*x)
    y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t * np.exp(np.power(x, 2))
    return sign * y

####################################################################################
# Personally defined poisson distribution for use in the fit_pmt algorithm

def my_poisson(n, mu):
    return np.power(mu, n) * np.exp(-mu) / my_factorial(n)
####################################################################################
# This function defines the "pedestal" signal of a PMT which is the distribution
# we should see if we take data with the PMT on in complete darkness. This signal
# will be highly gaussian but will also exhibit some exponential decay off to the
# right due to the probability of a Type II discrete background event.
# Reference: NIM_A339_468_PMT_Calibration.pdf in docs folder

def fit_pmt_bg(x, w, q0, s0, alpha, inj_norm, real_norm):
    pois = np.exp(-alpha)
    term1 = np.power(x - q0, 2) / (2.0 * np.power(s0, 2))
    term2 = s0 * np.sqrt(np.pi * 2.0)
    gaus = np.exp(term1) / term2 

    if x >= q0:
        igne = alpha * np.exp(-alpha * (x - q0))
    else:
        igne = 0.0

    term1 = (1.0 - w) * gaus + w * igne
    real_pedestal = pois * real_norm * term1
    injected_pedestal = inj_norm * term1

    return real_pedestal + injected_pedestal
####################################################################################
# This function defines the distribution of signal sizes we would see from a PMT
# if exactly n photoelectrons were ejected at once from the photocathode. We use 
# this function for 1-PE, 2-PE, 3-PE, ..., 16-PE events (whichever are relevant to
# the data taken).
#
# The distribution modeled here is quite gaussian but also exhibits some exponential
# decay off to the right side due to discrete background events described in ref.
# Reference: NIM_A339_468_PMT_Calibration.pdf in docs folder

def fit_pmt_pe(x, w, q0, s0, alpha, mu, q1, s1, inj_norm, real_norm, n):
    qn = q0 + n * q1
    sn = np.sqrt(np.power(s0, 2) + n * np.power(s1, 2))
    
    term1 = x - qn - alpha * np.power(sn, 2)
    term2 = x - qn - alpha * np.power(sn, 2) / 2.0
    term3 = q0 - qn - alpha * np.power(sn, 2)
    term4 = np.sqrt(2) * sn

    sign = 1.0 if term1 > 0.0 else -1.0
    term1 = my_erf(np.abs(term3) / term4) + sign * my_erf(np.abs(term1) / term4)
    igne = alpha / 2.0 * np.exp(-alpha * term2) * term1

    term1 = 2.0 * np.power(sn, 2)
    term2 = -np.power(x - qn, 2) / term1
    term3 = np.sqrt(2.0 * np.pi) * sn
    gn = np.exp(term2) / term3

    term1 = (1.0 - w) * gn + w * igne
    return my_poisson(n, mu) * real_norm * term1

####################################################################################
# This function defines the fit_pmt fitting algorithm originally written by 
# Yuxiang Zhao. This function models low-light PMT output distribution INCLUDING
# injected pedestal events (taking data when we aren't flashing the light).
# 
# This is a 9-parameter fit that requires n_min and n_max arguments to know
# which regime to consider during fitting.
# Reference: NIM_A339_468_PMT_Calibration.pdf in docs folder

def fit_pmt(x, w, q0, s0, alpha, mu, q1, s1, inj_norm, real_norm, n_min, n_max):
    pe_sum = 0.0
    cur_pe = n_min
    # Calculate the contributions from each PE in consideration
    for n in range(n_min, n_max + 1):
        pe_sum += fit_pmt_pe(x, w, q0, s0, alpha, mu, q1, s1, inj_norm, real_norm, n)
    # Return PE distribution plus pedestal distribution
    return pe_sum + fit_pmt_bg(x, w, q0, s0, alpha, inj_norm, real_norm)
####################################################################################

