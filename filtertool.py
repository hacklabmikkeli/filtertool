#!/usr/bin/python3
from pylab import *
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
        recvd = sock.recv(4096)
        while len(recvd) > 0:
            print(recvd)
            recvd = sock.recv(4096)
            data = data + recvd
    except socket.timeout:
        pass
    sock.close()
    return data


def parse_data(data):
    header = data[:0x50]
    payload = data[0x51:]

    print(header)
    print(payload)

    (time_div, volts_div) = struct.unpack(HEADER_FMT, header)
    signal = (x[0] for x in struct.iter_unpack(DATA_FMT, payload))
    
    return (time_div, volts_div, fromiter(signal, int16))


def calculate_fft(signal):
    length = len(signal)
    signal = rfft(signal)
    return (abs(signal), angle(signal))


class FilterTool:

    def __init__(self):
        self.signal_subplot = None
        self.ampl_subplot = None
        self.phase_subplot = None

    def run_once(self):
        data = get_data()
        _1, _2, signal = parse_data(data)
        ampl, phase = calculate_fft(signal)
        self.plot(signal, ampl, phase)

    def plot(self, signal_data, ampl_data, phase_data):
        figure = pyplot.figure()
        if self.signal_subplot is None:
            self.signal_subplot = figure.add_subplot(3,1,1)
        if self.ampl_subplot is None:
            self.ampl_subplot = figure.add_subplot(3,1,2)
        if self.phase_subplot is None:
            self.phase_subplot = figure.add_subplot(3,1,3)

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

        show()

if __name__ == "__main__":
    ft = FilterTool()
    ft.run_once()

