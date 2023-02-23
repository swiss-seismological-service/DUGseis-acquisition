import pyasdf
from pathlib import Path
from math import floor
from obspy.core import Stream
import plot_waveform_v03_only_wave as plot
from obspy.core import UTCDateTime

def plot_simple(asdf_folder, channel_array, starttime_relative_sec, length_sec, max_points=10**5, max_files=3):
    print(asdf_folder)
    print(channel_array)

    asdf_list = list(sorted(asdf_folder.glob('*.h5')))

    file_names = []
    npts_all = []
    delta = []
    stream_1 = Stream()
    for index, file_name in enumerate(asdf_list):

        print('')
        print('.', end='')
        asdf_1 = pyasdf.ASDFDataSet(file_name, mode='r')
        sta_one = asdf_1.waveforms.list()[0]
        network_str = sta_one.split('.')[0]
        station_str = sta_one.split('.')[1]
        # print("using station: {}".format(sta_one))
        start_time = asdf_1.waveforms[sta_one].raw_recording[0].stats.starttime
        end_time = asdf_1.waveforms[sta_one].raw_recording[0].stats.endtime
        if index == 0:
            start_time_first_file = start_time
            print(" start_time_first_file: {} ".format(start_time_first_file), end='')
        #if start_time > UTCDateTime(ns=start_time_first_file.ns + int(length_sec*10**9)):
        if start_time > start_time_first_file + starttime_relative_sec + length_sec or \
                end_time < start_time_first_file + starttime_relative_sec:
            print("time outside", end='')
        else:
            for chan in channel_array:
                print( str(chan).zfill(2), end=' ' )
                stream_1 += asdf_1.get_waveforms(network=chan.split('.')[0], station=chan.split('.')[1],
                                                 location=chan.split('.')[2], channel=chan.split('.')[3],
                                                 starttime=start_time_first_file + starttime_relative_sec,
                                                 endtime=start_time_first_file + starttime_relative_sec + length_sec,
                                                 tag="raw_recording")
        if index >= max_files-1:
            print("\nskipping other files (use max_files= to load more files)")
            break

    print("")
    print("merging", end='')
    stream_1.merge(method=0)
    print(" - done")
    stream_1.print_gaps()

    stream_2 = stream_1.copy()

    nr_datapoints = stream_1.count() * stream_1.traces[0].data.size
    print("total data points to plot: {}".format(nr_datapoints), end='')
    if nr_datapoints > max_points:
        d = floor(nr_datapoints/max_points)+1
        stream_1.decimate(d, no_filter=True)
        print(" - decimating by {} to {}".format(d, stream_1.count() * stream_1.traces[0].data.size))
    else:
        print()

    plot.plot_waveform(stream_1)
    return stream_2

