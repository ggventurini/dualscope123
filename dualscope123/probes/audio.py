from .generic import GenericProbe
import numpy
import pyaudio

class Probe(GenericProbe):
	def __init__(self):
		# audio setup
		self.CHUNK = 8192    # input buffer size in frames
		self.FORMAT = pyaudio.paInt16
		self.CHANNELS = 2
		self.RATE = 48000    # depends on sound card: 96000 might be possible
		self.p = None

	def open(self):
		# open sound card data stream
		self.p = pyaudio.PyAudio()
		self.stream = self.p.open(format=self.FORMAT,
				channels=self.CHANNELS,
				rate=self.RATE,
				input=True,
				frames_per_buffer=self.CHUNK)

	def read(self, channel, npoints, verbose=False):
		#nchunks = int(npoints/self.CHUNK) + 1*(npoints % self.CHUNK > 0)
		x = self.stream.read(npoints)
		X = numpy.fromstring(x, dtype='h')
		X = numpy.array(X, numpy.int32)
		if str(channel) == '1':
			return X[::2]
		if str(channel) == '2':
			return X[1::2]
		if str(channel) == '12':
			return X[::2], X[1::2]

	def close(self):
		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()

