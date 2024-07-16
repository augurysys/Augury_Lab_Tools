import math
import numpy as np
import json
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import os
from scipy import signal
#from hw_variables import *
from hw_varibles import *

class Vibration_Analysis:
    print("vibration ")
    def __init__(self):
        self.ref_frequency_error = None
        self.ref_rms = None
        self.ref_detected_peaks_amp = None
        self.ref_detected_peaks_bin = None
        self.ref_fft_values = None
        self.ref_freq_bin = None
        self.ref_data = None
        self.ref_fs = None
        self.ref_time_axis = None
        self.shaker_tool_only = None
        self.rms_of_noise_check = None
        self.freq_error_check = None
        self.freq_bin = None
        self.hw_version = None
        self.fw_version = None
        self.data_channel = None
        self.data_unit = None
        self.fs = None
        self.num_of_samples = None
        self.scaling_factor = None
        self.data = None
        self.report_path = None
        self.white_list = [89, 281, 479, 677, 877, 1069, 1259, 1459, 1657, 1847, 2039, 2237, 2437, 2633, 2833, 3023, 3217, 3413, 3613, 3803, 4001, 4201, 4397, 4591, 4793, 4993, 5189, 5387, 5573, 5779, 5953, 6151, 10000]
        self.serial_number = None
        self.fft_values = None
        self.detected_peaks_bin = None
        self.detected_peaks_amp = None
        self.frequency_error = None
        self.rms = None
        self.time_axis = None

    def set_vibration_analysis(self, report_path, method, white_list, shaker_reports_full_path, shaker_tool_only):

        self.shaker_tool_only = not (shaker_tool_only == 'false')
        self.report_path = report_path

        if method not in VIBRATION_METHODS:
            raise Exception("Unrecognized method was given.")

        if white_list is not None:
            self.white_list = [int(x) for x in white_list.split(",")]
        else:
            self.white_list = WHITE_LIST[method]

        self.get_shaker_reports(shaker_reports_full_path)


    # fix the value for shaker piezo - need only path
    def get_shaker_reports(self, shaker_reports_full_path):
        print(shaker_reports_full_path)
        with open(shaker_reports_full_path) as f:
            shaker_output = json.load(f)
        self.ref_data = shaker_output["output_data"]
        print(type(self.ref_data))

        self.ref_fs = shaker_output["fs_rec"]
        print("finish stage A - path + piezo data from file from shaker_reports_full_path  ")

    def run_vibration_analysis(self, report_path, method=None, white_list=None,  shaker_reports_full_path=None, shaker_tool_only='False'):

        self.set_vibration_analysis(report_path, method, white_list, shaker_reports_full_path, shaker_tool_only)
        print("stage A")
        self.calculate_data()
        print("stage B")
        self.plot_and_save()
        print("stage C")
        self.check_pass_fail()
        print("stage D")
    def extract_data_from_json(self):
        ep_file_path = ''

        # List all items in the directory
        dir_contents = os.listdir(self.report_path)



        # Find the first directory that starts with "halo"todo :
        # halo_dir = next(
        #     (d for d in dir_contents if os.path.isdir(os.path.join(self.report_path, d)) and d.startswith("halo")), None)
        #
        # if halo_dir:
        #     ep_file_path = os.path.join(self.report_path, halo_dir)
        #
        # else:
        #     raise Exception("No directory starting with 'halo' found in the specified path")
        ep_file_path = self.report_path
        os.chdir(ep_file_path)

        if len(os.listdir()) == 0:
            raise Exception("The directory is empty.")

        acc_z_exists = False

        for f_name in os.listdir():
            if not (f_name.endswith("2.json")):
                continue
            else:
                acc_z_exists = True

            with open(f_name) as f:
                jsondict = json.load(f)
                self.serial_number = jsondict["Serial_Number"]
                self.hw_version = jsondict["HW_Version"]
                self.fw_version = jsondict["FW_Version"]
                self.data_channel = jsondict["Data_Channel"]
                self.data_unit = jsondict["Data_Unit"]
                self.fs = jsondict["Sampling_Frequency"]
                self.num_of_samples = jsondict["Num_Of_Samples"]
                self.scaling_factor = jsondict["Scaling_Factor"]
                self.data = jsondict["Data"]


        if not acc_z_exists:
            raise Exception("Acceleration Z file does not exist.")

    def calculate_data(self):
        self.calculate_ref_data()
        print("calc piezo rerf data ")
        if not self.shaker_tool_only:
            print("call ep calc Value ")
            self.calculate_ep_data()

    def calculate_ep_data(self):
        print("Function - calculate EP Data ")
        self.extract_data_from_json()
        if self.data_unit == 'g':
            self.data = np.array(self.data)
            self.data = self.data.astype(int)
            self.data = np.multiply(self.data, self.scaling_factor * 1000 )  # self.scaling_factor * 1000)
        self.data = self.data - np.mean(self.data)

        self.time_axis = np.arange(0, len(self.data)) / self.fs
        self.freq_bin, self.fft_values = self.apply_fft(self.data, self.fs)
        self.detected_peaks_bin, self.detected_peaks_amp = self.detect_peaks(self.white_list, self.freq_bin, self.fft_values)
        self.rms = self.calculate_rms(self.freq_bin, self.detected_peaks_bin, self.fft_values)
        self.frequency_error = self.calculate_freq_error(self.white_list, self.detected_peaks_bin)

    def calculate_ref_data(self):

        if not self.ref_data:
            raise Exception('No ref data was given.')

        self.ref_data = np.array(self.ref_data)
        #self.ref_data = self.data.astype(int)
        self.ref_data = np.multiply(self.ref_data, 1)

        self.ref_data = self.ref_data - np.mean(self.ref_data) # remove mean
        num_of_samples = len(self.ref_data) # get num of sample
        self.ref_time_axis = np.arange(0, num_of_samples) / self.ref_fs
        self.ref_freq_bin, self.ref_fft_values = self.apply_fft(self.ref_data, self.ref_fs)
        self.ref_detected_peaks_bin, self.ref_detected_peaks_amp = self.detect_peaks(self.white_list, self.ref_freq_bin, self.ref_fft_values)
        self.ref_rms = self.calculate_rms(self.ref_freq_bin, self.ref_detected_peaks_bin, self.ref_fft_values)
        self.ref_frequency_error = self.calculate_freq_error(self.white_list, self.ref_detected_peaks_bin)
        print("piezo ok ")
    def check_pass_fail(self):
        if not self.shaker_tool_only:
            self.freq_error_check = all(x < FREQ_ERROR_THRESHOLD for x in self.frequency_error)
            self.rms_of_noise_check = all(x < RMS_THRESHOLD for x in self.rms)

            if all(np.abs(x) < VIBRATION_THRESHOLD for x in self.data):
                print("todo") #todo: add back
                # raise Exception(
                #     "Vibration data is too low (<100 [mg]). For solving: \n1. Check the shaker gain. \n2. Make sure the "
                #     "EP sampled on time.")
            if not self.freq_error_check:
                print("self.freq_error_check")
                #raise Exception("frequency error is over 1")todo: add
            if not self.rms_of_noise_check:
                print("self.rms_of_noise_check")
                #raise Exception("rms of noise is over 1")todo: add

    @staticmethod
    def calculate_freq_error(white_list, detected_peaks_bin):
        frequency_error = []
        for i in range(len(detected_peaks_bin)):
            frequency_error.append(np.abs(white_list[i] - detected_peaks_bin[i]))
        return frequency_error

    @staticmethod
    def detect_peaks(white_list, freq_bin, fft_values, search_range=2.0):
        detected_peaks_bin = []
        detected_peaks_amp = []
        while len(white_list) > len(detected_peaks_bin):
            detected_peaks_bin, detected_peaks_amp = Vibration_Analysis.find_vibration_peaks(white_list, freq_bin, fft_values, search_range=search_range)
            search_range += 1.0
        return detected_peaks_bin, detected_peaks_amp

    @staticmethod
    def calculate_rms(freq_bin, detected_peaks_bin, fft_values, peak_buffer=4):
        """
        Loop over all detected frequency bins.\n
        For each frequency bin, calculate the noise values preceding/succeeding it.\n
        Store the values in values dictionary - sorted by the detected FFT frequencies - which their corresponding bin is of length greater than 0.
        """
        fft_freq = freq_bin.tolist()
        previous_frequency = 0
        rms = []
        for curr_frequency in detected_peaks_bin:
            previous_index = fft_freq.index(previous_frequency)
            curr_ind = fft_freq.index(curr_frequency)
            start = previous_index + peak_buffer
            stop = curr_ind - peak_buffer
            fft_bin = fft_values[start:stop]
            if len(fft_bin):
                rms.append(math.sqrt(sum(np.square(fft_bin)) / len(fft_bin)))
            previous_frequency = curr_frequency
        return rms

    @staticmethod
    def find_vibration_peaks(white_list, freq_bin, fft_values, noise_floor=0.002, search_range=2.0):
        # print(freq_bin)
        # print((np.diff(freq_bin)))
        # print(np.mean(np.diff(freq_bin)))
        dist = np.round(search_range / np.mean(np.diff(freq_bin)))
        index_of_peaks, _ = signal.find_peaks(fft_values, height=noise_floor, distance=dist)
        white_list_pk = []
        white_list_pk_values = []
        for f in white_list:  # f is an input frequency
            peaks_in_white = []
            values_peaks_in_white = []
            for ind_pk in index_of_peaks:
                if np.abs(freq_bin[ind_pk] - f) < search_range:
                    peaks_in_white.append(freq_bin[ind_pk])  # frequency in fft close to f
                    values_peaks_in_white.append(fft_values[ind_pk])  # corresponding amplitude of frequency in fft
            if len(peaks_in_white) > 1:  # at least one peak was found close to f
                I = np.argmax(values_peaks_in_white)
            elif len(peaks_in_white) == 1:  # exactly one peak was found close to f
                I = 0
            else:  # no peaks were found around f
                continue

            white_list_pk.append(peaks_in_white[I])  # frequency in bin of f with highest amplitude
            white_list_pk_values.append(values_peaks_in_white[I])  # corresponding peak amplitude
        detected_peaks_bin = white_list_pk
        detected_peaks_amp = white_list_pk_values
        return detected_peaks_bin, detected_peaks_amp

    @staticmethod
    def apply_fft(data, sr, apply_hann_window=True):
        # FFT of ep data
        data_length = len(data)
        fft_length = data_length
        values_before_fft = data[:data_length]
        if apply_hann_window:
            window = np.hanning(data_length)
            values_before_fft = 2 * np.multiply(values_before_fft, window)
        fft_values = np.fft.rfft(values_before_fft, fft_length) / (len(values_before_fft) / 2.0)
        fft_values = np.abs(fft_values)
        fft_frequencies = np.fft.rfftfreq(fft_length, 1.0 / sr)
        return fft_frequencies, fft_values

    def plot_and_save(self):

        # Create subplots with 2 rows and 2 columns
        print("A")
        fig = make_subplots(rows=2, cols=2,
                            subplot_titles=['Acceleration over time', 'Acceleration FFT', 'Frequency Error', 'RMS of Noise'])

        # Acceleration over time - EP
        print("b")
        fig1 = px.line(x=self.time_axis, y=self.data, labels={'x': 'time [sec]', 'y': 'Acceleration [mG]'})
        fig.add_trace(go.Scatter(x=fig1.data[0]['x'], y=fig1.data[0]['y'], mode='lines', name='EP - Acceleration'), row=1, col=1)

        # Acceleration FFT - EP
        print("c")
        fig2 = px.line(x=self.freq_bin, y=self.fft_values, title='Acceleration FFT')
        fig.add_trace(go.Scatter(x=fig2.data[0]['x'], y=fig2.data[0]['y'], mode='lines', name='EP - FFT'), row=1, col=2)
        fig.add_scatter(x=self.detected_peaks_bin, y=self.detected_peaks_amp, mode="markers", row=1, col=2, name='Detected peaks EP')

        # Frequency Error - EP
        print("d")
        fig3 = px.bar(x=self.detected_peaks_bin, y=self.frequency_error, labels={'x': 'Frequency [Hz]', 'y': 'Error'})
        fig.add_trace(go.Bar(x=fig3.data[0]['x'], y=fig3.data[0]['y'], name='EP - Frequency Error'), row=2, col=1)
        print("e")
        fig.add_shape(dict(type='line', y0=1, y1=FREQ_ERROR_THRESHOLD, x0=min(self.white_list), x1=max(self.white_list),
                           line=dict(color='red', dash='dash')), row=2, col=1)


        # RMS of Noise - EP
        print("f")
        fig4 = px.bar(x=self.detected_peaks_bin, y=self.rms, labels={'x': 'Frequency', 'y': 'Amplitude [mg]'})
        fig.add_trace(go.Bar(x=fig4.data[0]['x'], y=fig4.data[0]['y'], name='EP - RMS'), row=2, col=2)
        fig.add_shape(dict(type='line', y0=1, y1=RMS_THRESHOLD, x0=min(self.ref_detected_peaks_bin), x1=max(self.ref_detected_peaks_bin),
                           line=dict(color='red', dash='dash')), row=2, col=2)

        # Acceleration over time - ref
        print("g")
        fig5 = px.line(x=self.ref_time_axis, y=self.ref_data, labels={'x': 'time [sec]', 'y': 'Acceleration [mG]'})
        fig.add_trace(go.Scatter(x=fig5.data[0]['x'], y=fig5.data[0]['y'], mode='lines', name='Ref - Acceleration'), row=1, col=1)

        # Acceleration FFT - ref
        print("h")
        fig6 = px.line(x=self.ref_freq_bin, y=self.ref_fft_values, title='Acceleration FFT')
        fig.add_trace(go.Scatter(x=fig6.data[0]['x'], y=fig6.data[0]['y'], mode='lines', name='Ref - FFT'), row=1, col=2)
        print("i")
        # Frequency Error - ref
        fig7 = px.line(x=self.white_list, y=self.ref_frequency_error, title='Frequency Error')
        fig.add_trace(go.Scatter(x=fig7.data[0]['x'], y=fig7.data[0]['y'], name='Ref - Frequency Error'), row=2, col=1)
        print("j")
        # RMS of Noise - ref
        fig8 = px.line(x=self.ref_detected_peaks_bin, y=self.ref_rms, title='RMS of Noise')
        fig.add_trace(go.Scatter(x=fig8.data[0]['x'], y=fig8.data[0]['y'], name='Ref - RMS'), row=2, col=2)

        # Update layout for better positioning and visibility
        fig.update_layout(
            showlegend=True,
            xaxis=dict(title='Time [sec]'),
            yaxis=dict(title='Acceleration [mG]'),
            xaxis2=dict(title='Frequency [Hz]'),
            yaxis2=dict(title='Magnitude [mG]'),
            xaxis3=dict(title='Frequency [Hz]'),
            yaxis3=dict(title='Error [Hz]'),
            xaxis4=dict(title='Frequency [Hz]'),
            yaxis4=dict(title='Amplitude [mG]')
        )
        #fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
        fig.write_html('Test_Run_Result.html', auto_open=True)

        # Save the combined plot as an HTML file
        html_file_path = os.path.join('Shaker_results_Amit_Write12345a.html')
        print(html_file_path)
        fig.write_html(html_file_path)
        #fig.write_html('ASAS.html')
        print("save to file")


# call him from gui ! - > open in the end !

# A = Vibration_Analysis()
# A.run_vibration_analysis(report_path= "report", method="wave_packet", white_list= "89, 281, 479, 677, 877, 1069, 1259, 1459, 1657, 1847, 2039, 2237, 2437, 2633, 2833, 3023, 3217, 3413, 3613, 3803, 4001, 4201, 4397, 4591, 4793, 4993, 5189, 5387, 5573, 5779, 5953, 6151",
#                          shaker_reports_full_path="piezo.json", shaker_tool_only='false')