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
        partHead = None
        try:
            self.fd.seek(0,2)      # Go to the end of the file
            while True:
                partTail = None
                line = self.fd.readline()
                if not line:
                    time.sleep(1)    # Sleep briefly
                    continue
                if line[-1] != '\n':
                    partHead = line
                    #print "found partial line:", partHead
                elif line[-1] == '\n' and partHead:
                    partTail = line
                    #print "will concatinate part:", partHead, "and partTail:", partTail
                    line = partHead + partTail
                if line[-1] == '\n':
                    yield line
        except KeyboardInterrupt:
            print "Tailer thread exiting..."
