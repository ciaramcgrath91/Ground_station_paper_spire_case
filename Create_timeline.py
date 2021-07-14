"""
Created by Ciara McGrath 31/07/2019
Code Ref: GS_CM_31072019_V2

* DISCLAIMER *
  The S/W remains property of Ciara McGrath and shall not be modified,
  nor shall it be forwarded to third parties without prior written consent

"""

import numpy as np          # need to import modules to be used in every individual module that calls it
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import time
from supporting_funcs import (
                                              odeFixedStepnoman, eq_of_motion_noman, greg2jd, gast, find_sat_elevation, 
                                               lat_long_ssp_calc, find_dist
                                              )

def divisionbyzeroiszero(n, d):
    return n / d if d else 0


start_time = time.time()

case_name = "spire_final_test"

## ---------------------------
## Input Values
## ---------------------------

## Constants
mu =  3.986004418 * 10**14    # standard gravitational parameter, m^3/s^2
Re = 6371000               # mean Earth radius, m
J2 = 1082.7 * (10**-6)        # coefficient of the Earth's gravitational zonal harmonic of the 2nd degree, -
flattening = 0.00335281    # flattening value
rot_rate = 0.0000729212   # rotation rate of central body

## Parameters
max_target_elevation = 15 # degs
max_gstation_elevation = 15 # degs

## Spacecraft set up
sat_name = 'LEMUR'                                  # sats to find by name
satellite_coes = np.load("Data\\satellite_coes_time_" + sat_name + ".npy").tolist()  # load in satellite coes (LEMURS in this case) and convert to list of lists
sats_epoch = satellite_coes
num_sats = len(sats_epoch)
sats_names = ["Sat " + str(i + 1) for i in range(0,num_sats)]

## Sources set up
sources = np.load("Data\\250_shipping_locations2.npy").tolist()  # load in source locations in latitude and longitude
# list of lists of source latitude and longitude 
num_sources = len(sources)                              # number of sources   
source_names = ["Source " + str(i + 1) for i in range(0,num_sources)]


## ground stations set up: changed to test specific set
gstations = np.load("Data\\GS_locations.npy").tolist()  # load in ground stations locations in latitude and longitude
# list of lists of gstations latitude and longitude 
num_gstations = len(gstations)                                  # number of ground stations   
gstations_names = ["Gstation " + str(i + 1) for i in range(0,num_gstations)]


## creating lists of headings for assigning to adj matrix
headings = [source_names + sats_names + gstations_names]


## date set up
"""
date_d = 1              # start day
date_m = 1              # start month
date_y = 2020           # start year
jdate_start = greg2jd(date_m, date_d, date_y)     # convert start date to Julian
"""
jdate_start = 2458701.72286614

## analysis set up 
tmin = 0                # analysis start time
num_days = 100            # number of days to run analysis
tmax = num_days * 24 * 60 * 60     # analysis end time, secs
tstep = 30              # time step, secs


## ---------------------------
## Execution
## ---------------------------

# set start of satellite count
sat_index = 0

# loop over satellites:
for satellite in sats_epoch:
    y0 = [satellite[0], satellite[3], satellite[4] + satellite[5]]     # assign sma, raan and arg of latitude
    incl = satellite[2]                                 # assign inclination
    
    # integrate equations. sol has states of each value at all times in t vector 
    sol, t = odeFixedStepnoman(eq_of_motion_noman, y0, tmin, tmax, tstep, mu, Re, J2, incl)

    # create timeline for satellite 
    timeline = [[i] for i in t]

    # assign values
    a_full = sol[:, 0]
    raan_full = sol[:, 1]
    aol_full = sol[:, 2]

    # initialise value holders
    lat_ssp = []
    lon_ssp = []

    # loop through solutions and calculate latitude and longtude of ssp at each time step
    for i in range(0,len(sol)):
            sat_ssp_temp = lat_long_ssp_calc(sol[i], t[i], Re, incl, flattening, rot_rate, jdate_start)
            lat_ssp.append(sat_ssp_temp[0])
            lon_ssp.append(sat_ssp_temp[1])

    # set start of sources count
    source_index = 0   
    
    # loop over ground stations
    for source in sources:
        # set up ground station
        source_lat_deg = source[0]         # latitude of target, deg
        source_lon_deg = source[1]           # longitude of target, deg
        source_lat = source_lat_deg * np.pi / 180      # latitude of target, deg
        source_lon = source_lon_deg * np.pi / 180        # longitude of target, deg

        # initialise value holders
        dist = []
        elevation = []

        # loop through solutions and calculate elevation at each time step
        for i in range(0,len(lat_ssp)):
            dist_temp = find_dist(lat_ssp[i], lon_ssp[i], source_lat, source_lon, Re)
            elev_temp = find_sat_elevation(sol[i][0], dist_temp, Re)
            dist.append(dist_temp)
            elevation.append(elev_temp) 

        # convert elevation to degrees
        elevation_deg = [i * 180 / np.pi for i in elevation]


        # want instances with elevation > x deg
        el_deg_in_view = [i for i in elevation_deg if i >= max_target_elevation]
        index_in_view = [i for i, v in enumerate(elevation_deg) if v >= max_target_elevation]       # returns index i if value v is greater than or equal to x: https://stackoverflow.com/questions/13717463/find-the-indices-of-elements-greater-than-x
        timesteps_in_view = [t[i] for i in index_in_view]

        # indicate in timeline when source is in view and which source
        for i in index_in_view: 
            timeline[i].append([t[i], 'source', source_names[source_index]])

        source_index += 1                                                 # increment ground station count for next loop


    # set start of ground stations count
    gstation_index = 0   
    
    # loop over ground stations
    for station in gstations:
        # set up ground station
        tar_lat_deg = station[0]         # latitude of target, deg
        tar_lon_deg = station[1]           # longitude of target, deg
        tar_lat = tar_lat_deg * np.pi / 180      # latitude of target, deg
        tar_lon = tar_lon_deg * np.pi / 180        # longitude of target, deg

        # initialise value holders
        dist = []
        elevation = []

        # loop through solutions and calculate elevation at each time step
        for i in range(0,len(lat_ssp)):
            dist_temp = find_dist(lat_ssp[i], lon_ssp[i], tar_lat, tar_lon, Re)
            elev_temp = find_sat_elevation(sol[i][0], dist_temp, Re)
            dist.append(dist_temp)
            elevation.append(elev_temp) 

        # convert elevation to degrees
        elevation_deg = [i * 180 / np.pi for i in elevation]

        # want instances with elevation > x deg
        el_deg_in_view = [i for i in elevation_deg if i >= max_gstation_elevation]
        index_in_view = [i for i, v in enumerate(elevation_deg) if v >= max_gstation_elevation]       # returns index i if value v is greater than or equal to x: https://stackoverflow.com/questions/13717463/find-the-indices-of-elements-greater-than-x
        timesteps_in_view = [t[i] for i in index_in_view]

        # indicate in timeline when sink is in view and which gstation
        for i in index_in_view: 
            timeline[i].append([t[i], 'sink', gstations_names[gstation_index]])

        gstation_index += 1                                                 # increment ground station count for next loop

    # save timelines
    np.save("Timeline Files\\timeline_" + "sat_" + str(sat_index) + '_' + case_name, timeline)

    sat_index +=1                           # increment ground station count for next loop




runtime = (time.time() - start_time)

print("--- runtime: %s seconds ---" % (runtime))

