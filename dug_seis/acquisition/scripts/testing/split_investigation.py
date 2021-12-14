import time

more_verbose = False

one_buffer_bytes = 32*1024*1024
one_buffer_nr_of_samples = int(one_buffer_bytes/16/2)
nr_of_new_datapoints = one_buffer_nr_of_samples
file_length_sec = 10.0
sampling_rate = 200e3
file_length_in_samples = int(file_length_sec * sampling_rate)
data_points_since_start = 0
data_points_in_this_file = 0
# calculate when next datapoint needs to be deleted
_fpga_value_should = 2**32*sampling_rate/20e6
fpga_value_is = round(_fpga_value_should)
one_sample_delay_in_sec = 1/(20e6*(fpga_value_is-_fpga_value_should)/2**32)
drop_point_every = sampling_rate * one_sample_delay_in_sec
drop_next_point_at = drop_point_every
smallest_file_start = 9999999
biggest_file_start = 0

print(one_buffer_bytes)
print(one_buffer_nr_of_samples)
print(type(data_points_since_start))

while True:
    data_points_since_start += nr_of_new_datapoints
    if file_length_in_samples - data_points_in_this_file >= nr_of_new_datapoints:
        data_points_in_this_file += nr_of_new_datapoints
        data_points_to_file1 = nr_of_new_datapoints
    else:
        # print("splitting file")
        data_points_to_file1 = file_length_in_samples - data_points_in_this_file
    data_points_to_file2 = nr_of_new_datapoints - data_points_to_file1
    if data_points_to_file1 + data_points_to_file2 != nr_of_new_datapoints:
        print("error: data_points_to_file1 + data_points_to_file2 != nr_of_new_datapoints")

    if data_points_to_file2 != 0:
        if more_verbose or data_points_since_start > 406950248070:
            print("starting the next file with {} datapoints.".format(data_points_to_file2))
        start_sample = data_points_to_file1
        if smallest_file_start > data_points_to_file2:
            smallest_file_start = data_points_to_file2
            print("new smaller value found: {}".format(smallest_file_start))

        if biggest_file_start < data_points_to_file2:
            biggest_file_start = data_points_to_file2
            print("new bigger value found: {} at data_points_since_start {}".format(biggest_file_start, data_points_since_start))

        if 277277048574-60*200e3 < data_points_since_start < 277277048574+60*200e3:
            print("starting the next file with {} datapoints.".format(data_points_to_file2))

        # drop one sample if needed, its the first sample of the new file
        if data_points_since_start > drop_next_point_at:
            print("dropped one data point nr: {}".format(data_points_since_start))
            drop_next_point_at += drop_point_every
            data_points_since_start -= 1
            data_points_to_file2 -= 1
            print("dropped one data point, data_points_to_file2: {}".format(data_points_to_file2))
            #time.sleep(0.5)
            if type(data_points_since_start) is not int:
                print(type(data_points_since_start))
            if data_points_since_start == 406950248070 - 1:
                print("last before error")
                time.sleep(2)
            if data_points_since_start > 406950248070:
                print("one more than the error")
                time.sleep(2)
                break

        data_points_in_this_file = data_points_to_file2

    # time.sleep(0.5)

print("")
print(type(data_points_since_start))
print("smallest value found: {}".format(smallest_file_start))
print("biggest value found: {}".format(biggest_file_start))
