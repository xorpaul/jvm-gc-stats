import time

class Tailer:
    def __init__(self, logfile):
        print "I will follow file: %s" % str(logfile)
        self.fd = open(logfile)

    def follow(self, fd):
        self.fd.seek(0,2)      # Go to the end of the file
        while True:
            line = self.fd.readline()
            if not line:
                time.sleep(0.1)    # Sleep briefly
                continue
            yield line
