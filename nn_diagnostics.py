import numpy as np
import glob
from scipy import misc
from PIL import Image

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

def list_good_images(predictions, fnames):
    # loop over all training examples
    for itr in range(predictions.shape[1]):
        if (predictions[0, itr] == 1):
            print(fnames[itr])

def list_bad_images(predictions, fnames):
    # loop over all training examples
    for itr in range(predictions.shape[1]):
        if (predictions[0, itr] == 0):
            print(fnames[itr])

def list_mislabeled_images(Y, predictions, fnames):
    # loop over all training examples
    for itr in range(predictions.shape[1]):
        if (predictions[0, itr] != Y[0, itr]):
            print(fnames[itr])

def get_n_correct(Y, predictions):
    n_total = predictions.shape[1]
    wrong_answers = np.abs(Y - predictions)
    n_wrong = np.sum(wrong_answers)
    return n_total - n_wrong


