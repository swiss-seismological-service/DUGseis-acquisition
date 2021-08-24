from pathlib import Path
import pyasdf
# import pandas as pd

# Path of asdf files
asdf_folder = Path('/data/raw_waveforms/99/')
asdf_list = list(sorted(asdf_folder.glob('*.h5')))

file_names = []
npts_all = []
delta = []
for index, file_name in enumerate(asdf_list):

    asdf_1 = pyasdf.ASDFDataSet(file_name, mode='r')
    start_time = asdf_1.waveforms.XB_04.raw_recording[0].stats.starttime
    daq_nr = '02'
    end_time = asdf_1.waveforms.XB_04.raw_recording[0].stats.endtime
    file_name_file = start_time.strftime('%Y_%m_%dT%H_%M_%S_%f') + '__' + \
                    end_time.strftime('%Y_%m_%dT%H_%M_%S_%f') + '__' + daq_nr + '.h5'
    npts = asdf_1.waveforms.XB_04.raw_recording[0].stats.npts
    asdf_1 = None
    file_names.append(file_name_file)
    npts_all.append(npts)
    delta.append(end_time - start_time)
    print(file_name)
    print(npts)


d = {'file_names': file_names, 'npts': npts_all, 'delta [s]': delta}
df = pd.DataFrame(data=d)
df.to_csv(Path(asdf_folder).parents[1].joinpath('log_start_endtimes_in_asdf.csv'), index=False)
