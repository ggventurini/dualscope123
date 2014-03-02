#!/usr/bin/env python

"""
Oscilloscope + spectrum analyser in Python.

------------------------------------------------------------
Copyright (C) 2008, Roger Fearick, University of Cape Town

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
------------------------------------------------------------

Version 0.7c

Dependencies:
uumpy         -- numerics, fft
PyQt4, PyQwt5 -- gui, graphics
pyaudio       -- sound card     -- Enthought unstable branch!

This code provides an oscillator and spectrum analyzer using
the PC sound card as input.

The interface, based on qwt, uses a familar 'knob based' layout
so that it approximates an analogue scope.

Two traces are provided with imput via the sound card "line in" jack.

Traces can be averaged to reduce influence of noise.
The cross-correlation between the inputs can be computed.
The spectrum analyser has both log (dB) scale and linear scale.
A cross hair status display permits the reading ov values off the screen.
Printing is provided.
"""

# dualscope6.py derived from dualscopy5.py  11/8/05
# adds autocorrelation
# Update for Qt4: 4-11/10/2007 rwf
# dualscope7.py: use pyaudio  27/2/08 rwf

import sys, struct, subprocess
from PyQt4 import Qt
from PyQt4 import Qwt5 as Qwt
from numpy import *
import numpy.fft as FFT

import icons    # part of this package -- toolbar icons

# audio setup
CHUNK = 350    # input buffer size in frames
# FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 25000    # depends on sound card: 96000 might be possible

# scope configuration
BOTHLR=0
LEFT=1
RIGHT=2
soundbuffersize=CHUNK
samplerate=float(RATE)
scopeheight=700
scopewidth=1400
LRchannel=LEFT
PENWIDTH=2

# status messages
freezeInfo = 'Freeze: Press mouse button and drag'
cursorInfo = 'Cursor Pos: Press mouse button in plot region'

class ethernet_interface:
	def __init__(self):
		self.HOSTNAME = 'pcbe15055'
		self.PORT = '2307'
		self.FILENAME = 'receive'
	def read(self, nchunks, verbose=True):
		cmd = ["./"+self.FILENAME, self.HOSTNAME, self.PORT, str(int(nchunks))]
		p = subprocess.Popen(cmd, stdin=None, stdout=subprocess.PIPE)
		if verbose:
			print cmd
		data = p.communicate()[0]
		print "Received %d bytes (%d frames, %d chunks)" % (len(data), len(data)/8, len(data)/8/350)
		return data

# utility classes
class LogKnob(Qwt.QwtKnob):
    """
    Provide knob with log scale
    """
    def __init__(self, *args):
        apply(Qwt.QwtKnob.__init__, (self,) + args)
        self.setScaleEngine(Qwt.QwtLog10ScaleEngine())

    def setRange(self,minR,maxR):
        self.setScale(minR,maxR)
        Qwt.QwtKnob.setRange(self, log10(minR), log10(maxR), 0.333333)

    def setValue(self,val):
        Qwt.QwtKnob.setValue(self,log10(val))

class LblKnob:
    """
    Provide knob with a label
    """
    def __init__(self, wgt, x,y, name, logscale=0):
        if logscale:
            self.knob=LogKnob(wgt)
        else:
            self.knob=Qwt.QwtKnob(wgt)
        color=Qt.QColor(200,200,210)
        self.knob.palette().setColor(Qt.QPalette.Active,
                                     Qt.QPalette.Button,
                                     color )
        self.lbl=Qt.QLabel(name, wgt)
        self.knob.setGeometry(x, y, 140, 100)
        # oooh, eliminate this ...
        if name[0]=='o': self.knob.setKnobWidth(40)
        self.lbl.setGeometry(x, y+90, 140, 15)
        self.lbl.setAlignment(Qt.Qt.AlignCenter)

    def setRange(self,*args):
        apply(self.knob.setRange, args)

    def setValue(self,*args):
        apply(self.knob.setValue, args)

    def setScaleMaxMajor(self,*args):
        apply(self.knob.setScaleMaxMajor, args)

class Scope(Qwt.QwtPlot):
    """
    Oscilloscope display widget
    """
    def __init__(self, *args):
        apply(Qwt.QwtPlot.__init__, (self,) + args)

        self.setTitle('Scope');
        self.setCanvasBackground(Qt.Qt.white)

        # grid
        self.grid = Qwt.QwtPlotGrid()
        self.grid.enableXMin(True)
        self.grid.setMajPen(Qt.QPen(Qt.Qt.gray, 0, Qt.Qt.SolidLine))
        self.grid.attach(self)

        # axes
        self.enableAxis(Qwt.QwtPlot.yRight);
        self.setAxisTitle(Qwt.QwtPlot.xBottom, 'Time [s]');
        self.setAxisTitle(Qwt.QwtPlot.yLeft, 'Amplitude []');
        self.setAxisMaxMajor(Qwt.QwtPlot.xBottom, 10);
        self.setAxisMaxMinor(Qwt.QwtPlot.xBottom, 0);

        self.setAxisScaleEngine(Qwt.QwtPlot.yRight, Qwt.QwtLinearScaleEngine());
        self.setAxisMaxMajor(Qwt.QwtPlot.yLeft, 10);
        self.setAxisMaxMinor(Qwt.QwtPlot.yLeft, 0);
        self.setAxisMaxMajor(Qwt.QwtPlot.yRight, 10);
        self.setAxisMaxMinor(Qwt.QwtPlot.yRight, 0);

        # curves for scope traces: 2 first so 1 is on top      
        self.curve2 = Qwt.QwtPlotCurve('Trace2')
        self.curve2.setPen(Qt.QPen(Qt.Qt.magenta,PENWIDTH))
        self.curve2.setYAxis(Qwt.QwtPlot.yRight)
        self.curve2.attach(self)

        self.curve1 = Qwt.QwtPlotCurve('Trace1')
        self.curve1.setPen(Qt.QPen(Qt.Qt.blue,PENWIDTH))
        self.curve1.setYAxis(Qwt.QwtPlot.yLeft)
        self.curve1.attach(self)

        # default settings
        self.triggerval=0.0
        self.maxamp=100.0
        self.maxamp2=100.0
        self.freeze=0
        self.average=0
        self.autocorrelation=0
        self.avcount=0
        self.datastream = None
        self.offset1=0.0
        self.offset2=0.0
	self.maxtime = 0.1

        # set data 
        # NumPy: f, g, a and p are arrays!
        self.dt=1.0/samplerate
        self.f = arange(0.0, 10.0, self.dt)
        self.a1 = 0.0*self.f
        self.a2 = 0.0*self.f
        self.curve1.setData(self.f, self.a1)
        self.curve2.setData(self.f, self.a2)

        # start self.timerEvent() callbacks running
        self.startTimer(100)
        # plot
        self.replot()

    # convenience methods for knob callbacks
    def setMaxAmp(self, val):
        self.maxamp=val

    def setMaxAmp2(self, val):
        self.maxamp2=val

    def setMaxTime(self, val):
        self.maxtime=val

    def setOffset1(self, val):
        self.offset1=val

    def setOffset2(self, val):
        self.offset2=val

    def setTriggerLevel(self, val):
        self.triggerval=val

    # plot scope traces
    def setDisplay(self):
        l=len(self.a1)
	print l
        if LRchannel==BOTHLR:
            self.curve1.setData(self.f[0:l], self.a1[:l]+self.offset1*self.maxamp)
            self.curve2.setData(self.f[0:l], self.a2[:l]+self.offset2*self.maxamp2)
        elif LRchannel==RIGHT:
            self.curve1.setData([0.0,0.0], [0.0,0.0])
            self.curve2.setData(self.f[0:l], self.a2[:l]+self.offset2*self.maxamp2)
        elif LRchannel==LEFT:
            self.curve1.setData(self.f[0:l], self.a1[:l]+self.offset1*self.maxamp)
            self.curve2.setData([0.0,0.0], [0.0,0.0])
        self.replot()

    def getValue(self, index):
        return self.f[index],self.a[index]
            
    def setAverage(self, state):
        self.average = state
        self.avcount=0

    def setAutoc(self, state):
        self.autocorrelation = state
        self.avcount=0

    def setFreeze(self, freeze):
        self.freeze = 1-self.freeze

    def setDatastream(self, datastream):
        self.datastream = datastream

    # timer callback that does the work
    def timerEvent(self,e):   # Scope
        if self.datastream == None: return
	#print "Reading %d" % (CHUNK*8, )
	print self.maxtime
	points = ceil(self.maxtime*RATE)
	nchunks = ceil(points/CHUNK)
	print "Reading %d bytes (%d frames, %d chunks)" % (8*nchunks*CHUNK, CHUNK*nchunks, nchunks)
        x=self.datastream.read(nchunks)
        if self.freeze==1 or self.avcount>16: return
	if x is None or not len(x): return
	X = array(struct.unpack('<'+('i'*nchunks*CHUNK), x.decode('hex')))
	print X
        if len(X) == 0: return
        P=array(X,dtype=int32)#/32768.0
        val=self.triggerval*self.maxamp
        i=0
        R=P
        L=zeros(P.shape)

        if self.autocorrelation:
            lenX=len(R)
            if lenX == 0: return
            if lenX!=soundbuffersize:
                print lenX
            window=blackman(lenX)
            A1=FFT.fft(R*window) #lenX
            A2=FFT.fft(L*window) #lenX
            B2=(A1*conjugate(A2))/10.0
            R=FFT.ifft(B2).real
        else: # normal scope
            # set trigger levels
            for i in range(len(R)-1):
                if R[i]<val and R[i+1]>=val: break
            if i > len(R)-2: i=0
            #R=R[i:]
            #L=L[i:]
            
        if self.average == 0:
            self.a1=R
            self.a2=L
        else:
            self.avcount+=1
            if self.avcount==1:
                self.sumR=R
                self.sumL=L
            else:
                lp=min(len(R),len(self.sumR))
                self.sumR=self.sumR[:lp]+R[:lp]
                self.sumL=self.sumL[:lp]+L[:lp]
            self.a1=self.sumR/self.avcount
            self.a2=self.sumL/self.avcount
        self.setDisplay()


inittime=0.01
initamp=0.1
class ScopeFrame(Qt.QFrame):
    """
    Oscilloscope widget --- contains controls + display
    """
    def __init__(self, *args):
        apply(Qt.QFrame.__init__, (self,) + args)
        # the following: setPal..  doesn't seem to work on Win
        try:
            self.setPaletteBackgroundColor( QColor(240,240,245))
        except: pass
        hknobpos=scopewidth+10
        vknobpos=scopeheight+30
        self.setFixedSize(scopewidth+150, scopeheight+150)
        self.freezeState = 0
        self.knbLevel = LblKnob(self,hknobpos,50,"Trigger level")
        self.knbTime = LblKnob(self,hknobpos, 220,"Time", 1) 
        self.knbSignal = LblKnob(self,150, vknobpos, "Signal1",1)
        self.knbSignal2 = LblKnob(self,450, vknobpos, "Signal2",1)
        self.knbOffset1=LblKnob(self,10, vknobpos,"offset1")
        self.knbOffset2=LblKnob(self,310, vknobpos,"offset2")

        self.knbTime.setRange(0.0001, 1.0)
        self.knbTime.setValue(0.01)

        self.knbSignal.setRange(0.1, 1000.0)
        self.knbSignal.setValue(10.0)

        self.knbSignal2.setRange(0.1, 1000.0)
        self.knbSignal2.setValue(10.0)

        self.knbOffset2.setRange(-1.0, 1.0, 0.001)
        self.knbOffset2.setValue(0.0)

        self.knbOffset1.setRange(-1.0, 1.0, 0.001)
        self.knbOffset1.setValue(0.0)


        self.knbLevel.setRange(-1.0, 1.0, 0.001)
        self.knbLevel.setValue(0.1)
        self.knbLevel.setScaleMaxMajor(10)

        self.plot = Scope(self)
        self.plot.setGeometry(10, 10, scopewidth, scopeheight)
        self.picker = Qwt.QwtPlotPicker(
            Qwt.QwtPlot.xBottom,
            Qwt.QwtPlot.yLeft,
            Qwt.QwtPicker.PointSelection | Qwt.QwtPicker.DragSelection,
            Qwt.QwtPlotPicker.CrossRubberBand,
            Qwt.QwtPicker.ActiveOnly, #AlwaysOn,
            self.plot.canvas())
        self.picker.setRubberBandPen(Qt.QPen(Qt.Qt.green))
        self.picker.setTrackerPen(Qt.QPen(Qt.Qt.cyan))

        self.connect(self.knbTime.knob, Qt.SIGNAL("valueChanged(double)"),
                     self.setTimebase)
        self.knbTime.setValue(0.01)
        self.connect(self.knbSignal.knob, Qt.SIGNAL("valueChanged(double)"),
                     self.setAmplitude)
        self.connect(self.knbSignal2.knob, Qt.SIGNAL("valueChanged(double)"),
                     self.setAmplitude2)
        self.knbSignal.setValue(0.1)
        self.connect(self.knbLevel.knob, Qt.SIGNAL("valueChanged(double)"),
                     self.setTriggerlevel)
        self.connect(self.knbOffset1.knob, Qt.SIGNAL("valueChanged(double)"),
                     self.plot.setOffset1)
        self.connect(self.knbOffset2.knob, Qt.SIGNAL("valueChanged(double)"),
                     self.plot.setOffset2)
        self.knbLevel.setValue(0.1)
        self.plot.setAxisScale( Qwt.QwtPlot.xBottom, 0.0, 10.0*inittime)
        self.plot.setAxisScale( Qwt.QwtPlot.yLeft, -5.0*initamp, 5.0*initamp)
        self.plot.setAxisScale( Qwt.QwtPlot.yRight, -5.0*initamp, 5.0*initamp)
        self.plot.show()


    def _calcKnobVal(self,val):
        ival=floor(val)
        frac=val-ival
        if frac >=0.9:
            frac=1.0
        elif frac>=0.66:
            frac=log10(5.0)
        elif frac>=log10(2.0):
            frac=log10(2.0)
        else: frac=0.0
        dt=10**frac*10**ival
        return dt

    def setTimebase(self, val):
        dt=self._calcKnobVal(val)
        self.plot.setAxisScale( Qwt.QwtPlot.xBottom, 0.0, 10.0*dt)
	self.plot.setMaxTime(dt*10.0)
        self.plot.replot()

    def setAmplitude(self, val):
        dt=self._calcKnobVal(val)
        self.plot.setAxisScale( Qwt.QwtPlot.yLeft, -5.0*dt, 5.0*dt)
        self.plot.setMaxAmp( 5.0*dt )
        self.plot.replot()

    def setAmplitude2(self, val):
        dt=self._calcKnobVal(val)
        self.plot.setAxisScale( Qwt.QwtPlot.yRight, -5.0*dt, 5.0*dt)
        self.plot.setMaxAmp2( 5.0*dt )
        self.plot.replot()

    def setTriggerlevel(self, val):
        self.plot.setTriggerLevel(val)
        self.plot.setDisplay()


#--------------------------------------------------------------------

class FScope(Qwt.QwtPlot):
    """
    Power spectrum display widget
    """
    def __init__(self, *args):
        apply(Qwt.QwtPlot.__init__, (self,) + args)

        self.setTitle('Power spectrum');
        self.setCanvasBackground(Qt.Qt.white)

        # grid 
        self.grid = Qwt.QwtPlotGrid()
        self.grid.enableXMin(True)
        self.grid.setMajPen(Qt.QPen(Qt.Qt.gray, 0, Qt.Qt.SolidLine));
        self.grid.attach(self)

        # axes
        self.setAxisTitle(Qwt.QwtPlot.xBottom, 'Frequency [Hz]');
        self.setAxisTitle(Qwt.QwtPlot.yLeft, 'Power [dB]');
        self.setAxisMaxMajor(Qwt.QwtPlot.xBottom, 10);
        self.setAxisMaxMinor(Qwt.QwtPlot.xBottom, 0);
        self.setAxisMaxMajor(Qwt.QwtPlot.yLeft, 10);
        self.setAxisMaxMinor(Qwt.QwtPlot.yLeft, 0);

        # curves
        self.curve2 = Qwt.QwtPlotCurve('PSTrace2')
        self.curve2.setPen(Qt.QPen(Qt.Qt.magenta,PENWIDTH))
        self.curve2.setYAxis(Qwt.QwtPlot.yLeft)
        self.curve2.attach(self)
        
        self.curve1 = Qwt.QwtPlotCurve('PSTrace1')
        self.curve1.setPen(Qt.QPen(Qt.Qt.blue,PENWIDTH))
        self.curve1.setYAxis(Qwt.QwtPlot.yLeft)
        self.curve1.attach(self)
        
        self.triggerval=0.0
        self.maxamp=1.0
        self.freeze=0
        self.average=0
        self.avcount=0
        self.logy=1
        self.datastream=None
        
        self.dt=1.0/samplerate
        self.df=1.0/(soundbuffersize*self.dt)
        self.f = arange(0.0, samplerate, self.df)
        self.a = 0.0*self.f
        self.p = 0.0*self.f
        self.curve1.setData(self.f, self.a)
        self.setAxisScale( Qwt.QwtPlot.xBottom, 0.0, 10.0*initfreq)
        self.setAxisScale( Qwt.QwtPlot.yLeft, -120.0, 0.0)

        self.startTimer(100)
        self.replot()

    def resetBuffer(self):
        self.df=1.0/(soundbuffersize*self.dt)
        self.f = arrayrange(0.0, 20000.0, self.df)
        self.a = 0.0*self.f
        self.p = 0.0*self.f
        self.curve1.setData(self.curve1, self.f, self.a)
        
    def setMaxAmp(self, val):
        if val>0.6:
            self.setAxisScale( Qwt.QwtPlot.yLeft, -120.0, 0.0)
            self.logy=1
        else:
            self.setAxisScale( Qwt.QwtPlot.yLeft, 0.0, 10.0*val)
            self.logy=0
        self.maxamp=val

    def setMaxTime(self, val):
        self.maxtime=val

    def setTriggerLevel(self, val):
        self.triggerval=val
        
    def setDisplay(self):
        n=soundbuffersize/2
        if LRchannel==BOTHLR:
            self.curve1.setData(self.f[0:n], self.a[:n])
            self.curve2.setData(self.f[0:n], self.a2[:n])
        elif LRchannel==RIGHT:
            self.curve1.setData([0.0,0.0], [0.0,0.0])
            self.curve2.setData(self.f[0:n], self.a2[:n])
        elif LRchannel==LEFT:
            self.curve1.setData(self.f[0:n], self.a[:n])
            self.curve2.setData([0.0,0.0], [0.0,0.0])
        self.replot()
        
    def getValue(self, index):
        return self.f[index],self.a[index]
            
    def setAverage(self, state):
        self.average = state
        self.avcount=0

    def setFreeze(self, freeze):
        self.freeze = 1-self.freeze

    def setDatastream(self, datastream):
        self.datastream = datastream

    def timerEvent(self,e):     # FFT
        if self.datastream == None: return
        x=self.datastream.read(CHUNK)
        if self.freeze==1: return
        X=fromstring(x,dtype='h')
        if len(X) == 0: return
        P=array(X,dtype='d')/32768.0
        val=self.triggerval*self.maxamp
        i=0
        R=P[0::2]
        L=P[1::2]
        lenX=len(R)
        if lenX == 0: return
        if lenX!=(CHUNK): print 'size fail',lenX
        window=blackman(lenX)
        sumw=sum(window*window)
        A=FFT.fft(R*window) #lenX
        B=(A*conjugate(A)).real
        A=FFT.fft(L*window) #lenX
        B2=(A*conjugate(A)).real
        sumw*=2.0   # sym about Nyquist (*4); use rms (/2)
        sumw/=self.dt  # sample rate
        B=B/sumw
        B2=B2/sumw
        if self.logy:
            P1=log10(B)*10.0+20.0#60.0
            P2=log10(B2)*10.0+20.0#60.0
        else:
            P1=B
            P2=B2
        if self.average == 0:
            self.a=P1
            self.a2=P2
        else:
            self.avcount+=1
            if self.avcount==1:
                self.sumP1=P1
                self.sumP2=P2
            else:
                self.sumP1=self.sumP1+P1
                self.sumP2=self.sumP2+P2
            self.a=self.sumP1/self.avcount
            self.a2=self.sumP2/self.avcount
        self.setDisplay()

initfreq=100.0
class FScopeFrame(Qt.QFrame):
    """
    Power spectrum widget --- contains controls + display
    """
    def __init__(self , *args):
        apply(Qt.QFrame.__init__, (self,) + args)
        vknobpos=scopeheight+30
        hknobpos=scopewidth+10
        # the following: setPal..  doesn't seem to work on Ein
        try:
            self.setPaletteBackgroundColor( QColor(240,240,245))
        except: pass
        self.setFixedSize(scopewidth+150, scopeheight+150)
        self.freezeState = 0

        self.knbSignal = LblKnob(self,160, vknobpos, "Signal",1)
        self.knbTime = LblKnob(self,310, vknobpos,"Frequency", 1) 
        self.knbTime.setRange(1.0, 2000.0)

        self.knbSignal.setRange(0.0000001, 1.0)

        self.plot = FScope(self)
        self.plot.setGeometry(10, 10, scopewidth+150, scopeheight)
        self.picker = Qwt.QwtPlotPicker(
            Qwt.QwtPlot.xBottom,
            Qwt.QwtPlot.yLeft,
            Qwt.QwtPicker.PointSelection | Qwt.QwtPicker.DragSelection,
            Qwt.QwtPlotPicker.CrossRubberBand,
            Qwt.QwtPicker.ActiveOnly, #AlwaysOn,
            self.plot.canvas())
        self.picker.setRubberBandPen(Qt.QPen(Qt.Qt.green))
        self.picker.setTrackerPen(Qt.QPen(Qt.Qt.cyan))

        self.connect(self.knbTime.knob, Qt.SIGNAL("valueChanged(double)"),
                     self.setTimebase)
        self.knbTime.setValue(1000.0)
        self.connect(self.knbSignal.knob, Qt.SIGNAL("valueChanged(double)"),
                     self.setAmplitude)
        self.knbSignal.setValue(1.0)

        self.plot.show()

    def _calcKnobVal(self,val):
        ival=floor(val)
        frac=val-ival
        if frac >=0.9:
            frac=1.0
        elif frac>=0.66:
            frac=log10(5.0)
        elif frac>=log10(2.0):
            frac=log10(2.0)
        else: frac=0.0
        dt=10**frac*10**ival
        return dt

    def setTimebase(self, val):
        dt=self._calcKnobVal(val)
        self.plot.setAxisScale( Qwt.QwtPlot.xBottom, 0.0, 10.0*dt)
        self.plot.replot()

    def setAmplitude(self, val):
        dt=self._calcKnobVal(val)
        self.plot.setMaxAmp( dt )
        self.plot.replot()
        
#---------------------------------------------------------------------

class FScopeDemo(Qt.QMainWindow):
    """
    Application container  widget

    Contains scope and power spectrum analyser in tabbed windows.
    Enables switching between the two.
    Handles toolbar and status.
    """
    def __init__(self, *args):
        apply(Qt.QMainWindow.__init__, (self,) + args)

        self.freezeState = 0
        self.changeState = 0
        self.averageState = 0
        self.autocState = 0

        self.scope = ScopeFrame(self)
        self.current = self.scope
        self.pwspec = FScopeFrame(self)
        self.pwspec.hide()

        self.stack=Qt.QTabWidget(self)
        self.stack.addTab(self.scope,"scope")
        self.stack.addTab(self.pwspec,"fft")
        self.setCentralWidget(self.stack)

        toolBar = Qt.QToolBar(self)
        self.addToolBar(toolBar)
        sb=self.statusBar()
        sbfont=Qt.QFont("Helvetica",12)
        sb.setFont(sbfont)

        self.btnFreeze = Qt.QToolButton(toolBar)
        self.btnFreeze.setText("Freeze")
        self.btnFreeze.setIcon(Qt.QIcon(Qt.QPixmap(icons.stopicon)))
        self.btnFreeze.setCheckable(True)
        self.btnFreeze.setToolButtonStyle(Qt.Qt.ToolButtonTextUnderIcon)
        toolBar.addWidget(self.btnFreeze)

        self.btnPrint = Qt.QToolButton(toolBar)
        self.btnPrint.setText("Print")
        self.btnPrint.setIcon(Qt.QIcon(Qt.QPixmap(icons.print_xpm)))
        self.btnPrint.setToolButtonStyle(Qt.Qt.ToolButtonTextUnderIcon)
        toolBar.addWidget(self.btnPrint)

        self.btnMode = Qt.QToolButton(toolBar)
        self.btnMode.setText("fft")
        self.btnMode.setIcon(Qt.QIcon(Qt.QPixmap(icons.pwspec)))
        self.btnMode.setCheckable(True)
        self.btnMode.setToolButtonStyle(Qt.Qt.ToolButtonTextUnderIcon)
        toolBar.addWidget(self.btnMode)

        self.btnAvge = Qt.QToolButton(toolBar)
        self.btnAvge.setText("average")
        self.btnAvge.setIcon(Qt.QIcon(Qt.QPixmap(icons.avge)))
        self.btnAvge.setCheckable(True)
        self.btnAvge.setToolButtonStyle(Qt.Qt.ToolButtonTextUnderIcon)
        toolBar.addWidget(self.btnAvge)

        self.btnAutoc = Qt.QToolButton(toolBar)
        self.btnAutoc.setText("correlate")
        self.btnAutoc.setIcon(Qt.QIcon(Qt.QPixmap(icons.avge)))
        self.btnAutoc.setCheckable(True)
        self.btnAutoc.setToolButtonStyle(Qt.Qt.ToolButtonTextUnderIcon)
        toolBar.addWidget(self.btnAutoc)

        self.lstLabl = Qt.QLabel("Buffer:",toolBar)
        toolBar.addWidget(self.lstLabl)
        self.lstChan = Qt.QComboBox(toolBar)
        self.lstChan.insertItem(0,"8192")
        self.lstChan.insertItem(1,"16k")
        self.lstChan.insertItem(2,"32k")
        toolBar.addWidget(self.lstChan)
        
        self.lstLR = Qt.QLabel("Channels:",toolBar)
        toolBar.addWidget(self.lstLR)
        self.lstLRmode = Qt.QComboBox(toolBar)
        self.lstLRmode.insertItem(0,"LR")
        self.lstLRmode.insertItem(1,"L")
        self.lstLRmode.insertItem(2,"R")
        toolBar.addWidget(self.lstLRmode)

        self.connect(self.btnPrint, Qt.SIGNAL('clicked()'), self.printPlot)
        self.connect(self.btnFreeze, Qt.SIGNAL('toggled(bool)'), self.freeze)
        self.connect(self.btnMode, Qt.SIGNAL('toggled(bool)'), self.mode)
        self.connect(self.btnAvge, Qt.SIGNAL('toggled(bool)'), self.average)
        self.connect(self.btnAutoc, Qt.SIGNAL('toggled(bool)'),
                        self.autocorrelation)
        self.connect(self.lstChan, Qt.SIGNAL('activated(int)'), self.fftsize)
        self.connect(self.lstLRmode, Qt.SIGNAL('activated(int)'), self.channel)
        self.connect(self.scope.picker,
                        Qt.SIGNAL('moved(const QPoint&)'),
                        self.moved)
        self.connect(self.scope.picker,
                        Qt.SIGNAL('appended(const QPoint&)'),
                        self.appended)
        self.connect(self.pwspec.picker,
                        Qt.SIGNAL('moved(const QPoint&)'),
                        self.moved)
        self.connect(self.pwspec.picker,
                        Qt.SIGNAL('appended(const QPoint&)'),
                        self.appended)
        self.connect(self.stack,
                        Qt.SIGNAL('currentChanged(int)'),
                        self.mode)
        self.showInfo(cursorInfo)

    def showInfo(self, text):
        self.statusBar().showMessage(text)

    def printPlot(self):
        p = QPrinter()
        if p.setup():
            self.current.plot.printPlot(p)#, Qwt.QwtFltrDim(200));

    def fftsize(self, item):
        pass
##         global s, soundbuffersize
##         s.stop()
##         s.close()
##         if item==2:
##             soundbuffersize=8192*3
##         elif item==1:
##             soundbuffersize=8192*2
##         else:
##             soundbuffersize=8192
##         s=f.stream(48000,2,'int16',soundbuffersize,1)
##         s.open()
##         s.start()
##         self.pwspec.plot.resetBuffer()
##         if self.current==self.pwspec:
##             self.pwspec.plot.setDatastream(s)
##             self.pwspec.plot.avcount=0
##         else:
##             self.scope.plot.setDatastream(s)

    def channel(self, item):
        global LRchannel
        if item==2:
            LRchannel=RIGHT
        elif item==1:
            LRchannel=LEFT
        else:
            LRchannel=BOTHLR
        
    def freeze(self, on):
        if on:
            self.freezeState = 1
            self.btnFreeze.setText("Run")
            self.btnFreeze.setIcon(Qt.QIcon(Qt.QPixmap(icons.goicon)))
        else:
            self.freezeState = 0
            self.btnFreeze.setText("Freeze")
            self.btnFreeze.setIcon(Qt.QIcon(Qt.QPixmap(icons.stopicon)))
        self.scope.plot.setFreeze(self.freezeState)
        self.pwspec.plot.setFreeze(self.freezeState)

    def average(self, on):
        if on:
            self.averageState = 1
            self.btnAvge.setText("single")
            self.btnAvge.setIcon(Qt.QIcon(Qt.QPixmap(icons.single)))
        else:
            self.averageState = 0
            self.btnAvge.setText("average")
            self.btnAvge.setIcon(Qt.QIcon(Qt.QPixmap(icons.avge)))
        self.scope.plot.setAverage(self.averageState)
        self.pwspec.plot.setAverage(self.averageState)

    def autocorrelation(self, on):
        if on:
            self.autocState = 1
            self.btnAutoc.setText("normal")
            self.btnAutoc.setIcon(Qt.QIcon(Qt.QPixmap(icons.single)))
        else:
            self.autocState = 0
            self.btnAutoc.setText("correlate")
            self.btnAutoc.setIcon(Qt.QIcon(Qt.QPixmap(icons.avge)))
        self.scope.plot.setAutoc(self.autocState)

    def mode(self, on):
        if on:
            self.changeState=1
            self.current=self.pwspec
            self.btnMode.setText("scope")
            self.btnMode.setIcon(Qt.QIcon(Qt.QPixmap(icons.scope)))
        else:
            self.changeState=0
            self.current=self.scope
            self.btnMode.setText("fft")
            self.btnMode.setIcon(Qt.QIcon(Qt.QPixmap(icons.pwspec)))
        if self.changeState==1:
            self.stack.setCurrentIndex(self.changeState)
            self.scope.plot.setDatastream(None)
            self.pwspec.plot.setDatastream(stream)
        else:
            self.stack.setCurrentIndex(self.changeState)
            self.pwspec.plot.setDatastream(None)
            self.scope.plot.setDatastream(stream)
        
        

    def moved(self, e):
        if self.changeState==1:
            name='Freq'
        else:
            name='Time'
        frequency = self.current.plot.invTransform(Qwt.QwtPlot.xBottom, e.x())
        amplitude = self.current.plot.invTransform(Qwt.QwtPlot.yLeft, e.y())
        if name=='Time':
            df=self.scope.plot.dt
            i=int(frequency/df)
            ampa=self.scope.plot.a1[i]
            ampb=self.scope.plot.a2[i]
        else:
            df=self.pwspec.plot.df
            i=int(frequency/df)
            ampa=self.pwspec.plot.a[i]
            ampb=self.pwspec.plot.a2[i]
        self.showInfo('%s=%g, cursor=%g, A=%g, B=%g' %
                      (name,frequency, amplitude,ampa,ampb))
        
    def appended(self, e):
        print 's'
        # Python semantics: self.pos = e.pos() does not work; force a copy
        self.xpos = e.x()
        self.ypos = e.y()
        self.moved(e)  # fake a mouse move to show the cursor position

# open sound card data stream
stream = ethernet_interface()

# Admire! 
app = Qt.QApplication(sys.argv)
demo=FScopeDemo()
demo.scope.plot.setDatastream(stream)
demo.show()

app.exec_()

