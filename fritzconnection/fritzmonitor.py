#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
fritzmonitor.py

Implement a tkinter-based grafic interface to view basic status- and
traffic-informations.

License: MIT https://opensource.org/licenses/MIT
Source: https://bitbucket.org/kbr/fritzconnection
Author: Klaus Bremer
"""

__version__ = '0.5.0'

import argparse
try:
    # python 2
    import Tkinter as tk
    import tkFont as tkfont
except ImportError:
    # python 3
    import tkinter as tk
    import tkinter.font as tkfont
from . import fritzconnection
from . import fritzstatus
from . import fritztools


class MeterRectangle(object):
    """
    a Tkinter meter-rectangel. This is a rectangle with a
    background-color that can be filled up from left to right with
    another color (fill).
    This object must have a canvas-widget as parent.
    """

    def __init__(self, canvas, xpos, ypos, meter_width, meter_height,
                 fill="#0080FF", background="#E6E6E6", horizontal=True,
                 **kwargs):
        self.canvas = canvas
        self.xpos = xpos
        self.ypos = ypos
        self.width = meter_width
        self.height = meter_height
        self.horizontal = horizontal
        self.container = canvas.create_rectangle(xpos, ypos,
                                             xpos + meter_width,
                                             ypos + meter_height,
                                             fill = background,
                                             outline = background,
                                             **kwargs)
        self.meter = canvas.create_rectangle(xpos, ypos,
                                             xpos,
                                             ypos + meter_height,
                                             fill = fill,
                                             outline = fill,
                                             **kwargs)

    def set_fraction(self, value):
        """Set the meter indicator. Value should be between 0 and 1."""
        if value < 0:
            value *= -1
        value = min(value, 1)
        if self.horizontal:
            width = int(self.width * value)
            height = self.height
        else:
            width = self.width
            height = int(self.height * value)
        self.canvas.coords(self.meter, self.xpos, self.ypos,
                           self.xpos + width, self.ypos + height)


class FritzMonitor(tk.Frame):

    def __init__(self, master=None,
                       address=fritzconnection.FRITZ_IP_ADDRESS,
                       port=fritzconnection.FRITZ_TCP_PORT):
        tk.Frame.__init__(self, master)
        self.status = fritzstatus.FritzStatus(address=address, port=port)
        self.max_upstream, self.max_downstream = self.status.max_byte_rate
        self.max_stream_rate = tk.StringVar()
        self.connection_state = tk.StringVar()
        self.ip = tk.StringVar()
        self.uptime = tk.StringVar()
        self.traffic_info = tk.StringVar()
        self.bytes_received = self.status.bytes_received
        self.bytes_sent = self.status.bytes_sent
        self.grid()
        self.create_widgets()
        self.update_status()

    def get_stream_rate_str(self):
        up, down = self.status.str_max_bit_rate
        return "Down: %s, Up: %s" % (down, up)

    def update_connection_status(self):
        if self.status.is_connected:
            color, text = 'green', 'up'
        else:
            color, text = 'red', 'down'
        self.connection_label.config(fg=color)
        self.connection_state.set(text)

    def update_traffic_info(self):
        received = fritztools.format_num(
            self.status.bytes_received - self.bytes_received)
        sent = fritztools.format_num(
            self.status.bytes_sent - self.bytes_sent)
        text = "received: %s, send: %s" % (received, sent)
        self.traffic_info.set(text)

    def update_status(self):
        """Update status informations in tkinter window."""
        try:
            # all this may fail if the connection to the fritzbox is down
            self.update_connection_status()
            self.max_stream_rate.set(self.get_stream_rate_str())
            self.ip.set(self.status.external_ip)
            self.uptime.set(self.status.str_uptime)
            upstream, downstream = self.status.transmission_rate
        except IOError:
            # here we inform the user about being unable to
            # update the status informations
            pass
        else:
            # max_downstream and max_upstream may be zero if the
            # fritzbox is configured as ip-client.
            if self.max_downstream > 0:
                self.in_meter.set_fraction(
                    1.0 * downstream / self.max_downstream)
            if self.max_upstream > 0:
                self.out_meter.set_fraction(1.0 * upstream / self.max_upstream)
            self.update_traffic_info()
        self.after(1000, self.update_status)

    def create_widgets(self):
        self.place_header()
        self.place_meter()
        self.place_traffic_info()
        self.place_connection_info()
        self.place_buttons()

    def place_header(self):
        tk.Label(self, text="%s:" % self.status.modelname).grid(
            row=0, column=0, sticky=tk.NW, padx=5)
        self.connection_label = tk.Label(self,
            textvariable=self.connection_state, fg='red')
        self.connection_label.grid(row=0, column=1)
        tk.Label(self, textvariable=self.max_stream_rate).grid(
            row=1, column=0, sticky=tk.W, padx=5)

    def place_traffic_info(self):
        tk.Label(self, textvariable=self.traffic_info,
                       font=tkfont.Font(family='courier', size=12),
                       fg='grey',
                ).grid(row=2, column=0, columnspan=2,
                       padx=5, pady=5, sticky=tk.W)

    def place_meter(self):
        pane = tk.Canvas(self, height=50)
        pane.grid(row=3, column=0, columnspan=2, sticky=tk.NW, pady=10)
        self.in_meter = MeterRectangle(pane, 10, 10, 240, 12)
        self.out_meter = MeterRectangle(
            pane, 10, 30, 240, 12, fill="#FF6666")

    def place_connection_info(self):
        tk.Label(self, textvariable=self.ip).grid(
            row=4, column=0, sticky=tk.W, padx=5)
        tk.Label(self, textvariable=self.uptime).grid(row=4, column=1)

    def place_buttons(self):
        tk.Button(self, text='Reconnect', command=self.status.reconnect).grid(
            row=5, column=0, sticky=tk.W, padx=10)
        tk.Button(self, text='Quit', command=self.quit).grid(row=5, column=1)


# ---------------------------------------------------------
# cli-section:
# ---------------------------------------------------------

def _get_cli_arguments():
    parser = argparse.ArgumentParser(description='FritzBox Monitor')
    parser.add_argument('-i', '--ip-address',
                        nargs='?', default=fritzconnection.FRITZ_IP_ADDRESS,
                        dest='address',
                        help='ip-address of the FritzBox to connect to. '
                             'Default: %s' % fritzconnection.FRITZ_IP_ADDRESS)
    parser.add_argument('-p', '--port',
                        nargs='?', default=fritzconnection.FRITZ_TCP_PORT,
                        dest='port',
                        help='port of the FritzBox to connect to. '
                             'Default: %s' % fritzconnection.FRITZ_TCP_PORT)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    arguments = _get_cli_arguments()
    app = FritzMonitor(address=arguments.address, port=arguments.port)
    app.master.title('FritzMonitor')
    app.mainloop()
