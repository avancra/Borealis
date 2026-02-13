# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 16:38:58 2024

@author: renebes
"""
new_file('Dummy experiment')

new_sample('Dummy sample')

# scan motor mono
mono.scan(1, 10, 1, acq_time=1)

# scan in energy with detector (acquisition) and acquisition time of 1 s per point
energy.scan(17.1, 17.2, 0.01, acq_time=1)
