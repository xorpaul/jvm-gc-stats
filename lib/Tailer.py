import sys
import time
from os import stat
from os.path import abspath
from stat import ST_SIZE, ST_DEV, ST_INO

# http://toic.org/blog/2009/08/11/tail-f-in-python-truncate-aware/

class Tailer:
    def __init__(self, logfile):
        self.logfile = abspath(logfile)
        print "following file: %s" % str(self.logfile)

        try:
          self.fd = open(self.logfile, "r")
        except IOError, msg:
          sys.stderr.write('%s: Can\'t open: %s\n' % (logfile, msg))
          sys.exit(1)

        # fd.tell() returns an integer giving the file object's current 
        # position in the file, measured in bytes from the beginning of the file.
        self.pos = self.fd.tell()


    def reset(self):
        """
        Close the old file handler, open the new file 
        and start reading the new file from the top by setting
        self.pos to 0
        """
        self.fd.close()
        self.fd = open(self.logfile, "r")
        self.pos = 0


    def tail(self):
        # array for partial reads that doesn't end with a newline character
        parts = []
        try:
            self.fd.seek(0,2)      # Go to the end of the file
            while True:
                self.pos = self.fd.tell()
                line = self.fd.readline()
                if not line:
                    # check is the current file size is smaller 
                    # than the currently read file size, which indicates 
                    # a logrotate
                    if stat(self.logfile)[ST_SIZE] < self.pos:
                        print "noticed logrotate"
                        self.reset()
                        parts = []
                    time.sleep(1)    # Sleep briefly
                    self.fd.seek(self.pos)
                    continue
                if line[-1] != '\n':
                    # partial read found, because there was no 
                    # newline char at the end
                    parts.append(line)
                    #print "found partial line:", parts
                elif line[-1] == '\n' and len(parts) > 0 and line != 'Heap\n':
                    # current read has newline char at the end and 
                    # there are partial reads left from previous reads
                    # Also checks if current read is 'Heap' if JVM got
                    # terminated 
                    for partHead in parts[::-1]:
                        # loops through previous partial reads in reverse order
                        # and merges it at the beginning of the current read 
                        line = partHead + line
                        #print "concatinate partHead:", partHead, "and partTail:", partTail
                    parts = []  # After we looped through all parts we have to
                                # reset it, so it doesn't get concated again
                if line[-1] == '\n':
                    # only yield, when there is a newline character at the end
                    # the other scenarios should have been taken care of before
                    yield line
        except KeyboardInterrupt:
            print "Tailer thread exiting..."
