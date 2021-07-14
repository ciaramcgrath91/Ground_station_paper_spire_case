import numpy as np
import pandas as pd
import time

start_time = time.time()
case_name = "spire_final_test"
file_location = "Timeline Files\\"
results_location = "Adjacency Matrices\\"


# define number of sources, satellites and sinks
num_sources = 250                                           
num_sats = 84
num_gstations = 77
# number of days simulated
num_days = 100

#set timestep length in seconds
time_step_length = 30
#number of timesteps to consider
num_timesteps = int(num_days * 24 * 60 * 60 / time_step_length)

# matrix size is number of sources + satellites + sinks along rows and columns
num_matrix_elements = num_sources + num_sats + num_gstations

# set up adjacency
adjacency_matrix_basic = np.zeros((num_matrix_elements, num_matrix_elements))
adjacency_matrix_no_duplicates = np.zeros((num_matrix_elements, num_matrix_elements))

# load sats_in_view matrix
sats_in_view = np.load(file_location + "sats_in_view_" + case_name + ".npy")


# to create adjacency matrix
for sat_number in range(0,num_sats):
    timeline = np.load(file_location + 'timeline_sat_' + str(sat_number) + '_' + case_name + '.npy', allow_pickle = True)
    timestep_number = 0                                      # set timestep to count from 0 for new satellite
    for step in timeline:                                    # for each step in the timeline
        for element in step[1:]:                                    # for each item seen in this time step
            if element[1] == 'sink':                                # if the item seen is a ground station
                gstation_number_temp = int(element[2][9:])          # pull out the ground station number
                # add the time step length to the weighting at the element row = satellite, column = ground station
                adjacency_matrix_basic[num_sources + sat_number, num_sources + num_sats + gstation_number_temp - 1] += time_step_length
                adjacency_matrix_no_duplicates[num_sources + sat_number, num_sources + num_sats + gstation_number_temp - 1] += (time_step_length / sats_in_view[gstation_number_temp - 1, timestep_number])
            elif element[1] == 'source':
                target_number_temp = int(element[2][6:])          # pull out the ground station number
                # add the time step length to the weighting at the element row = satellite, column = ground station
                adjacency_matrix_basic[target_number_temp -1, num_sources + sat_number] += time_step_length
                adjacency_matrix_no_duplicates[target_number_temp -1, num_sources + sat_number] += time_step_length


        timestep_number += 1                                        # increment timestep

adjacency_matrix_basic_norm = adjacency_matrix_basic / num_days
adjacency_matrix_no_duplicates_norm = adjacency_matrix_no_duplicates / num_days

# save adjacency matrices
data_frame_temp = pd.DataFrame(adjacency_matrix_basic)                          # convert to data frame using pandas
data_frame_temp.to_csv(results_location + 'adj_matrix_basic_' + case_name + '.csv', index=False, header= None)   # save as csv file          
data_frame_temp = pd.DataFrame(adjacency_matrix_basic_norm)                          # convert to data frame using pandas
data_frame_temp.to_csv(results_location + 'adj_matrix_basic_norm_' + case_name + '.csv', index=False, header= None)   # save as csv file          
data_frame_temp = pd.DataFrame(adjacency_matrix_no_duplicates)                  # convert to data frame using pandas
data_frame_temp.to_csv(results_location + 'adj_matrix_no_duplicates_' + case_name + '.csv', index=False, header= None)   # save as csv file          
data_frame_temp = pd.DataFrame(adjacency_matrix_no_duplicates_norm)                  # convert to data frame using pandas
data_frame_temp.to_csv(results_location + 'adj_matrix_no_duplicates_norm_' + case_name + '.csv', index=False, header= None)   # save as csv file          



end_time = time.time()
runtime = (end_time - start_time)
print("Runtime: %s seconds" % runtime)