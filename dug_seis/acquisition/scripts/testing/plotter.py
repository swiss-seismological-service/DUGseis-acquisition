# DUG-Seis
#
# :copyright:
#    ETH Zurich, Switzerland
# :license:
#    GNU Lesser General Public License, Version 3
#    (https://www.gnu.org/copyleft/lesser.html)
#

import os
import pyasdf
from scipy.io import savemat
# from obspy.core import read

file_list = []
for file in os.listdir("../../raw_waveforms/299/"):
    if file.endswith(".h5"):
        file_list.append(os.path.join("../../raw_waveforms/299", file))
        # print(os.path.join("/20181107_sw_test", file))
file_list.sort(reverse=True)
load_file_0 = file_list[0]
print("loading latest file: {}".format(load_file_0))

ds_0 = pyasdf.ASDFDataSet(load_file_0)
print(ds_0.events)
print(ds_0.waveforms.list())
print(ds_0.waveforms.XB_99.raw_recording[1].stats)

load_file_1 = file_list[1]
#print("loading latest file: {}".format(load_file_1))

ds_1 = pyasdf.ASDFDataSet(load_file_1)
#print(ds_1.events)
#print(ds_1.waveforms.list())
print(ds_1.waveforms.XB_99.raw_recording[1].stats)

print(ds_1.waveforms.XB_99.raw_recording)


several_channels = ds_1.waveforms["XB.99"].raw_recording
several_channels += ds_1.waveforms["XB.99"].raw_recording
several_channels += ds_1.waveforms["XB.99"].raw_recording

# print some info
print("sampling_rate: " + str(ds_1.waveforms["XB.99"].raw_recording[0].stats.sampling_rate))
print("data type of trace: " + str(type(ds_1.waveforms["XB.99"].raw_recording[0].data)))
print("nr of samples recorded: " + str(ds_1.waveforms["XB.99"].raw_recording[0].data.size))
print("seconds @ 200k samples: " + str(ds_1.waveforms["XB.99"].raw_recording[0].data.size/200e3))
print("seconds @ 200k samples: " + str(ds_1.waveforms["XB.99"].raw_recording[0].data.size/200e3))
print("seconds @ 200k samples: " + str(ds_1.waveforms["XB.99"].raw_recording[0].data.size/200e3))

total_samples = 0
for one_recording in ds_1.waveforms["XB.99"].raw_recording:
    print("one_recording : " + str(one_recording.data.size))
    total_samples += one_recording.data.size

print("total samples: " + str(total_samples))
print("seconds @ 200k samples: " + str(total_samples/200e3))


dt = ds_1.waveforms["XB.99"].raw_recording[0].stats.starttime
several_channels.plot(size=(800, 600))
# three_channels.plot(size=(800, 600), starttime=dt, endtime=dt+0.02)

# gap at 5.2429 sec? 32 Mb buffer
# several_channels.plot(size=(800, 600), starttime=dt + 5.241, endtime=dt + 5.245)

several_channels.plot(size=(800, 600), starttime=dt + 4, endtime=dt + 5.42)

for i, tr in enumerate(several_channels):
    # for i, tr in enumerate(ds_1.waveforms["XG.001"].raw_recording):
    mdict = {k: str(v) for k, v in tr.stats.items()}
    mdict['data'] = tr.data
    folder = 'matlab'
    if not os.path.isdir(folder):
        os.makedirs(folder)
        print("creating folder: {}".format(folder))
    savemat(folder + "/" + "data-%d.mat" % i, mdict)



# direct:
# ds_1.waveforms["XG.003"].raw_recording.plot()

print(ds_1.events)
print(ds_1.waveforms.list())

station = ds_1.waveforms["XB.99"]
print(station)
print(station.get_waveform_tags())

stream = station.raw_recording
print(stream)

stream.plot()

dt = stream[0].stats.starttime
stream.plot(starttime=dt, endtime=dt+0.01)

three_channels = ds_1.waveforms["XB.99"].raw_recording
three_channels += ds_1.waveforms["XB.99"].raw_recording
three_channels += ds_1.waveforms["XB.99"].raw_recording
three_channels += ds_1.waveforms["XB.99"].raw_recording
three_channels.plot(size=(800, 600))

