import plot_simple
import fft_helper
from pathlib import Path

asdf_folder = Path('C:/Users/thaag/PycharmProjects/DUGseis-acquisition/raw_waveforms/01_Inputrange_change/b_100mV_range/raw_waveforms/306')
channel_array = [1,6,7]

# channel_array = range(1, 4)

# print("\nall channels:")
# plot_simple.plot_simple(asdf_folder, range(1, 33), 0, 300)

x = plot_simple.plot_simple(asdf_folder, [6], 29.99, 0.2)
fft_helper.fft_helper(x)

x.filter("bandpass", freqmin=200.0, freqmax=2000.0)
x.plot()

"""
print("\n2 channels:")
plot_simple.plot_simple(asdf_folder, channel_array, 0, 300)

print("\none buffer, in simulation mode this is a jump:")
plot_simple.plot_simple(asdf_folder, channel_array, 20.8, 0.4)

print("\ngluing two 30sec files (@10ms mark):")
plot_simple.plot_simple(asdf_folder, channel_array, 29.99, 0.04)
plot_simple.plot_simple(asdf_folder, [6], 29.99, 0.04)
plot_simple.plot_simple(asdf_folder, [7], 29.99, 0.04)

print("\ngluing two 30sec files (@10ms mark):")
plot_simple.plot_simple(asdf_folder, channel_array, 59.99, 0.02)
"""
