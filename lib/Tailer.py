import re
import sys
import time
import glob
import threading
from os import stat, path
from stat import ST_SIZE, ST_DEV, ST_INO

# http://toic.org/blog/2009/08/11/tail-f-in-python-truncate-aware/

class Tailer:
    """ Tails a gc log and yields each line to Parser """

    def __init__(self, logfile, sleep):
        self.sleep = sleep
        self.originalLogfile = logfile
        self.logfile = self.getCurrentLogfile(logfile)
        self.inode = stat(self.logfile)[ST_INO]

        print 'following file: %s' % str(self.logfile)

        try:
            self.fd = open(self.logfile, 'r')
        except IOError, msg:
            sys.stderr.write('ERROR: Can\'t open: %s\n' % (logfile, msg))
            sys.exit(1)

        # fd.tell() returns an integer giving the file object's current position
        # in the file, measured in bytes from the beginning of the file.
        self.pos = self.fd.tell()
        self.fd.seek(0,2)      # Go to the end of the file


    def getCurrentLogfile(self, originalLogfile):
        if float(sys.version[:3]) < 2.5:
          logfiles = sorted(glob.glob(originalLogfile), key=path.getctime)
          if len(logfiles) > 1:
              logfile = logfiles[-1]
          elif len(logfiles) == 1:
              logfile = logfiles[0]

        else:
            # Changed in version 2.5: Added support for
            # the optional key argument
            logfile = max(glob.glob(originalLogfile), key=path.getctime)
        if logfile:
            return logfile
        else:
            sys.stderr.write('ERROR: No logfile found for: %s\n' % logfile)
            sys.exit(1)


    def reset(self):
        """
        Close the old file handler, open the new file 
        and start reading the new file from the top by setting
        self.pos to 0
        """
        self.fd.close()
        self.fd = open(self.logfile, 'r')
        self.pos = 0
        self.inode = stat(self.logfile)[ST_INO]


    def tail(self):
        # array for partial reads that doesn't end with a newline character
        parts = []
        # regex pattern for lines that can be ignored
        #regexIgnoreOnlyTimes = re.compile(r' \[Times: user=\d+\.\d+ sys=\d+\.\d+, real=\d+\.\d+ secs\]')
        regexIgnoreHeap1 = re.compile(r'Heap')
        regexIgnoreHeap2 = re.compile(r'\s*(par|eden|from|to|concurrent)')
        # or for partial lines with -XX:+PrintTenuringDistribution
        regexIgnoreTenuringDist1 = re.compile(r'Desired survivor size \d+ bytes, new threshold \d+ \(max \d+\)')
        regexIgnoreTenuringDist2 = re.compile(r'- age\s+\d+:')

        while True:
            self.pos = self.fd.tell()
            line = self.fd.readline()
            if not line:
                # check is the current file size is smaller
                # than the currently read file size or if the there is a new
                # logfile with a different inode, which indicates
                # a logrotate
                if (stat(self.logfile)[ST_INO] != self.inode
                    or stat(self.logfile)[ST_SIZE] < self.pos):
                    #print 'new inode: %s old inode: %s' % (
                    #    stat(self.logfile)[ST_INO], self.inode)
                    print 'noticed logrotate in', self.logfile
                    self.reset()
                    parts = []
                time.sleep(self.sleep)    # Sleep briefly
                self.fd.seek(self.pos)
                foundLogfile = self.getCurrentLogfile(self.originalLogfile)
                if self.logfile != foundLogfile:
                    print 'noticed logrotate from %s to %s' % (
                            self.logfile, foundLogfile)
                    self.logfile = foundLogfile
                pass

            if line == '\n':
              # Sometimes the newline character is the only thing that
              # was read. It did happen after '12.182: [GC 12.182: [DefNew'
              # was read with PrintTenuringDistribution activated.
              # So I need to skip the rest of the loop, otherwise it
              # would yield just the previous part.

                  #print 'found line containing only newline char:', repr(line)
                  pass

            if line.endswith('New\n') or line.endswith('New'):
                # newline terminated line,
                # but only partial line, because
                # of -XX:+PrintTenuringDistribution

                #print 'found line with 'New\\n' or 'New' at the end:', repr(line)

                # I will chomp the line, because 
                # it is actualy a partial line
                line = line.rstrip('\n')
            if line and line[-1] != '\n':
                # partial read found, because there was no
                # newline char at the end
                parts.append(line)
                #print 'found partial line:', parts
            elif (line and line[-1] == '\n'
                 #and not regexIgnoreOnlyTimes.match(line)
                 and not regexIgnoreHeap1.match(line)
                 and not regexIgnoreHeap2.match(line)
                 and not regexIgnoreTenuringDist1.match(line)
                 and not regexIgnoreTenuringDist2.match(line)):
                # current read has newline char at the end and
                # also checks if current read is 'Heap' if JVM got
                # terminated
                if len(parts) > 0:
                    # there are partial reads left from previous reads
                    for partHead in parts[::-1]:
                        # loops through previous partial reads in reverse order
                        # and merges it at the beginning of the current read
                        #print ('concatenate', repr(partHead), 
                        #    '----AND----', repr(line))
                        line = partHead + line
                    #print 'results in line:', line
                    parts = []  # After we looped through all parts we have to
                              # reset it, so it doesn't get concated again

                # only yield, when there is a newline character at the end
                # and no ignore regex pattern matched
                # the other scenarios should have been taken care of before
                #print 'will yield:', repr(line)
                yield line
