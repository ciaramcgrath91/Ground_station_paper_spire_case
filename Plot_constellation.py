"""
Plot Spire Constellation
"""

import numpy as np
import matplotlib.pyplot as plt

Re = 6371000               # mean Earth radius, m

## Spacecraft set up
sat_name = 'LEMUR'                                  # sats to find by name
satellite_coes = np.load("Data\\satellite_coes_time_" + sat_name + ".npy").tolist()  # load in satellite coes (LEMURS in this case) and convert to list of lists
# list of lists of satellite parameters at epoch in keplerian elements [a, e, i, raan, arg p, mean anomaly] (all angles in radians)

# get sets of elements
smas = [i[0] for i in satellite_coes]
eccs = [i[1] for i in satellite_coes]
incs = [i[2] for i in satellite_coes]
raas = [i[3] for i in satellite_coes]
aops = [i[4] for i in satellite_coes]
anos = [i[5] for i in satellite_coes]
aols = [(i[4] + i[5]) % (2*np.pi) for i in satellite_coes]        # need to get between 0 and 360

# to plot
alts= [(i - Re)/1000 for i in smas]
incs_degs = [np.degrees(i) for i in incs]
raan_degs = [np.degrees(i) for i in raas]

# group by inclination
incs_eq = [i for i in incs_degs if i < 20]
incs_iss = [i for i in incs_degs if i < 60 and i > 40]
incs_polar = [i for i in incs_degs if i > 60 and i < 91]
incs_ss = [i for i in incs_degs if i > 90]
raan_of_incs_eq = [raan_degs[i] for i in range(0,len(incs_degs)) if incs_degs[i] < 20]
raan_of_incs_iss = [raan_degs[i] for i in range(0,len(incs_degs)) if incs_degs[i] < 60 and incs_degs[i] > 40]
raan_of_incs_polar = [raan_degs[i] for i in range(0,len(incs_degs)) if incs_degs[i] > 60 and incs_degs[i] < 91]
raan_of_incs_ss = [raan_degs[i] for i in range(0,len(incs_degs)) if incs_degs[i] > 90]
alts_of_incs_eq = [alts[i] for i in range(0,len(incs_degs)) if incs_degs[i] < 20]
alts_of_incs_iss = [alts[i] for i in range(0,len(incs_degs)) if incs_degs[i] < 60 and incs_degs[i] > 40]
alts_of_incs_polar = [alts[i] for i in range(0,len(incs_degs)) if incs_degs[i] > 60 and incs_degs[i] < 91]
alts_of_incs_ss = [alts[i] for i in range(0,len(incs_degs)) if incs_degs[i] > 90]

# altitude vs raan  polar plot
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='polar')
ax.scatter(raan_of_incs_eq, alts_of_incs_eq, marker = "o", s = 100, cmap='hsv', alpha=0.75, label = "Equatorial") #  (5deg < i < 6deg)
ax.scatter(raan_of_incs_iss, alts_of_incs_iss, marker = "s", s = 100, cmap='hsv', alpha=0.75, label = "ISS")  #  (50deg < i < 52deg)
ax.scatter(raan_of_incs_polar, alts_of_incs_polar, marker = "^", s = 100, cmap='hsv', alpha=0.75, label = "Polar")    #  (82deg < i < 86deg)
ax.scatter(raan_of_incs_ss, alts_of_incs_ss, marker = "D", s = 100, cmap='hsv', alpha=0.75, label = 'Sun-sync')   #  (96deg < i < 98deg)
ax.set_ylim([350,700])
ax.tick_params(axis='both', which='major', labelsize=14)
ax.legend(fontsize=14, loc=(-0.2,0.9))
plt.show()
# plt.savefig('const_pars_hires.png', dpi=600)
