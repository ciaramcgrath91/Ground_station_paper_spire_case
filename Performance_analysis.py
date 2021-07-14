
#################
# Post-processing all sat data buffers
#################

import numpy as np
import pandas as pd
import time


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

# load in list of number os sats in view of each ground station at each time step
sats_in_view = np.load(timeline_path + 'sats_in_view_' + files_name + '.npy')

# set data expiry time
max_expiry_hours = 1

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
    
    
    ######
    # DELIVERED DATA
    ######

    # do for individual sats so don't overload memory
    for sat_number in range(0,num_sats):
        delivered_data = np.load(results_path + "Delivered_data_" + str(case_name) + "_sat_" + str(sat_number) + "_" + str(num_days) + "days.npy", allow_pickle = True).tolist()
        data_vol_delivered_allsats["Sat " + str(sat_number)] = (len(delivered_data))       # get number of delivered packets for each satellite)
    
        # calculate data volume delivered for each ground station
        for name in gstations_names:                                            # for each ground station
            data_down_station = len([i for i in delivered_data if i['gstation'] == name])         # calculate the volume of data downlinked to the ground stations in question and add it to the total
            data_vol_delivered_allgstations[name] += data_down_station                  # add on data downlinked by each sat to each gstation -- pull gstation name from 'name' variables

        # calculate data volume delivered for each source
        for name in target_names:                                            # for each source
            data_down_tar = len([i for i in delivered_data if i['target'] == name])     # calculate the volume of data downlinked that came from the source in question and add it to the total      
            data_vol_delivered_allsources[name] += data_down_tar                  # add on data delivered by each sat from each source -- pull name from 'name' variable

        # calculate average delay for each satellite
        if delivered_data == []:    # if no delivered data
            delay_allsats["Sat " + str(sat_number)] = None
            delay_allsats_mins["Sat " + str(sat_number)] = None
        else:
            delay_allsats["Sat " + str(sat_number)] = sum([i['delay'] for i in delivered_data])/len(delivered_data)              # get average of all delays
            delay_allsats_mins["Sat " + str(sat_number)] = (sum([i['delay'] for i in delivered_data])/len(delivered_data))/60              # get average of all delays

    # total values
    data_vol_total = sum([data_vol_delivered_allsats["Sat " + str(i)] for i in range(0,num_sats)])  # total data delivered by all satellites combined
    # total delay is average of all delays, for all satellites that have a delay value
    delay_total = sum([delay_allsats["Sat " + str(i)] for i in range(0,num_sats) if delay_allsats["Sat " + str(i)]])/len([delay_allsats["Sat " + str(i)] for i in range(0,num_sats) if delay_allsats["Sat " + str(i)]])
    delay_average_mins = delay_total/60


    # find worst connected source and volume of data from least connected source
    least_connected_source, data_vol_least_connected = find_least_connected(data_vol_delivered_allsources, target_names, data_vol_total)
    
    # Save results
    file1 = open(results_path + 'Performance_' + str(case_name) + '_' + str(num_days) +'_days.txt',"w")
    file1.write("\nData volume delivered: " + str(data_vol_total) + "\nData volume delivered by satellite: " + str(data_vol_delivered_allsats) + "\nData volume per ground station: " + str(data_vol_delivered_allgstations) + "\nData volume downlinked per source: " + str(data_vol_delivered_allsources) + "\nMinimum data volume from a source: " + str(data_vol_least_connected) + " at source: " + str(least_connected_source) + " \nAverage delay: " + str(delay_average_mins) + " mins.  \nDelay by satelite: " + str(delay_allsats_mins))
    file1.close()

end_time = time.time()
runtime = (end_time - start_time)
print("Runtime: %s seconds" % runtime)