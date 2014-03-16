from generic import GenericProbe
import ctypes, os
import os.path, ConfigParser
import time, struct
import numpy as np

libname = "libethc.so"
fullpath = os.path.abspath(os.path.join(os.path.dirname(__file__), libname))
print "loading %s" % (fullpath,)
_libfunctions = ctypes.cdll.LoadLibrary(fullpath)
# *read_nios(char *hostname, int port, int ch_number, int chunks_count)
_libfunctions.read_nios.argtypes = [ctypes.c_char_p, ctypes.c_int,  ctypes.c_int,  ctypes.c_int]
_libfunctions.read_nios.restype  =  ctypes.c_char_p

class Probe(GenericProbe):
	def __init__(self):
		# ADC test-bench read-out over ethernet.
		self.CHUNK = 350    # input buffer size in frames
		self.FORMAT = int   # Python int
		self.CHANNELS = 2
		self.RATE = 25000
		self.HOSTNAME = None
		self.port = None

	def open(self):
		conf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'eth_nios.cfg'))
		conf = ConfigParser.ConfigParser()
		if not os.path.isfile(conf_path):
			raise Exception(
                              "Please configure ~/.dualscope123 section" + 
			      "eth_nios with hostname and port")
		conf.read([conf_path])
		if not 'nios_eth' in conf.sections():
			raise ConfigParser.NoSectionError(
                              "Please configure ~/.dualscope123 section" + 
			      "eth_nios with hostname and port")
		self.HOSTNAME = conf.get('eth_nios', 'hostname').strip("\"'")
        	self.PORT = conf.get('eth_nios', 'hostname').strip("\"'")


	def read(self, channel, npoints):
                """Read 'nchunks' chunks from channel 'channel'.

                Args:

                 * channel (int) is the channel # to read from. May be 1 or 2
                   or 12
                 * nchunks (int) is the number of 350 points data chunks to be read
                   consecutively. 1 sample corresponds to 40us.
                 * verbose (boolean, defaults to True) is a flag that triggers,
                   when set to true, verbose print out.
                """
		nchunks = int(npoints/self.CHUNK) + 1*(npoints % self.CHUNK > 0)

		channels = [int(c) for c in str(channels)]
		data = []

		for c in channels:
			if verbose:
				print "Starting: %s %s %s %s" % \
                		    (self.HOSTNAME, int(self.PORT), int(channel), int(nchunks))
			start_time = time.time()
			x = _libfunctions.read_nios(self.HOSTNAME, int(self.PORT), int(channel)-1, int(nchunks))
			end_time = time.time()
			if verbose:
				print "CH%d: received %d bytes (%d frames, %d chunks) at %d kbps" % \
                              (channel, len(x)/2, len(x)/8, len(x)/8/350,
                               4e-3*len(x)/(end_time - start_time))
			data += [np.array(struct.unpack('<'+('i'*nchunks*CHUNK), x.decode('hex')))]
			if verbose:
				print data[-1]
		return data

	def close(self):
		pass

def autosetup():
        """If you're in a hurry, this function will create an interface for you,
           set up with all the defaults, check that it works and return the object
           ready to be used.
        """
        e = ethernet_interface()
        e.read(1, 1)
        print "call e.read(channel, chunks, verbose) to read data."
        return e

if __name__ == "__main__":
        e = autosetup()
