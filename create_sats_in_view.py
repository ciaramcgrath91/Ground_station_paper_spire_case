############
# CREATING SATS IN VIEW ARRAY
############

import numpy as np
import pandas as pd
import time

def divisionbyzeroiszero(n, d):
    return n / d if d else 0



start_time = time.time()
case_name = "spire_final_test"

timeline_path = "Timeline Files\\"                       # define path to load timelines                                    
results_path = "Timeline Files\\"                       # define path to save outputs                                    


# number of days simulated
num_days = 100
#set timestep length in seconds
time_step_length = 30
#number of timesteps to consider
num_timesteps = int(num_days * 24 * 60 * 60 / time_step_length)


num_sats = 84

num_gstations = 77


# to create sats in view matrix
sats_in_view = np.zeros((num_gstations, num_timesteps))    # to set up
for sat_number in range(0,num_sats):
    timeline = np.load(timeline_path + 'timeline_sat_' + str(sat_number) + '_' + case_name + '.npy', allow_pickle = True)
    timestep_number = 0                                      # set timestep to count from 0 for new satellite
    for step in timeline:
        for element in step[1:]:
            if element[1] == 'sink':                                # if the item seen is a ground station
                gstation_number_temp = int(element[2][9:])          # pull out the ground station number
                sats_in_view[gstation_number_temp - 1, timestep_number] += 1

        timestep_number += 1                                        # increment timestep

# save sats in view matrix
np.save(results_path + 'sats_in_view_' + case_name, sats_in_view)
