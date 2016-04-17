#!/usr/bin/python3

#     response-plotter.py - plot frequency response graphs
#     Copyright (C) 2016 Ilmo Euro
# 
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pylab import *
from matplotlib import animation
import matplotlib.pyplot as pyplot
import struct
import socket
import time


HEADER_FMT = "<49x1b8x1b21x"
DATA_FMT = "<h"


def get_data():
    sock = socket.socket()
    sock.connect(('10.0.0.3', 3001))
    sock.sendall(b"STARTBIN")
    sock.settimeout(0.1)
    data = b''
    try:
        while True:
            recvd = sock.recv(4096)
            data = data + recvd
    except socket.timeout:
        pass
    sock.close()
    return data


def parse_data(data):
    if len(data) < 80:
        data = b'\0' * 80
    header = data[:0x50]
    payload = data[0x51:]
    print(len(payload))

    if len(payload) % 2 == 1:
        payload = payload[:-1]

    (time_div_encoded, volts_div_encoded) = struct.unpack(HEADER_FMT, header)
    time_div = (1,2,4)[time_div_encoded % 3] * 10 ** (time_div_encoded // 3)
    volts_div = (1,2,5)[volts_div_encoded % 3] * 10 ** (volts_div_encoded // 3)
    signal = (x[0] for x in struct.iter_unpack(DATA_FMT, payload))
    
    return (time_div, volts_div, fromiter(signal, int16))


def calculate_fft(signal):
    length = len(signal)
    signal_2 = concatenate((signal, zeros(length*9)))
    if all(signal_2 == zeros(len(signal_2))):
        signal_2 = array([1, 0, 0, 0])
    fft_signal = rfft(signal_2)[:length//10]
    return (abs(fft_signal), angle(fft_signal))


class FilterTool:

    def __init__(self):
        self.figure = pyplot.figure()
        self.signal_subplot = self.figure.add_subplot(3,1,1)
        self.ampl_subplot = self.figure.add_subplot(3,1,2)
        self.phase_subplot = self.figure.add_subplot(3,1,3)

    def run(self):
        ani = animation.FuncAnimation(self.figure, self._run_once, interval=250)
        show()

    def _run_once(self, i):
        data = get_data()
        _1, _2, signal = parse_data(data)
        ampl, phase = calculate_fft(signal)
        self.plot(signal, ampl, phase)

    def plot(self, signal_data, ampl_data, phase_data):
        self.signal_subplot.clear()
        self.ampl_subplot.clear()
        self.phase_subplot.clear()

        signal_line, = self.signal_subplot.plot(signal_data, color='black')
        ampl_line, = self.ampl_subplot.plot(ampl_data, color='black')
        phase_line, = self.phase_subplot.plot(phase_data, color='black')

        self.ampl_subplot.set_yscale('log')
        self.ampl_subplot.set_xscale('log')

        self.phase_subplot.set_yscale('linear')
        self.phase_subplot.set_xscale('log')


if __name__ == "__main__":
    ft = FilterTool()
    ft.run()
