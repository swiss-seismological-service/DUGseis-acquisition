from pathlib import Path
import pyasdf
from obspy.core import Stream

# Path of asdf files
asdf_folder = Path('/home/user/Desktop/Test_acquisition/asdf_data/188/')
asdf_list = list(sorted(asdf_folder.glob('*.h5')))

file_names = []
npts_all = []
delta = []
stream_1 = Stream()
for index, file_name in enumerate(asdf_list):

    asdf_1 = pyasdf.ASDFDataSet(file_name, mode='r')
    start_time = asdf_1.waveforms.XB_02.raw_recording[0].stats.starttime
    end_time = asdf_1.waveforms.XB_02.raw_recording[0].stats.endtime

    stream_1 += asdf_1.get_waveforms(network='XB', station='02',
                                     location="04", channel="001",
                                     starttime=start_time,
                                     endtime=end_time,
                                     tag="raw_recording")
    print(stream_1[index].stats.sampling_rate)
    stream_1[index].stats.sampling_rate = 200000
    x = 2


for tr in stream_1:
    tr.stats.sampling_rate = 200000.0


stream_1.merge(method=0)
