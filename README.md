dualscope123
============

A versatile, tiny oscilloscope + spectrum analyser in Python/qwt

```dualscope123``` is a fork of Roger 
Fearick's ```dualscope.py```, written by me, Giuseppe Venturini.

The interface, based on qwt and uses a 'knob based' layout,
similarly to that found in an analogue scope. 

This tool may be employed to quickly inspect the data from digital-output 
devices, such as an ADC testbench.

It is here distributed in the hope that it may be useful.

## Features

 * Acquisition of two traces, 
 * Level-based triggering,
 * Power spectrum,
 * Averaging, in the time and frequency domain,
 * Autocorrelation,
 * A cross hair status display permits the reading of values,
 * Print, generate PDFs and CSV data dumps.

The traces can be averaged to reduce influence of noise.
The cross-correlation between the inputs can be computed.
The spectrum analyser has both log (dB) scale and linear scale.
A cross hair status display permits the reading of values off the screen.

## Software probes and extending dualscope123

### Software probes

The digital input data is provided by software probes.

Different probes may be used, according to what the user wishes to
accomplish:

*  A simple, example probe reading the input jack of the audio card is provided.
This probe requires ```pyaudio``` and it should be working on any machine
supported by pyaudio. 

* I personally use a different probe, designed to turn this 
oscilloscope into a crude-but-fast debugging tool for prototype ADCs: 
a ctypes-based module 
to read-out over TCP-IP the data buffer of an FPGA located in the ADC testbench 
(not part of this project). This probe is included as well: although it will be
of little to no use to anybody else, *as is*, it may be used as inspiration
to write simliar network-based software probes.

The probes have a standard interface and new probes can be easily coded.

### More traces

Two traces are provided, as they seem to allow covering all cases of interest
in my setup, but more may be added easily.

## Dependencies:
 * numpy         -- numerics, fft
 * PyQt4, PyQwt5 -- gui, graphics

## Copyright 

The original ```dualscope.py``` tool, also included in this package
is:

    Copyright (C) 2008, Roger Fearick, University of Cape Town

All subsequent additions, see ```dualscope123``` are:

    Copyright (C) 2010-2014, Giuseppe Venturini

## Copying

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; version 3
of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


