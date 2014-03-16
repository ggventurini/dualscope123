dualscope123
============

A versatile tiny software oscilloscope + spectrum analyser in Python/qwt

``dualscope123`` was written by Giuseppe Venturini, as a fork of Roger
Fearick's ``dualscope.py``, v. 0.7c.

The interface, based on qwt, uses a familar 'knob based' layout
similarly to that of an analogue scope, only the input data is digital.

The author uses the tool to quickly inspect the data from ADCs under
test. It is here distributed in the hope that it may be useful.

Features
--------

-  Acquisition of two traces,
-  Level-based triggering,
-  Power spectrum,
-  Averaging, in the time and frequency domain,
-  Autocorrelation,
-  A cross hair status display permits the reading of values,
-  Print, generate PDFs and CSV data dumps.

The traces can be averaged to reduce influence of noise. The
cross-correlation between the inputs can be computed. The spectrum
analyser has both log (dB) scale and linear scale. A cross hair status
display permits the reading of values off the screen.

Software probes and extending dualscope123
------------------------------------------

Different software probes may be used, according to what the user wishes
to accomplish with this tool.

A simple, example probe reading the input jack of the audio card is
provided. This probe requires ``pyaudio`` and it should be working on
any machine supported by pyaudio.

The author of this tool (GV) employs a different probe, designed to turn
this oscilloscope into a crude-but-fast debugging tool for prototype
ADCs: a ctypes-based module to read-out over TCP-IP the data buffer of
an FPGA located in the ADC testbench (not part of this project). This
probe is included as well. Although it will be of little to no use to
anybody else, *as is*, it may be used as inspiration to write simliar
network-based software probes.

Two traces are provided, as they seem to allow covering all cases of
interest in my setup, but more may be added easily.

Dependencies:
-------------

-  numpy -- numerics, fft
-  PyQt4, PyQwt5 -- gui, graphics

Copyright
---------

The original ``dualscope.py`` tool, also included in this package is:

::

    Copyright (C) 2008, Roger Fearick, University of Cape Town

All subsequent additions, see ``dualscope123`` are:

::

    Copyright (C) 2010-2014, Giuseppe Venturini

Copying
-------

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 3 of the License.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
