########
# Creating satellite buffers from timeline
#########

import numpy as np
import pandas as pd
import time

def divisionbyzeroiszero(n, d):
    return n / d if d else 0

def find_least_connected(data_vol_delivered_allsources, target_names, total_data_delivered):
    """
    Function to find the least connected source
    and the volume from that source
    """
    least_connected_source = None   # set as empty to start
    data_vol_least_connected = total_data_delivered # set starting guess as the total of all collected data
    
    for source in target_names:         # for each source
        data_from_source = data_vol_delivered_allsources[source]
        if data_from_source < data_vol_least_connected:     # if the data collected from this source is less than the current reference
            data_vol_least_connected = data_from_source     # update the reference for the least connected data volume
            least_connected_source = source                 # update the least connected source
            pass
        pass
    return least_connected_source, data_vol_least_connected

def load_gstation_selection(gstation_filename, gstation_selection, num_gstations):
    """
    loads in gstation lists from excel file using pandas
    from: https://stackoverflow.com/questions/45708626/read-data-in-excel-column-into-python-list
    """
    df = pd.read_excel(gstation_filename + '.xlsx', sheet_name = str(num_gstations)) # can also index sheet by name or fetch all sheets
    gstation_list = df[gstation_selection].tolist()
    return gstation_list

def find_oldest_data(data_buffer, target_names, expiry, current_timestep):
    """
    Function to find the oldest data in the data buffer dictionary
    that has not already exceeded the expiry time.
    Returns ID of data in dictionary and age of data
    """
    # set these as 0 to start
    oldest_data_source = 0
    oldest_data_time = 0
    
    for source in target_names:                # loop over each holder in the data dictionary
        if data_buffer[source]:    # if the holder is empty (i.e. == None) then skip
            age_of_data = current_timestep - data_buffer[source]   # calculate age of data as current time - collection time
            if age_of_data > oldest_data_time and age_of_data < expiry:     # if it's older than the current reference AND not older than 60 mins
                oldest_data_time = age_of_data      # update the reference time
                oldest_data_source = source         # update the oldest data ID
            pass
        pass
    return oldest_data_source, oldest_data_time


start_time = time.time()
files_name = "spire_final_test"

timeline_path = "Timeline files\\"                       # define path to save results                                    
results_path = "Performance Files\\"                       # define path to save results   
adj_matrix_path = "Adjacency Matrices\\"                                  

# number of days simulated
num_days = 100
#set timestep length in seconds
time_step_length = 30
#number of timesteps to consider
num_timesteps = int(num_days * 24 * 60 * 60 / time_step_length)

# set data expiry time
max_expiry_hours = 1
max_expiry = 60 * 60 * max_expiry_hours

# set list of gstations
gstation_filename = "Data\\GS_selections"      # file containing the lists of gstations
gstation_selection = 'consensus' # 'max flow' # 'consensus'  # selection method set to use: corresponds to column heading
num_gstations_list = [1, 5, 10, 15, 20, 25, 30]    # corresponds to sheet in excel file


"""
SET Satellites
"""
num_sats = 84


"""
SET TARGETS
"""
# all targets
target_subset = range(1,251)

# set names of each ground station
target_names = ["Source " + str(i) for i in target_subset]  


"""
SET ALL GSTATIONS LIST
"""
gstations_names_full = ["Gstation " + str(i) for i in range(1,78)]

# load in list of number os sats in view of each ground station at each time step
sats_in_view = np.load(timeline_path + 'sats_in_view_' + files_name + '.npy')

"""
MAIN LOOP: ANALYSIS
"""
# loop over ground stations
for num_gstations in num_gstations_list[0:]: 
    case_name = gstation_selection + '_' + str(num_gstations) + 'gstation_expiry_' + str(max_expiry_hours) + 'hrs'

    # set names of each ground station
    gstation_subset = load_gstation_selection(gstation_filename, gstation_selection, num_gstations)
    gstations_names = ["Gstation " + str(i) for i in gstation_subset]                                                                           # set names using selected list

    # to analyse performance from timeline
    data_vol_delivered_allsats = { "Sat " + str(i) : 0 for i in range(0,num_sats)}  # dictionary size of all sats
    data_vol_delivered_allgstations = { i : 0 for i in gstations_names} # dictionary of all ground stations
    data_vol_delivered_allsources = { i : 0 for i in target_names}  # dictionary of all sources
    delay_allsats = { "Sat " + str(i) : 0 for i in range(0,num_sats)}  # dictionary of all sats
    delay_allsats_mins = { "Sat " + str(i) : 0 for i in range(0,num_sats)}  # dictionary of all sats
    delay_allsats_alldata = []

    # Analyse timeline for each satellite we are interested in in this case:
    for sat_number in range(0,num_sats):
        timeline = np.load(timeline_path + 'timeline_sat_' + str(sat_number) + '_' + files_name + '.npy', allow_pickle = True)
        
        """
        Do "data routing"
        """
        # create dictionary to hold time of data collection with one key for each target
        data_buffer = { i : None for i in target_names}   # set as None when "empty"
        delivered_data = []         # holder for data delievered to the ground

        time_step_count = 0
        downlink_count = 0          # counter that increments by 1/(number of sats in view of gstation) at each step a gstation is in view. downlink occurs once it's >= 1
        for time_step in timeline[0:num_timesteps]:
            if len(time_step) > 1:         # if has more than one entry, and therefore something is in view
                for sight in time_step[1:]:     # skip timestamp
                    if sight[1] == 'source' and sight[2] in target_names:    # if it's a source and is in this analysis and it hasn't just been see by the same satellite
                        data_buffer[sight[2]] = sight[0]                    # store collection time in dictionary overwriting previous entry
                    elif sight[1] == 'sink' and sight[2] in gstations_names:    # if it's a sink and is in this analysis
                        # the below allows for the sats in view to be accounted for 
                        downlink_count += 1/(sats_in_view[gstations_names_full.index(sight[2])][time_step_count])   # increments by 1/(number of sats in view of gstation) at each step a gstation is in view.
                        if downlink_count >= 1:
                            # check which data to downlink
                            data_to_move, delay = find_oldest_data(data_buffer, target_names, max_expiry, time_step[0])
                            # data_to_move will be zero if the buffer is empty
                            if data_to_move != 0:                        
                                delivered_data.append({'target' : data_to_move, 'gstation' : sight[2], 'delay' : delay})   # add downlinked data to list as dictionary with target ID and delay time
                                data_buffer[data_to_move] = None      # clear target holder in buffer so data won't be downlinked again
                                downlink_count -= 1            # take 1 from the downlink counter
        
            time_step_count += 1

        np.save(results_path + "Delivered_data_" + str(case_name) + "_sat_" + str(sat_number) + "_" + str(num_days) + "days", delivered_data)

    
    