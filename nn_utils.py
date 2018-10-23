# Load dependencies
import numpy as np
from scipy import misc

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
# This function loads all the information available about the labeled Root fits from
# a local text file called no_sql_params.txt for those that would like to try out 
# the network but don't want to bother with sql. Images are loaded from the local 
# "images" directory.

def load_dataset_no_sql(m=-1, dataset="train"):

    # DEFINE IMAGE DIMENSIONS
    scale = 4
    wpx, hpx = 87 * scale, 59 * scale

    # In a loop, grab all the avaiable fit data from the no_sql_params.txt file.
    # In this file, we will grab filenames of pngs as well as labels for the data. 
    # We store all the information in lists which must be initialized before looping.
    linear_plots = []
    log_plots = []
    labels = []
    in_params = []
    out_params = []
    infile = open("no_sql_params.txt", "r")
    contents = infile.readlines()
    # Start the loop index at 1 because first line in the file is empty
    ii = 1
    while ii < len(contents):
        # Grab the run_params and fit_results into vectors
        run_params = contents[ii].split()
        fit_results = contents[ii + 1].split()
        # Check the run_id to see which dataset this run is in
        run_id = int(run_params[0])
        # Check which dataset this run falls in. Only load the requested ones
        # For dev, fit_id % 10 == 0
        # For test, fit_id % 10 == 1
        if (dataset == "train" and run_id % 10 < 2):
            ii += 3
            continue
        if (dataset == "dev" and run_id % 10 != 0):
            ii += 3
            continue
        if (dataset == "test" and run_id % 10 != 1):
            ii += 3
            continue
        # Split up into input and output parameters
        fit_in = [int(run_params[6]), int(run_params[9]), int(run_params[10]), int(run_params[8]), int(run_params[11]), int(run_params[12]), int(fit_results[2]), int(fit_results[3]), int(fit_results[4]), int(fit_results[5]), int(fit_results[6]), float(fit_results[7]), float(fit_results[8]), float(fit_results[9]), float(fit_results[10]), float(fit_results[11]), float(fit_results[12]), float(fit_results[13]), float(fit_results[14]), float(fit_results[15]), float(fit_results[16]), float(fit_results[17]), float(fit_results[18]), float(fit_results[19]), float(fit_results[20]), float(fit_results[21]), float(fit_results[22]), float(fit_results[23]), float(fit_results[24]), float(fit_results[25]), float(fit_results[26]), float(fit_results[27]), float(fit_results[28]), float(fit_results[29]), float(fit_results[30]), float(fit_results[31]), float(fit_results[32]), float(fit_results[33])]
        fit_out = [float(fit_results[34]), float(fit_results[35]), float(fit_results[36]), float(fit_results[37]), float(fit_results[38]), float(fit_results[40]), float(fit_results[41]), float(fit_results[42]), float(fit_results[43]), float(fit_results[44]), float(fit_results[45]), float(fit_results[46]), float(fit_results[47]), float(fit_results[49]), float(fit_results[50]), float(fit_results[51]), float(fit_results[52]), float(fit_results[53]), float(fit_results[54]), float(fit_results[55])]
        # Append parameters of this fit to our lists
        in_params.append(fit_in)
        out_params.append(fit_out)
        # Grab label
        label = int(fit_results[58])
        labels.append(label)
        # Grab image from filename, append the source dir, and make log filename
        linear_filename = fit_results[57]
        linear_filename = 'images/' + linear_filename
        log_filename = linear_filename.replace("log0", "log1")
        # Read in image to array, reduce resolution and append
        cur_png = misc.imread(linear_filename)
        linear_plots.append(misc.imresize(cur_png, (hpx, wpx)))
        cur_png = misc.imread(log_filename)
        log_plots.append(misc.imresize(cur_png, (hpx, wpx)))
        # Iterate to next fit in list (next 3 lines)
        ii += 3
        # Exit the loop if we hit the limit
        if m != -1 and len(labels) >= m:
            break

    # Convert all gathered info into arrays
    linear_plots = np.asarray(linear_plots)
    log_plots = np.asarray(log_plots)
    labels = np.asarray(labels)
    in_params = np.asarray(in_params)
    out_params = np.asarray(out_params)
    # Find out how many images were loaded
    m = linear_plots.shape[0]
    # Invert and normalize images
    linear_plots = (255. - linear_plots) / 255.
    log_plots = (255. - log_plots) / 255.
    # Reshape labels
    labels = labels.reshape(m, 1)
    # Return values
    return linear_plots, log_plots, in_params, out_params, labels


####################################################################################
# This function takes in either "train", "dev", or "test" and returns a mysql query
# conditional statement to use for selecting images of the corresponding type.

def get_dataset_condition(dataset):
    # Define condition for selecting train, dev, test set.
    # For dev, fit_id % 10 == 0
    # For test, fit_id % 10 == 1
    if (dataset == "train"):
        return "MOD(run_id, 10) > 1"
    elif (dataset == "dev"):
        return "MOD(run_id, 10) = 0"
    elif (dataset == "test"):
        return "MOD(run_id, 10) = 1"
    elif (dataset == "all"):
        return "TRUE"
    else:
        return "FALSE"

####################################################################################
# This function loads PNG images from file, converts them to numpy arrays of 
# numbers, inverts and normalizes them for the purpose of training nerual networks.

def load_images(m=-1, dataset="train", max_label=1, log_scale=False, im_path=""):
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
    query = "SELECT CONCAT('" + im_path + "', nn_png) FROM fit_results "
    query += " WHERE nn_png IS NOT NULL AND label IS NOT NULL AND label<=" + str(max_label)
    query += " AND " + get_dataset_condition(dataset) + " ORDER BY fit_id;"
    data.execute(query)

    # Grab pngs from file, create lists
    images = []
    for filename in data:
        filename = filename[0]
        # Change the filename if log plot
        if log_scale:
            filename = filename.replace("log0", "log1")
        # Read in image to array
        cur_png = misc.imread(filename)
        # Reduce resolution and append to list
        images.append(misc.imresize(cur_png, (hpx, wpx)))
        # Exit the loop if we hit the limit
        if m != -1 and len(images) >= m:
            break

    # Convert into array
    images = np.asarray(images)
    m = images.shape[0]
    # Invert and normalize images
    images = (255. - images) / 255.
    # Return
    return images

####################################################################################
# This function loads from mysql the input values of the fit_pmt algorithm such as 
# high voltage, light level, parameter constraints, param initial guesses, etc.
# These values are used to train neural networks on how to use the fit algorithm.

def load_fit_results(m=-1, dataset="train", max_label=1, using_pngs=True): 
    # Connect to mysql database twice for two queries
    import mysql.connector
    run_params = mysql.connector.connect(
        host='localhost', user='brady',
        password='thesis', database='gaindb'
    )
    fit_results = mysql.connector.connect(
        host='localhost', user='brady',
        password='thesis', database='gaindb'
    )
    rp_cursor = run_params.cursor()
    fr_cursor = fit_results.cursor()

    # Query database
    query = "SELECT * FROM fit_results WHERE label IS NOT NULL"
    query += " AND label<=" + str(max_label)
    query += " AND " + get_dataset_condition(dataset)
    if using_pngs:
        query += " AND nn_png IS NOT NULL"
    query += " ORDER BY fit_id;"
    fr_cursor.execute(query)
    # Initialize lists
    fit_inputs = []
    fit_outputs = []

    # Loop through results, fill lists
    for (_, run_id, fit_engine, fit_low, fit_high, min_pe, max_pe, w_0, ped_0, ped_rms_0, alpha_0, mu_0, sig_0, sig_rms_0, inj_0, real_0, w_min, ped_min, ped_rms_min, alpha_min, mu_min, sig_min, sig_rms_min, inj_min, real_min, w_max, ped_max, ped_rms_max, alpha_max, mu_max, sig_max, sig_rms_max, inj_max, real_max, w_out, ped_out, ped_rms_out, alpha_out, mu_out, sig_out, sig_rms_out, inj_out, real_out, w_out_error, ped_out_error, ped_rms_out_error, alpha_out_error, mu_out_error, sig_out_error, sig_rms_out_error, inj_out_error, real_out_error, chi, gain, gain_error, gain_percent_error, _, _, _) in fr_cursor:
        # Get additional information for this fit
        rp_cursor.execute("SELECT pmt, datarate, pedrate, hv, ll, filter FROM run_params WHERE run_id=" + str(run_id) + ";")
        for (pmt, datarate, pedrate, hv, ll, filtr) in rp_cursor:
            # Put together list of all inputs into fit algorithm
            fit_in = [pmt, datarate, pedrate, hv, ll, filtr, fit_engine, fit_low, fit_high, min_pe, max_pe, w_0, ped_0, ped_rms_0, alpha_0, mu_0, sig_0, sig_rms_0, inj_0, real_0, w_min, ped_min, ped_rms_min, alpha_min, mu_min, sig_min, sig_rms_min, inj_min, real_min, w_max, ped_max, ped_rms_max, alpha_max, mu_max, sig_max, sig_rms_max, inj_max, real_max]
            fit_inputs.append(fit_in)
            # Put together list of all outputs from fit algorithm
            fit_out = [w_out, ped_out, ped_rms_out, alpha_out, mu_out, sig_rms_out, inj_out, real_out, w_out_error, ped_out_error, ped_rms_out_error, alpha_out_error, mu_out_error, sig_rms_out_error, inj_out_error, real_out_error, chi, gain, gain_error, gain_percent_error]
            fit_outputs.append(fit_out)
            # Just do one
            break
        # Exit the loop if we hit the limit
        if m != -1 and len(fit_outputs) >= m:
            break

    # Convert into numpy arrays and reshape
    fit_inputs = np.asarray(fit_inputs)
    fit_outputs = np.asarray(fit_outputs)
    m = len(fit_inputs)
    fit_inputs = fit_inputs.reshape(m, -1)
    fit_outputs = fit_outputs.reshape(m, -1)

    # Return
    return fit_inputs, fit_outputs


####################################################################################
# This function loads from mysql the input values of the fit_pmt algorithm such as 
# high voltage, light level, parameter constraints, param initial guesses, etc.
# These values are used to train neural networks on how to use the fit algorithm.

def load_labels(m=-1, dataset="train", max_label=1, using_pngs=True): 
    # Connect to mysql database
    import mysql.connector
    gaindb = mysql.connector.connect(
        host='localhost', user='brady',
        password='thesis', database='gaindb'
    )

    # Query database
    query = "SELECT label FROM fit_results WHERE label IS NOT NULL"
    if using_pngs:
        query += " AND nn_png IS NOT NULL"
    query += " AND label<=" + str(max_label)
    query += " AND " + get_dataset_condition(dataset)
    query += " ORDER BY fit_id;"
    fit_results = gaindb.cursor()
    fit_results.execute(query)
    
    # Put values in array and return
    labels = []
    for label in fit_results:
        labels.append(int(label[0]))
        # Exit the loop if we hit the limit
        if m != -1 and len(labels) >= m:
            break

    # Convert into array
    labels = np.asarray(labels)
    m = labels.shape[0]
    labels = labels.reshape(m, 1)

    return labels


