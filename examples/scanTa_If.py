import numpy as np
import matplotlib.pyplot as plt

acq_time = 1150
output_name = 'Si(660)_Ta_L3_emission_1150s'

theta_min = 75
theta_max = 80
theta_step = 0.1

roi_min_L_alpha=1424
roi_max_L_alpha=1532

roi_min_L_beta=1662
roi_max_L_beta=1796

output = theta.scan(theta_min, theta_max, theta_step, acq_time)

angles = np.arange(theta_min, theta_max, theta_step)

data = np.zeros((np.shape(angles)[0], 2))
data[:, 0] = angles

#save If L_aplha as function of bragg angle in text file
for idx, mca in enumerate(output.tolist()):
    data[idx, 1] = np.sum(mca.counts[roi_min_L_alpha:roi_max_L_alpha])
np.savetxt(output_name + '_LA.txt.txt', data)

#save If L_beta as function of bragg angle in text file
for idx, mca in enumerate(output.tolist()):
    data[idx, 1] = np.sum(mca.counts[roi_min_L_beta:roi_max_L_beta])
np.savetxt(output_name + '_LB.txt', data)