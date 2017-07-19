 import numpy as np

 data = {}

 def add_peaks(peaks_arr,frequencies,times,song_title): #S is peaks
 """
 :param:
    peaks_arr[np.array]
        An array of the peaks.
        A 2D boolean array. If peaks_arr[i,j], there is a peak at [i,j]

    frequencies[np.array]
        A 1D integer array.
        frequencies[i] is the frequency of peaks_arr[i,:]

    times[np.array]
        A 1D integer array.
        times[j] is the time of peaks_arr[:,j]

  :return:
    No return. Adds new peaks into data dictionary

"""

    for freq_idx, time_idx in freq_idxs, time_idxs
         data[frequencies[freq_idx], times[time_inx]] = song_title
