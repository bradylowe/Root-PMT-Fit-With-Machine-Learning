import numpy as np
import glob
from scipy import misc
from PIL import Image

####################################################################################

def get_label_from_filename(filename):
    return int(filename[len(filename) - 5])

####################################################################################

def load_dataset(m=-1, return_filenames=False, im_dir="train"):
    
    # DEFINE IMAGE DIMENSIONS
    wpx, hpx = 87 * 4, 59 * 4
    
    # INITIALIZE STORAGE
    images = []
    labels = []
    filenames = []

    # Loop over all images in directory (up to m)
    for image_path in glob.glob("images/" + im_dir + "/*.png"):
        # Save the filename
        filenames.append(image_path)
        # Read in image to array
        cur_png = misc.imread(image_path)
        # Reduce resolution and append to list
        images.append(misc.imresize(cur_png, (hpx, wpx)))
        # Grab the label off the end of the filename
        labels.append(get_label_from_filename(image_path))
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
    new_name = filename[0:len(filename) - 5]
    # Append new label and .png
    new_label = 1 - get_label_from_filename(filename)
    new_name += str(new_label) + ".png"
    # Change the filename
    os.rename(filename, new_name)


