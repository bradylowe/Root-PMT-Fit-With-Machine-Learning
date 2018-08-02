import numpy as np
import glob
from scipy import misc
from PIL import Image

def load_dataset(samples=-1, shuffle=False, return_filenames=False):
    
    # Define training and testing data sizes
    if samples != -1:
        m_total = samples
        m_train = int(m_total * 0.8)
        m_test = m_total - m_train
    
    # DEFINE IMAGE DIMENSIONS
    wpx, hpx = 87 * 4, 59 * 4
    
    # INITIALIZE STORAGE
    train_pngs = []
    test_pngs = []
    train_labels = []
    test_labels = []
    train_filenames = []
    test_filenames = []

    # Loop over all images in directory (up to m_train)
    for image_path in glob.glob("images/train/*.png"):
        # Save the filename
        train_filenames.append(image_path)
        # Read in image to array
        cur_png = misc.imread(image_path)
        # Resize image and append to list
        train_pngs.append(misc.imresize(cur_png, (hpx, wpx)))
        # Grab the label off the end of the filename
        train_labels.append(int(image_path[len(image_path) - 5]))
        # Exit the loop if we hit the limit
        if samples != -1 and len(train_labels) >= m_train:
            break

    # Loop over all images in directory (up to m_test)
    for image_path in glob.glob("images/dev/*.png"):
        # Save the filename
        test_filenames.append(image_path)
        # Read in image
        cur_png = misc.imread(image_path)
        # Resize image and append to list
        test_pngs.append(misc.imresize(cur_png, (hpx, wpx)))
        # Grab the label off the end of the filename
        test_labels.append(int(image_path[len(image_path) - 5]))
        # Exit the loop if we hit the limit
        if samples != -1 and len(test_labels) >= m_test:
            break

    # Convert all gathered info into arrays
    train_x = np.asarray(train_pngs)
    test_x = np.asarray(test_pngs)
    train_y = np.asarray(train_labels)
    test_y = np.asarray(test_labels)
    
    # Find out how many images were loaded
    m_train = train_x.shape[0]
    m_test = test_x.shape[0]

    # Invert and normalize images
    train_x = (255. - train_x) / 255.
    test_x = (255. - test_x) / 255.
    
    # Reshape labels
    train_y = train_y.reshape(train_y.shape[0], 1)
    test_y = test_y.reshape(test_y.shape[0], 1)

    # Shuffle
    if (shuffle):
        idx = np.random.permutation(m_train)
        train_x = train_x[idx]
        train_y = train_y[idx]
        train_filenames = train_filenames[idx]
        
    if return_filenames:
        return train_x, train_y, train_filenames, test_x, test_y, test_filenames
    else:
        return train_x, train_y, test_x, test_y

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

def get_printable_image(this_image):
    this_image = 255 - this_image * 255
    this_image = misc.toimage(this_image)
    return this_image


