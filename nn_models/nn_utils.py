import numpy as np
import glob
from pathlib import Path
from scipy import misc
from PIL import Image

####################################################################################

def load_dataset(m=-1, return_filenames=False, im_dir="train", log=False):
    # DEFINE IMAGE DIMENSIONS
    scale = 4
    wpx, hpx = 87 * scale, 59 * scale

    # INITIALIZE STORAGE
    images = []
    labels = []
    filenames = []

    # Loop over all images in directory (up to m)
    path = "*images/*" + im_dir + "/*"
    for image_path in glob.glob(path):
        # Change the filename if log plot
        if log:
            image_path = image_path.replace("log0", "log1")
        # Save the filename
        filenames.append(image_path)
        # Read in image to array
        cur_png = misc.imread(image_path)
        # Reduce resolution and append to list
        images.append(misc.imresize(cur_png, (hpx, wpx)))
        # Grab the label off the end of the filename
        labels.append(int(image_path[-5]))
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

def get_mini_batches(X, Y, size, seed):
    np.random.seed(seed)
    m = X.shape[0]
    n_batches = int(m / size)
    batches = []
    # LOOP OVER FULL BATCHES
    for i in range(n_batches):
        cur_x = X[i * size : (i + 1) * size]
        cur_y = Y[i * size : (i + 1) * size]
        cur_batch = (cur_x, cur_y)
        batches.append(cur_batch)
    # GET LAST BATCH IF EXTRA
    if (m % size > 0):
        cur_x = X[n_batches * size :]
        cur_y = Y[n_batches * size :]
        cur_batch = (cur_x, cur_y)
        batches.append(cur_batch)

    return batches

####################################################################################

def random_mini_batches(X, Y, batch_size, seed):
    np.random.seed(seed)
    m = X.shape[0]
    n_batches = int(m / batch_size)
    batches = []

    # Shuffle
    idx = np.random.permutation(m)
    X, Y = X[idx], Y[idx]

    # LOOP OVER FULL BATCHES
    for i in range(n_batches):
        cur_x = X[i * batch_size : (i + 1) * batch_size]
        cur_y = Y[i * batch_size : (i + 1) * batch_size]
        cur_batch = (cur_x, cur_y)
        batches.append(cur_batch)
    # GET LAST BATCH IF EXTRA
    if (m % size > 0):
        cur_x = X[n_batches * batch_size :]
        cur_y = Y[n_batches * batch_size :]
        cur_batch = (cur_x, cur_y)
        batches.append(cur_batch)

    return batches

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

def load_dataset_mysql(m=-1, return_filenames=False, im_dir="train", log=False):

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

def load_dataset_mysql_chi(m=-1, return_filenames=False, im_dir="train", log=False):

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
    data.execute("SELECT nn_png, label, chi FROM fit_results WHERE nn_png IS NOT NULL AND label IS NOT NULL AND label<2 AND " + im_dir)

    # Grab pngs from file, create lists
    images = []
    labels = []
    filenames = []
    chis=[]
    for (filename, label, chi) in data:
        # Change the filename if log plot
        if log:
            filename = filename.replace("log0", "log1")
        # Save the filename
        filenames.append(filename)
        # Read in image to array
        cur_png = misc.imread(filename)
        # Reduce resolution and append to list
        images.append(misc.imresize(cur_png, (hpx, wpx)))
        # Append other values to their lists
        labels.append(label)
        chis.append(chi)
	
        # Exit the loop if we hit the limit
        if m != -1 and len(labels) >= m:
            break

    # Convert all gathered info into arrays
    images = np.asarray(images)
    labels = np.asarray(labels)
    chis = np.asarray(chis)

    # Find out how many images were loaded
    m = images.shape[0]

    # Invert and normalize images
    images = (255. - images) / 255.

    # Reshape labels
    labels = labels.reshape(labels.shape[0], 1)
    chis = chis.reshape(chis.shape[0], 1)

    # Return values
    if return_filenames:
        return images, labels, chis, filenames
    else:
        return images, labels, chis

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

