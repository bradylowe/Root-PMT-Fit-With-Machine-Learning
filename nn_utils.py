import numpy as np
import glob
from pathlib import Path
from scipy import misc
from PIL import Image

####################################################################################

def get_printable_image(this_image):
    this_image = 255 - this_image * 255
    this_image = misc.toimage(this_image)
    return this_image

####################################################################################

def get_stats(train_x, train_y, test_x = '', test_y = ''):
    # Calculate predictions
    predictions = conv_model.predict(x=train_x)
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
    predictions = conv_model.predict(x=test_x)
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

def get_wrong_answers(x, y):
    # Calculate predictions
    predictions = conv_model.predict(x)
    predictions = np.floor(predictions + 0.5)
    # Get vector mask for good and bad fits and right and wrong answers
    good_fits = y
    wrong_answers = np.abs(np.subtract(predictions, good_fits))
    # Make list of bad answers
    bad_list = []
    for i in range(len(y)):
        if wrong_answers[i] == 1:
            bad_list.append(i)
    # Return list
    return bad_list

####################################################################################

import os
def change_label(filename):
    # Get rid of old label and .png extension
    new_name = filename[0:-5]
    # Append new label and .png
    new_label = 1 - int(filename[-5])
    new_name += str(new_label) + ".png"
    # Change the filename
    os.rename(filename, new_name)
    # Store this label in file
    fitID = filename[filename.find("fitID"):]
    fitID = fitID[0:fitID.find("_")]
    with open('classified.txt', 'a') as f:
        f.write(fitID + " " + str(new_label) + "\r\n")

####################################################################################

def classify_image(filename, prediction):
    # Look for existing prediction
    if filename.find("predict") > 0:
        # Remove prediction and .png
        new_name = filename[0:-13]
    else:
        # Remove .png
        new_name = filename[0:-4]
    # Append new prediction and .png
    new_name += "_predict" + str(int(prediction)) + ".png"
    # Change the filename
    os.rename(filename, new_name)
    # Store this label in file
    fitID = new_name[new_name.find("fitID"):]
    fitID = fitID[0:fitID.find("_")]
    with open('classified.txt', 'a') as f:
        f.write(fitID + " " + str(int(prediction)) + "\r\n")

####################################################################################

def round(num):
    return int(num + 0.5)

####################################################################################

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

# This function will display images on screen
def print_mislabeled_images(X, Y, predictions):
    # get size of image
    w, h = 696 / 2, 472 / 2
    # loop over all training examples
    for itr in range(X.shape[1]):
        if (Y[0, itr] != predictions[0, itr]):
            # do ten images at a time
            if (itr % 10 == 0):
                raw_input("Press enter to show next 10 images")
            # get image
            data = X[:,itr].reshape(h, w, 3)
            # uninvert and unscale
            data = 255 - (data * 255)
            img = Image.fromarray(data, 'RGB')
            img.show()

####################################################################################

def print_good_images(X, predictions, fnames):
    # get size of image
    w, h = 696 / 2, 472 / 2
    # loop over all training examples
    for itr in range(predictions.shape[1]):
        if (predictions[0, itr] == 1):
            # get image
            data = X[:,itr].reshape(h, w, 3)
            # uninvert and unscale
            data = 255 - (data * 255)
            img = Image.fromarray(data, 'RGB')
            img.show()
            # do one image at a time
            raw_input(fnames[itr])

####################################################################################

def print_bad_images(X, predictions, fnames):
    # get size of image
    w, h = 696 / 2, 472 / 2
    # loop over all training examples
    for itr in range(predictions.shape[1]):
        if (predictions[0, itr] == 0):
            # get image
            data = X[:,itr].reshape(h, w, 3)
            # uninvert and unscale
            data = 255 - (data * 255)
            img = Image.fromarray(data, 'RGB')
            img.show()
            # do one image at a time
            raw_input(fnames[itr])

####################################################################################

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
    scale = 8
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

def load_images_from_scratch():
    return 0
####################################################################################

def load_images_from_file():
    return 0
####################################################################################

def load_fit_inputs(): 
    return 0
####################################################################################

def load_fit_outputs():
    return 0
####################################################################################

def make_image_from_numbers(parameters, histogram):
    return 0
####################################################################################

