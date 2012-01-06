from subprocess import Popen, PIPE

class JstatMonitor:
    def __init__(self, pid):
        self.pid = pid


    def parseJstat(self):
        values = {}

        gccapacityOut = Popen(['jstat', '-gccapacity', '-t', str(self.pid)], 
                    stdout=PIPE).stdout.read().split()
        gcoldOut = Popen(['jstat', '-gcold', '-t', str(self.pid)], 
                    stdout=PIPE).stdout.read().split()

        #print "pid:", self.pid
    
        if (len(gccapacityOut) == 34 and gccapacityOut[3] == 'NGC' 
                and len(gcoldOut) == 18 and gcoldOut[2] == 'PU'):
            gccapacityOut = gccapacityOut[18:]
            gcoldOut = gcoldOut[10:]
            #print "gcoldOut:", gcoldOut
            #print "gccapacityOut:", gccapacityOut
            PU = gcoldOut[1]
            OU = gcoldOut[3]
            PGCMX = gccapacityOut[11]
            OGCMX = gccapacityOut[7]
            permUtil = float(PU)/(float(PGCMX)/100)
            oldUtil = float(OU)/(float(OGCMX)/100)
            #print "P:", permUtil
            #print "O:", oldUtil
            values['perm'] = str(round(permUtil, 2))
            values['old'] = str(round(oldUtil, 2))

        return values
