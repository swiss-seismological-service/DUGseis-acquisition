from pathlib import Path
import pyasdf
from obspy.core import Stream

import plot_waveform_v03_only_wave as plot

# Path of asdf files
asdf_folder = Path('/data/testData/secondPulsesOnCh32/')
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
                                         endtime=start_time+0.001,  # start_time+1,  # end_time,
                                         tag="raw_recording")
        stream_1 += asdf_1.get_waveforms(network='XB', station='04',
                                         location=str(chan).zfill(2), channel="001",
                                         starttime=end_time-0.001,
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

plot.plot_waveform(stream_1)
