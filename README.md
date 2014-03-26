dualscope123
============

A versatile, tiny oscilloscope + spectrum analyser in Python/qwt

```dualscope123``` is a fork of Roger 
Fearick's ```dualscope.py```.

The interface, based on qwt and uses a 'knob based' layout,
similarly to that found in an analogue scope. 

![screenshot](https://github.com/ggventurini/dualscope123/raw/master/dualscope123.png)

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

## Configuration 

### Software probes

The digital input data is provided by software probes.

Different probes may be used, according to what the user wishes to
accomplish. All supplied probes are located in the submodule
`dualscope123.probes`.

*  A simple, example probe -- named `audio` -- reading the input jack of the
audio card is provided. This probe requires ```pyaudio```.

* I use a different probe, designed to run `dualscope123`
oscilloscope as a crude-but-fast debugging tool for prototype ADCs: 
a ctypes-based module named `eth_nios` 
to read-out over TCP-IP the data buffer of an FPGA located in the ADC testbench 
(not part of this project). This probe is included as well: although it will be
of little to no use to anybody else, *as is*, it may be used as inspiration
to write simliar network-based software probes.

### Writing your own probe

The probes have a standard interface and new probes can be easily coded.
Look into the `audio` probe and the `generic` probe for examples.

### Probe setup

Which probe is employed is selected through a config INI file named
`~/.dualscope123`, read once, at start-up time.

The default configuration is:

```ini
[DEFAULT]
verbose = false

[probes]
probe = audio
```

which contains all configuration base options and is rather self-explanatory.

A probe may require some configuration, in the form of a section named as the
probe containing the relevant options.

## Dependencies:
 * `numpy`         -- numerics, fft
 * `PyQt4`, `PyQwt5` -- gui, graphics

### A quick guide to installing PyQwt5

Installing `PyQwt5` may be complicated the first time one faces the task. Neither `PyQt4` nor `PyQwt5` are on the PYPI.

#### Install the binary libraries.

Straight forward on Linux, on Mac OS X it is greately simplified by using [Homebrew](http://brew.sh/).

```bash
brew install qt qwt portaudio wget
```

#### Create a virtual environment:

If you have the `virtualenv` wrapper installed:

```bash
mkvirtualenv env_qwt
```

or, if you are on Mac and use [Anaconda](https://store.continuum.io/cshop/anaconda/):

```bash
conda create -n qwt_env setuptools
source activate qwt_env
```

If you use another Python environment / package manager please check how to make a virtual environment. Installing in a separate environment allows keeping the changes separate and reistalling in a sec.

#### Install numpy

```bash
pip install numpy
```
or, if you are on Mac and use Anaconda:

```bash
conda install numpy
```

#### Install SIP

As of writing, the latest `SIP` version is `4.15.6-snapshot`. Make sure to check on the [SIP website](http://www.riverbankcomputing.com/) if there is a newer one!

Make sure you configure `SIP` with `--incdir=YOUR_INCLUDE_PATH`. With virtualenv, that is likely `$HOME/.virtualenvs/env_qwt/include`, with Anaconda, `/anaconda/envs/qwt_env/include/`.

Then:

```bash
wget http://www.riverbankcomputing.com/static/Downloads/sip4/sip-4.15.6-snapshot-0c1b13e45887.tar.gz
tar zxf sip-4.15.6-snapshot-0c1b13e45887.tar.gz
cd sip-4.15.6-snapshot-0c1b13e45887/
python configure.py --incdir=$HOME/.virtualenvs/env_qwt/include
make
make install
cd ..
```

Remember that if you update `SIP`, you need to reinstall the following packages as well.

#### Install PyQt4

Make sure to download the latest version for your platform. As of writing, [link for linux](http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.10.4/PyQt-x11-gpl-4.10.4.tar.gz), [link for Mac](http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.10.4/PyQt-mac-gpl-4.10.4.tar.gz). You may want to check if newer versions are available!

```bash
wget http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.10.4/PyQt-x11-gpl-4.10.4.tar.gz
tar zxf PyQt-x11-gpl-4.10.4.tar.gz
cd PyQt-x11-gpl-4.10.4/
python configure.py
make -j9
make install
cd ..
```

#### Install PyQwt5 

```bash
wget "http://downloads.sourceforge.net/project/pyqwt/pyqwt5/PyQwt-5.2.0/PyQwt-5.2.0.tar.gz
tar xvzf PyQwt-5.2.0.tar.gz
cd PyQwt-5.2.0/configure
python configure.py -Q ../qwt-5.2
make -j9
make install
cd ../..
```

Check that PyQwt5 works with:

```bash
python -c 'from PyQt4 import Qwt5'
```

No errors? woohoo, it works!

**Credit:** [David Balbert's pyqwt gist](https://gist.github.com/davidbalbert/5768767).

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


