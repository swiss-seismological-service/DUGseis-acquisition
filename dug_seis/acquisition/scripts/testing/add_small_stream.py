from obspy.core import Stream, Trace, UTCDateTime
import numpy as np
import pyasdf
import time

time_start = time.time()
starttime_ns = UTCDateTime().ns
stats = {'network': 'XB',
         'station': '99'.zfill(2),
         'location': '00',
         'channel': '001',
         'starttime': UTCDateTime(ns=starttime_ns),
         'delta': 1/200000,
         'gain': '0'
         }

_st = str(stats['starttime'])
_st = _st.replace(":", "_")
_st = _st.replace("-", "_")
folder_file_name = "./small_stream/{}.h5".format(_st)

np_data = np.ones(int(200e3)) # Fall 1
np_data = np.ones(5) # Fall 2

stream = Stream()
stream += Trace(np_data, header=stats)

file_handle = pyasdf.ASDFDataSet(folder_file_name, compression=None)
file_handle.append_waveforms(stream, tag="raw_recording")
del stream

nr_of_datapoints = len(np_data)
delta = 1/200e3
starttime_ns = starttime_ns + int(nr_of_datapoints * (delta * 10 ** 9))
print(stats['starttime'])
stats['starttime'] = UTCDateTime(ns=starttime_ns)
print(stats['starttime'])
np_data = np.ones(int(200e3*10)-nr_of_datapoints) # 1048576

stream = Stream()
stream += Trace(np_data, header=stats)

file_handle.append_waveforms(stream, tag="raw_recording")
del stream

print("writing file took: {:.3f}sec".format(time.time()-time_start))

ds = pyasdf.ASDFDataSet(folder_file_name)
print(ds)

station_list = ds.waveforms.list()
sta = ds.waveforms[ station_list[0] ]
print(sta.raw_recording)

print("script took: {:.3f}sec".format(time.time()-time_start))