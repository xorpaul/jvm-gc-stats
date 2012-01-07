import re
import copy
import thread
import os.path
from string import maketrans
try:
    import json
except ImportError:
    import simplejson as json

import Tailer

class Parser(object):
    # Singleton pattern
    # http://stackoverflow.com/a/1810367/682847
    __lockObj = thread.allocate_lock()  # lock object
    __instance = None  # the unique instance
    __init = None  # the unique instance
    def __new__(self, *args, **kwargs):
        #print "ID Parser obj:", id(self), "- Parser new"
        if not self.__instance:
            self.__instance = super(Parser, self).__new__(self)
        return self.__instance

    def __init__(self):
        #print "ID Parser obj:", id(self), "- Parser init"
        if not self.__init:
            datum = {}
            self.pid = None
            # http://stackoverflow.com/a/39858/682847
            # Needed to set default values for dictionary, 
            # otherwise I would get KeyErrors when trying to 
            # sum up numbers in getMetrics
            self.data = DefaultDict(DefaultDict(0.0), **DefaultDict(0.0))
            self.data['errors'] = 0
            self.__init = True

        return

    def setPid(self, pid):
        if pid < 2:
            raise Exception("Java process id '%i' < 2 not possible!" % pid)
        if os.path.exists("/proc/"):
            if not os.path.exists("/proc/%i" % pid):
                raise Exception("pid '%i' does not exist!" % pid)

        print "jstating pid %i" % pid
        self.pid = pid
        return

    def getPid(self):
        return self.pid

    def follow(self, t):
        loglines = t.tail()
        for line in loglines:
            self.parse(line)

    def parse(self, line):
        regexParNew = re.compile(r"(.*: )?\d+\.\d+: \[GC \d+\.\d+: \[ParNew: (\d+)K\->(\d+)K\(\d+K\), \d+\.\d+ secs\] (\d+)K\->(\d+)K\(\d+K\), \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        #2011-12-02T22:54:14.955+0100: 39.331: [GC 39.331: [ParNew: 57344K->7619K(57344K), 0.4781460 secs] 63799K->21896K(516096K), 0.4905760 secs] [Times: user=0.38 sys=0.00, real=0.49 secs]
        regexProFail = re.compile(r"(.*: )?\d+\.\d+: \[GC \d+\.\d+: \[ParNew \(promotion failed\): (\d+)K->(\d+)K\(\d+K\), \d+\.\d+ secs\]\d+\.\d+: \[CMS: (\d+)K->(\d+)K\(\d+K\), \d+\.\d+ secs\] (\d+)K->(\d+)K\(\d+K\), \[CMS Perm : (\d+)K->(\d+)K\(\d+K\)\], \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexPSY = re.compile(r"(.*: )?\d+\.\d+: \[GC \[PSYoungGen: (\d+)K->(\d+)K\(\d+K\)\] (\d+)K->(\d+)K\(\d+K\), \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexCMS = re.compile(r"(.*: )?\d+\.\d+: \[(CMS-concurrent-mark-start|CMS-concurrent-preclean-start|CMS-concurrent-abortable-preclean-start|CMS-concurrent-sweep-start|CMS-concurrent-reset-start)\]")
        regexCMSr = re.compile(r"(.*: )?\d+\.\d+: \[GC\[YG occupancy: \d+ K \(\d+ K\)\]\d+\.\d+: \[Rescan \(parallel\) , \d+\.\d+ secs\]\d+\.\d+: \[weak refs processing, \d+\.\d+ secs\] \[1 CMS-remark: \d+K\(\d+K\)\] \d+K\(\d+K\), \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexCMSi = re.compile(r"(.*: )?\d+\.\d+: \[GC \[1 CMS\-initial\-mark: \d+K\(\d+K\)\] \d+K\(\d+K\), \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexCMSc = re.compile(r"(.*: )?\d+\.\d+: \[(CMS-concurrent-abortable-preclean|CMS-concurrent-preclean|CMS-concurrent-mark): \d+\.\d+\/\d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexCMScs = re.compile(r"(.*: )?\d+\.\d+: \[(CMS-concurrent-reset|CMS-concurrent-sweep): \d+\.\d+\/\d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexFull = re.compile(r"(.*: )?\d+\.\d+: \[Full GC(?: \(System\))? \d+\.\d+: \[CMS: (\d+)K->(\d+)K\(\d+K\), \d+\.\d+ secs\] (\d+)K->(\d+)K\(\d+K\), \[CMS Perm : (\d+)K->(\d+)K\(\d+K\)\], \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexFulln = re.compile(r"(.*: )?\d+\.\d+: \[Full GC \[PSYoungGen: (\d+)K->(\d+)K\(\d+K\)\] \[ParOldGen: (\d+)K->(\d+)K\(\d+K\)\] (\d+)K->(\d+)K\(\d+K\) \[PSPermGen: (\d+)K->(\d+)K\(\d+K\)\], \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexFullc = re.compile(r"(.*: )?\d+\.\d+: \[Full GC \d+\.\d+: \[CMS \(concurrent mode failure\)\[YG occupancy: \d+ K \(\d+ K\)\]\d+\.\d+: \[weak refs processing, \d+\.\d+ secs\]: (\d+)K->(\d+)K\(\d+K\), \d+\.\d+ secs\] (\d+)K->(\d+)K\(\d+K\), \[CMS Perm : (\d+)K->(\d+)K\(\d+K\)\], \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        #2012-01-03T20:02:05.259+0100: 3.765: [GC 3.765: [ParNew: 14784K->1600K(14784K), 0.0211600 secs] 17799K->6030K(63936K), 0.0212600 secs] [Times: user=0.04 sys=0.00, real=0.02 secs]
        #2012-01-03T20:02:05.509+0100: 4.016: [Full GC 4.016: [CMS (concurrent mode failure)[YG occupancy: 5207 K (14784 K)]4.074: [weak refs processing, 0.0000560 secs]: 4430K->3972K(49152K), 0.0758790 secs] 9638K->9179K(63936K), [CMS Perm : 16383K->16383K(16384K)], 0.0760660 secs] [Times: user=0.11 sys=0.02, real=0.07 secs]
        regexIgnore = re.compile(r"\s*(par|eden|from|to|concurrent)")

        datum = {}
        if regexParNew.match(line):
            datum['type'] = 'par_new'
            datum['timestamp'] = regexParNew.match(line).group(1)
            datum['newgen_kb_before'] = int(regexParNew.match(line).group(2))
            datum['newgen_kb_after'] = int(regexParNew.match(line).group(3))
            datum['total_kb_before'] = int(regexParNew.match(line).group(4))
            datum['total_kb_after'] = int(regexParNew.match(line).group(5))
            datum['user_time'] = float(regexParNew.match(line).group(6))
            datum['sys_time'] = float(regexParNew.match(line).group(7))
            datum['real_time'] = float(regexParNew.match(line).group(8))

        elif regexProFail.match(line):
            datum['type'] = 'promotion_failure'
            datum['timestamp'] = regexProFail.match(line).group(1)
            datum['newgen_kb_before'] = int(regexProFail.match(line).group(2))
            datum['newgen_kb_after'] = int(regexProFail.match(line).group(3))
            datum['oldgen_kb_before'] = int(regexProFail.match(line).group(4))
            datum['oldgen_kb_after'] = int(regexProFail.match(line).group(5))
            datum['total_kb_before'] = int(regexProFail.match(line).group(6))
            datum['total_kb_after'] = int(regexProFail.match(line).group(7))
            datum['permgen_kb_before'] = int(regexProFail.match(line).group(8))
            datum['permgen_kb_after'] = int(regexProFail.match(line).group(9))
            datum['user_time'] = float(regexProFail.match(line).group(10))
            datum['sys_time'] = float(regexProFail.match(line).group(11))
            datum['real_time'] = float(regexProFail.match(line).group(12))

        elif regexPSY.match(line):
            datum['type'] = 'ps_young_gen'
            datum['timestamp'] = regexPSY.match(line).group(1)
            datum['newgen_kb_before'] = int(regexPSY.match(line).group(2))
            datum['newgen_kb_after'] = int(regexPSY.match(line).group(3))
            datum['total_kb_before'] = int(regexPSY.match(line).group(4))
            datum['total_kb_after'] = int(regexPSY.match(line).group(5))
            datum['user_time'] = float(regexPSY.match(line).group(6))
            datum['sys_time'] = float(regexPSY.match(line).group(7))
            datum['real_time'] = float(regexPSY.match(line).group(8))

        elif regexCMS.match(line):
            datum['timestamp'] = regexCMS.match(line).group(1)
            datum['type'] = self.underscore(regexCMS.match(line).group(2))

        elif regexCMSr.match(line):
            datum['type'] = 'cms_remark'
            datum['timestamp'] = regexCMSr.match(line).group(1)
            datum['user_time'] = float(regexCMSr.match(line).group(2))
            datum['sys_time'] = float(regexCMSr.match(line).group(3))
            datum['real_time'] = float(regexCMSr.match(line).group(4))

        elif regexCMSi.match(line):
            datum['type'] = 'cms_initial_mark'
            datum['timestamp'] = regexCMSi.match(line).group(1)
            datum['user_time'] = float(regexCMSi.match(line).group(2))
            datum['sys_time'] = float(regexCMSi.match(line).group(3))
            datum['real_time'] = float(regexCMSi.match(line).group(4))

        elif regexCMSc.match(line):
            datum['timestamp'] = regexCMSc.match(line).group(1)
            datum['type'] = self.underscore(regexCMSc.match(line).group(2))
            datum['user_time'] = float(regexCMSc.match(line).group(3))
            datum['sys_time'] = float(regexCMSc.match(line).group(4))
            datum['real_time'] = float(regexCMSc.match(line).group(5))

        elif regexCMScs.match(line):
            datum['timestamp'] = regexCMScs.match(line).group(1)
            datum['type'] = self.underscore(regexCMScs.match(line).group(2))
            datum['user_time'] = float(regexCMScs.match(line).group(3))
            datum['sys_time'] = float(regexCMScs.match(line).group(4))
            datum['real_time'] = float(regexCMScs.match(line).group(5))

        elif regexFull.match(line):
            datum['type'] = 'full'
            datum['blocking'] = True
            datum['timestamp'] = regexFull.match(line).group(1)
            datum['oldgen_kb_before'] = int(regexFull.match(line).group(2))
            datum['oldgen_kb_after'] = int(regexFull.match(line).group(3))
            datum['total_kb_before'] = int(regexFull.match(line).group(4))
            datum['total_kb_after'] = int(regexFull.match(line).group(5))
            datum['permgen_kb_before'] = int(regexFull.match(line).group(6))
            datum['permgen_kb_after'] = int(regexFull.match(line).group(7))
            datum['user_time'] = float(regexFull.match(line).group(8))
            datum['sys_time'] = float(regexFull.match(line).group(9))
            datum['real_time'] = float(regexFull.match(line).group(10))

        elif regexFulln.match(line):
            datum['type'] = 'full'
            datum['timestamp'] = regexFulln.match(line).group(1)
            datum['newgen_kb_before'] = int(regexFulln.match(line).group(2))
            datum['newgen_kb_after'] = int(regexFulln.match(line).group(3))
            datum['oldgen_kb_before'] = int(regexFulln.match(line).group(4))
            datum['oldgen_kb_after'] = int(regexFulln.match(line).group(5))
            datum['total_kb_before'] = int(regexFulln.match(line).group(6))
            datum['total_kb_after'] = int(regexFulln.match(line).group(7))
            datum['permgen_kb_before'] = int(regexFulln.match(line).group(8))
            datum['permgen_kb_after'] = int(regexFulln.match(line).group(9))
            datum['user_time'] = float(regexFulln.match(line).group(10))
            datum['sys_time'] = float(regexFulln.match(line).group(11))
            datum['real_time'] = float(regexFulln.match(line).group(12))

        elif regexFullc.match(line):
            datum['type'] = 'full'
            datum['timestamp'] = regexFullc.match(line).group(1)
            datum['oldgen_kb_before'] = int(regexFullc.match(line).group(2))
            datum['oldgen_kb_after'] = int(regexFullc.match(line).group(3))
            datum['total_kb_before'] = int(regexFullc.match(line).group(4))
            datum['total_kb_after'] = int(regexFullc.match(line).group(5))
            datum['permgen_kb_before'] = int(regexFullc.match(line).group(6))
            datum['permgen_kb_after'] = int(regexFullc.match(line).group(7))
            datum['user_time'] = float(regexFullc.match(line).group(8))
            datum['sys_time'] = float(regexFullc.match(line).group(9))
            datum['real_time'] = float(regexFullc.match(line).group(10))

        elif regexIgnore.match(line):
            pass

        else:
            print Exception("couldn't parse line: %s" % line)
            self.data['errors'] += 1

        #print "datum:", datum
        if datum:      # check if a regex did match
            # Critical section start
            self.__lockObj.acquire()
            type = datum['type']
            #print "type:", type
            if type == 'par_new':
                self.data[type]['real_time'] += datum['real_time']
                self.data[type]['sys_time'] += datum['sys_time']
                self.data[type]['user_time'] += datum['user_time']
                self.data[type]['newgen_kb_collected'] += datum['newgen_kb_before'] - datum['newgen_kb_after']
                self.data[type]['total_kb_collected'] += datum['total_kb_before'] - datum['total_kb_after']
                self.data[type]['count'] += 1

            elif type == 'ps_young_gen':
                self.data[type]['real_time'] += datum['real_time']
                self.data[type]['sys_time'] += datum['sys_time']
                self.data[type]['user_time'] += datum['user_time']
                self.data[type]['newgen_kb_collected'] += datum['newgen_kb_before'] - datum['newgen_kb_after']
                self.data[type]['total_kb_collected'] += datum['total_kb_before'] - datum['total_kb_after']
                self.data[type]['count'] += 1

            elif type == 'promotion_failure':
                self.data[type]['real_time'] += datum['real_time']
                self.data[type]['sys_time'] += datum['sys_time']
                self.data[type]['user_time'] += datum['user_time']
                self.data[type]['newgen_kb_collected'] += datum['newgen_kb_before'] - datum['newgen_kb_after']
                self.data[type]['oldgen_kb_collected'] += datum['oldgen_kb_before'] - datum['oldgen_kb_after']
                self.data[type]['permgen_kb_collected'] += datum['permgen_kb_before'] - datum['permgen_kb_after']
                self.data[type]['total_kb_collected'] += datum['total_kb_before'] - datum['total_kb_after']
                self.data[type]['count'] += 1

            elif type == 'full':
                self.data[type]['real_time'] += datum['real_time']
                self.data[type]['sys_time'] += datum['sys_time']
                self.data[type]['user_time'] += datum['user_time']
                self.data[type]['total_kb_collected'] += datum['total_kb_before'] - datum['total_kb_after']
                self.data[type]['oldgen_kb_collected'] += datum['oldgen_kb_before'] - datum['oldgen_kb_after']
                self.data[type]['permgen_kb_collected'] += datum['permgen_kb_before'] - datum['permgen_kb_after']
                self.data[type]['total_kb_collected'] += datum['total_kb_before'] - datum['total_kb_after']
                self.data[type]['count'] += 1

            elif type in ['cms_initial_mark', 'cms_concurrent_mark', 'cms_concurrent_preclean',
                        'cms_concurrent_abortable_preclean', 'cms_remark', 
                        'cms_concurrent_sweep', 'cms_concurrent_reset']:
                self.data[type]['real_time'] += datum['real_time']
                self.data[type]['sys_time'] += datum['sys_time']
                self.data[type]['user_time'] += datum['user_time']
                self.data[type]['count'] += 1

            datum.clear()
            #print "data:", self.data
            #  Exit from critical section
            self.__lockObj.release()
            # Critical section end
        return

    def getMetrics(self):
        """ Returns the current data in JSON format.

        Gets called from every request.
        """
        return json.dumps(self.data)

    def addMetrics(self, values):
        """ Adds old and perm gen memory utilization from jstat.

        Gets only called if the pid argument was found and the GET
        request URI doesn't contain jstat=0
        """
        # Critical section start
        self.__lockObj.acquire()

        self.data['perm'] = values['perm']
        self.data['old'] = values['old']

        #  Exit from critical section
        self.__lockObj.release()
        # Critical section end
        return

    def getData(self):
        """ Returns the current data from the Parse object.

        Gets only used for the unittest.
        """
        return self.data

    def clearData(self):
        self.data = DefaultDict(DefaultDict(0.0), **DefaultDict(0.0))
        self.data['errors'] = 0
        return

    def underscore(self, camel_cased_word):
        word = str(copy.copy(camel_cased_word))
        word = re.sub('::', '/', word)
        word = re.sub('([A-Z]+)([A-Z][a-z])', '\g<1>_\g<2>', word)
        word = re.sub('([a-z\d])([A-Z])', '\g<1>_\g<2>', word)
        word = word.translate(maketrans('-', '_'))
        word = word.translate(maketrans(' ', '_'))
        return word.lower()


## {{{ http://code.activestate.com/recipes/389639/ (r1)
class DefaultDict(dict):
    """Dictionary with a default value for unknown keys."""
    def __init__(self, default):
        self.default = default

    def __getitem__(self, key):
        if key in self: 
            return self.get(key)
        else:
            ## Need copy in case self.default is something like []
            return self.setdefault(key, copy.deepcopy(self.default))

    def __copy__(self):
        copy = DefaultDict(self.default)
        copy.update(self)
        return copy
## end of http://code.activestate.com/recipes/389639/ }}}

