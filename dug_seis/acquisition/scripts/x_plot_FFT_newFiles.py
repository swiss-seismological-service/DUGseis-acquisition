from pathlib import Path
import pyasdf
from obspy.core import Stream

import plot_waveform_v03_only_wave as plot

import numpy as np
import scipy.fftpack

import matplotlib.pyplot as plt
plt.style.use('classic')

# Path of asdf files
asdf_folder = Path('/data/raw_waveforms/236/')
asdf_folder = Path('/data/testData/secondPulsesOnCh32')
#asdf_folder = Path('/data/testData/sine20kHzConti04/')
#asdf_folder = Path('/data/testData/noiseConti04/')
asdf_list = list(sorted(asdf_folder.glob('*.h5')))
fast_mode = False

file_names = []
npts_all = []
delta = []
stream_1 = Stream()
for index, file_name in enumerate(asdf_list):

    print('.', end='')
    asdf_1 = pyasdf.ASDFDataSet(file_name, mode='r')
    start_time = asdf_1.waveforms.XB_04.raw_recording[0].stats.starttime
    end_time = asdf_1.waveforms.XB_04.raw_recording[0].stats.endtime

    for chan in range(32, 33): # 33
        stream_1 += asdf_1.get_waveforms(network='XB', station='04',
                                         location=str(chan).zfill(2), channel="001",
                                         starttime=start_time,
                                         endtime=end_time,  # start_time+1,  # end_time,
                                         tag="raw_recording")

    # print(stream_1)
    # stream_1[index].stats.sampling_rate = 200000
    # stream_1[index].stats.delta = 5e-6
    # print(stream_1[index].stats.sampling_rate)
    # print(stream_1[index].stats.delta)

    if index >= 2 and fast_mode:
        break

print("merging")
stream_1.merge(method=0)

# Number of sample points
N = 120000
print("length of stream_1: " + str(len(stream_1.traces[0].data)))
sig = stream_1.traces[0].data[0:N]
print("length of sig: " + str(len(sig)))

plt.plot(sig)

# sample spacing
T = 5e-6
x = np.linspace(0.0, N*T, N)
yf = scipy.fftpack.fft(sig)
xf = np.linspace(0.0, 1.0/(2.0*T), int(N/2))

fig, ax = plt.subplots()
ax.plot(xf, 2.0/N * np.abs(yf[:N//2]), marker='o')
plt.show()

# plot.plot_waveform(stream_1)
