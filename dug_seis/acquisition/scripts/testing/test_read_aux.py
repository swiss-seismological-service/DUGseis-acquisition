import pyasdf
import numpy as np
import os

print(os.getcwd())

ds = pyasdf.ASDFDataSet("./../../../../01_dummy_Grimsel/01_ASDF_data/188/2021_07_07T15_11_30.215733Z__2021_07_07T15_11_36.215728Z__02.h5")
print(ds.events)
ds.waveforms.list()

print(ds.auxiliary_data)

print(ds.auxiliary_data.hardware_settings)
print(ds.auxiliary_data.hardware_settings.input_range)
print(ds.auxiliary_data.hardware_settings.input_range.data[:])
print(ds.auxiliary_data.hardware_settings)
print(ds.auxiliary_data.hardware_settings.various)
