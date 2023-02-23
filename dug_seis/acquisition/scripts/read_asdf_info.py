from pathlib import Path
import pyasdf

asdf_folder = Path('C:/polybox/asdfAqSys/code/DUGseis-acquisition/raw_waveforms/54')
asdf_list = list(sorted(asdf_folder.glob('*.h5')))

# dataset
ds = pyasdf.ASDFDataSet(asdf_list[0])
print(ds)
print(ds.events)
station_list = ds.waveforms.list()
print(station_list)
print(ds.waveforms[ station_list[0] ])

for station in ds.waveforms:
    print(station)

sta = ds.waveforms[ station_list[0] ]
print(sta.get_waveform_tags())
print(sta.raw_recording)

print(ds.auxiliary_data)
aux_data_list = ds.auxiliary_data.list()
print(aux_data_list)
print(ds.auxiliary_data[ aux_data_list[0] ])
aux_items_list = ds.auxiliary_data[ aux_data_list[0] ].list()
aux_item = ds.auxiliary_data[ aux_data_list[0] ][aux_items_list[0]]
print(aux_item)
print(aux_item.parameters)

print(aux_item.data[0])
print("---")
i = 1
for x in aux_item.data:
    print("{}: {}".format(i, x))
    i = i+1
print("---")

for aux_item in aux_items_list:
    one_aux_item = ds.auxiliary_data[ aux_data_list[0] ][aux_item]
    print(one_aux_item.parameters)

