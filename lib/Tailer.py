import sys
import time

class Tailer:
    def __init__(self, logfile):
        print "I will follow file: %s" % str(logfile)
        try:
          self.fd = open(logfile)
        except IOError, msg:
          sys.stderr.write('%s: Can\'t open: %s\n' % (logfile, msg))
          sys.exit(1)


    def follow(self, fd):
        self.fd.seek(0,2)      # Go to the end of the file
        while True:
            line = self.fd.readline()
            if not line:
                time.sleep(0.1)    # Sleep briefly
                continue
            yield line
