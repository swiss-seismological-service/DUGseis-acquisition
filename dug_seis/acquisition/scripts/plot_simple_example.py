import plot_simple
from pathlib import Path

asdf_folder = Path('C:/Users/thaag/PycharmProjects/DUGseis-acquisition/raw_waveforms/302')
channel_array = [1,2,3]

# channel_array = range(1, 4)

# print("\nall channels:")
# plot_simple.plot_simple(asdf_folder, range(1, 33), 0, 300)

print("\n2 channels:")
plot_simple.plot_simple(asdf_folder, channel_array, 0, 300)
"""
print("\none buffer, in simulation mode this is a jump:")
plot_simple.plot_simple(asdf_folder, channel_array, 20.8, 0.4)
"""
print("\ngluing two 30sec files (@10ms mark):")
plot_simple.plot_simple(asdf_folder, channel_array, 29.99, 0.02)

print("\ngluing two 30sec files (@10ms mark):")
plot_simple.plot_simple(asdf_folder, channel_array, 59.99, 0.02)
