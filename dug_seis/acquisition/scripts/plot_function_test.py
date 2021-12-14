import plot_simple
import fft_helper
from pathlib import Path

asdf_folder = Path('C:/Users/thaag/PycharmProjects/DUGseis-acquisition/raw_waveforms/01_Inputrange_change/b_100mV_range/raw_waveforms/306')
asdf_folder = Path('C:/polybox/asdfAqSys/codeTH/raw_waveforms/348')

print("towards automated testing")
print("let acquisition run for 3 files of 10 sec")

channel_array = [1, 2]

buffer_change_sec = 32*1024*1024/200e3/32
print("buffer_change_sec:{}".format(buffer_change_sec))
print("jump expected here, simulation data wraps over")
plot_simple.plot_simple(asdf_folder, channel_array, buffer_change_sec*4-0.02, 0.04)
print("no jump expected, between two buffers")
x = plot_simple.plot_simple(asdf_folder, channel_array, buffer_change_sec-0.005, 0.01)
print("10kHz 20'000 amplitude sine")
fft_helper.fft_helper(x)
print("at the beginning of a file")
x = plot_simple.plot_simple(asdf_folder, channel_array, 0, 0.01)
fft_helper.fft_helper(x)
print("between two files")
x = plot_simple.plot_simple(asdf_folder, channel_array, 9.98, 0.04)
fft_helper.fft_helper(x)