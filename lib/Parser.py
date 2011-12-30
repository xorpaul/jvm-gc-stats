import re
import copy
import signal
import thread
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
    def __new__(cls, *args, **kwargs):
        #print "ID Parser obj:", id(cls), "- Parser new"
        if not cls.__instance:
            cls.__instance = super(Parser, cls).__new__(
                                cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        #print "ID Parser obj:", id(self), "- Parser init"
        if not self.__init:
            self.datum = {}
            # http://stackoverflow.com/a/39858/682847
            # Needed to set default values for dictionary, 
            # otherwise I would get KeyErrors when trying to 
            # sum up numbers in getMetrics
            self.data = DefaultDict(DefaultDict(0.0), **DefaultDict(0.0))
            self.data['error']['count'] = 0
            self.__init = True

        return

    def parse(self, t):
        #string = "2011-12-02T22:54:14.955+0100: 39.331: [GC 39.331: [ParNew: 57344K->7619K(57344K), 0.4781460 secs] 63799K->21896K(516096K), 0.4905760 secs] [Times: user=0.38 sys=0.00, real=0.49 secs]"
        regexParNew = re.compile(r"(.*): \d+\.\d+: \[GC \d+\.\d+: \[ParNew: (\d+)K\->(\d+)K\(\d+K\), \d+\.\d+ secs\] (\d+)K\->(\d+)K\(\d+K\), \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]\n")
        regexProFail = re.compile(r"(.*): \d+\.\d+: \[GC \d+\.\d+: \[ParNew \(promotion failed\): (\d+)K->(\d+)K\(\d+K\), \d+\.\d+ secs\]\d+\.\d+: \[CMS: (\d+)K->(\d+)K\(\d+K\), \d+\.\d+ secs\] (\d+)K->(\d+)K\(\d+K\), \[CMS Perm : (\d+)K->(\d+)K\(\d+K\)\], \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexPSY = re.compile(r"(.*): \d+\.\d+: \[GC \[PSYoungGen: (\d+)K->(\d+)K\(\d+K\)\] (\d+)K->(\d+)K\(\d+K\), \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexCMS = re.compile(r"(.*): \d+\.\d+: \[(CMS-concurrent-mark-start|CMS-concurrent-preclean-start|CMS-concurrent-abortable-preclean-start|CMS-concurrent-sweep-start|CMS-concurrent-reset-start)\]")
        regexCMSr = re.compile(r"(.*): \d+\.\d+: \[GC\[YG occupancy: \d+ K \(\d+ K\)\]\d+\.\d+: \[Rescan \(parallel\) , \d+\.\d+ secs\]\d+\.\d+: \[weak refs processing, \d+\.\d+ secs\] \[1 CMS-remark: \d+K\(\d+K\)\] \d+K\(\d+K\), \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexCMSi = re.compile(r"(.*): \d+\.\d+: \[GC \[1 CMS\-initial\-mark: \d+K\(\d+K\)\] \d+K\(\d+K\), \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexCMSc = re.compile(r"(.*): \d+\.\d+: \[(CMS-concurrent-abortable-preclean|CMS-concurrent-preclean|CMS-concurrent-mark): \d+\.\d+\/\d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexCMScs = re.compile(r"(.*): \d+\.\d+: \[(CMS-concurrent-reset|CMS-concurrent-sweep): \d+\.\d+\/\d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexFull = re.compile(r"(.*): \d+\.\d+: \[Full GC \d+\.\d+: \[CMS: (\d+)K->(\d+)K\(\d+K\), \d+\.\d+ secs\] (\d+)K->(\d+)K\(\d+K\), \[CMS Perm : (\d+)K->(\d+)K\(\d+K\)\], \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")
        regexFulln = re.compile(r"(.*): \d+\.\d+: \[Full GC \[PSYoungGen: (\d+)K->(\d+)K\(\d+K\)\] \[ParOldGen: (\d+)K->(\d+)K\(\d+K\)\] (\d+)K->(\d+)K\(\d+K\) \[PSPermGen: (\d+)K->(\d+)K\(\d+K\)\], \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]")

        loglines = t.follow(t.fd)
        for line in loglines:
            if regexParNew.match(line):
                self.datum['type'] = 'ParNew'
                self.datum['timestamp'] = regexParNew.match(line).group(1)
                self.datum['newgen_kb_before'] = int(regexParNew.match(line).group(2))
                self.datum['newgen_kb_after'] = int(regexParNew.match(line).group(3))
                self.datum['total_kb_before'] = int(regexParNew.match(line).group(4))
                self.datum['total_kb_after'] = int(regexParNew.match(line).group(5))
                self.datum['user_time'] = float(regexParNew.match(line).group(6))
                self.datum['sys_time'] = float(regexParNew.match(line).group(7))
                self.datum['real_time'] = float(regexParNew.match(line).group(8))

            elif regexProFail.match(line):
                self.datum['type'] = 'promotion failure'
                self.datum['timestamp'] = regexProFail.match(line).group(1)
                self.datum['newgen_kb_before'] = int(regexProFail.match(line).group(2))
                self.datum['newgen_kb_after'] = int(regexProFail.match(line).group(3))
                self.datum['old_kb_before'] = int(regexProFail.match(line).group(4))
                self.datum['old_kb_after'] = int(regexProFail.match(line).group(5))
                self.datum['total_kb_before'] = int(regexProFail.match(line).group(6))
                self.datum['total_kb_after'] = int(regexProFail.match(line).group(7))
                self.datum['permgen_kb_before'] = int(regexProFail.match(line).group(8))
                self.datum['permgen_kb_after'] = int(regexProFail.match(line).group(9))
                self.datum['user_time'] = float(regexProFail.match(line).group(10))
                self.datum['sys_time'] = float(regexProFail.match(line).group(11))
                self.datum['real_time'] = float(regexProFail.match(line).group(12))

            elif regexPSY.match(line):
                self.datum['type'] = 'PSYoungGen'
                self.datum['timestamp'] = regexPSY.match(line).group(1)
                self.datum['newgen_kb_before'] = int(regexPSY.match(line).group(2))
                self.datum['newgen_kb_after'] = int(regexPSY.match(line).group(3))
                self.datum['total_kb_before'] = int(regexPSY.match(line).group(4))
                self.datum['total_kb_after'] = int(regexPSY.match(line).group(5))
                self.datum['user_time'] = float(regexPSY.match(line).group(6))
                self.datum['sys_time'] = float(regexPSY.match(line).group(7))
                self.datum['real_time'] = float(regexPSY.match(line).group(8))

            elif regexCMS.match(line):
                self.datum['timestamp'] = regexCMS.match(line).group(1)
                self.datum['type'] = regexCMS.match(line).group(2)

            elif regexCMSr.match(line):
                self.datum['type'] = 'CMS-remark'
                self.datum['timestamp'] = regexCMSr.match(line).group(1)
                self.datum['user_time'] = float(regexCMSr.match(line).group(2))
                self.datum['sys_time'] = float(regexCMSr.match(line).group(3))
                self.datum['real_time'] = float(regexCMSr.match(line).group(4))

            elif regexCMSi.match(line):
                self.datum['type'] = 'CMS-initial-mark'
                self.datum['timestamp'] = regexCMSi.match(line).group(1)
                self.datum['user_time'] = float(regexCMSi.match(line).group(2))
                self.datum['sys_time'] = float(regexCMSi.match(line).group(3))
                self.datum['real_time'] = float(regexCMSi.match(line).group(4))

            elif regexCMSc.match(line):
                self.datum['timestamp'] = regexCMSc.match(line).group(1)
                self.datum['type'] = regexCMSc.match(line).group(2)

            elif regexCMScs.match(line):
                self.datum['timestamp'] = regexCMScs.match(line).group(1)
                self.datum['type'] = regexCMScs.match(line).group(2)
                self.datum['user_time'] = float(regexCMScs.match(line).group(3))
                self.datum['sys_time'] = float(regexCMScs.match(line).group(4))
                self.datum['real_time'] = float(regexCMScs.match(line).group(5))

            elif regexFull.match(line):
                self.datum['type'] = 'Full'
                self.datum['blocking'] = True
                self.datum['timestamp'] = regexFull.match(line).group(1)
                self.datum['oldgen_kb_before'] = int(regexFull.match(line).group(2))
                self.datum['oldgen_kb_after'] = int(regexFull.match(line).group(3))
                self.datum['total_kb_before'] = int(regexFull.match(line).group(4))
                self.datum['total_kb_after'] = int(regexFull.match(line).group(5))
                self.datum['permgen_kb_before'] = int(regexFull.match(line).group(6))
                self.datum['permgen_kb_after'] = int(regexFull.match(line).group(7))
                self.datum['user_time'] = float(regexFull.match(line).group(8))
                self.datum['sys_time'] = float(regexFull.match(line).group(9))
                self.datum['real_time'] = float(regexFull.match(line).group(10))

            elif regexFulln.match(line):
                self.datum['type'] = 'Full'
                self.datum['timestamp'] = regexFulln.match(line).group(1)
                self.datum['newgen_kb_before'] = int(regexFulln.match(line).group(2))
                self.datum['newgen_kb_after'] = int(regexFulln.match(line).group(3))
                self.datum['oldgen_kb_before'] = int(regexFulln.match(line).group(4))
                self.datum['oldgen_kb_after'] = int(regexFulln.match(line).group(5))
                self.datum['total_kb_before'] = int(regexFulln.match(line).group(6))
                self.datum['total_kb_after'] = int(regexFulln.match(line).group(7))
                self.datum['permgen_kb_before'] = int(regexFulln.match(line).group(8))
                self.datum['permgen_kb_after'] = int(regexFulln.match(line).group(9))
                self.datum['user_time'] = float(regexFulln.match(line).group(10))
                self.datum['sys_time'] = float(regexFulln.match(line).group(11))
                self.datum['real_time'] = float(regexFulln.match(line).group(12))

            else:
                print Exception("couldn't parse line: %s" % line)
                self.data['error']['count'] += 1

            #print self.datum
            # we are still in the for line in lines loop!
            if self.datum:      # check if a regex did match
                # Critical section start
                self.__lockObj.acquire()
                type = self.underscore(self.datum['type'])
                #print type
                if type == 'par_new':
                    self.data[type]['real_time'] += self.datum['real_time']
                    self.data[type]['sys_time'] += self.datum['sys_time']
                    self.data[type]['user_time'] += self.datum['user_time']
                    self.data[type]['newgen_kb_collected'] += self.datum['newgen_kb_before'] - self.datum['newgen_kb_after']
                    self.data[type]['total_kb_collected'] += self.datum['total_kb_before'] - self.datum['total_kb_after']
                    self.data[type]['count'] += 1

                elif type == 'ps_young_gen':
                    self.data[type]['real_time'] += self.datum['real_time']
                    self.data[type]['sys_time'] += self.datum['sys_time']
                    self.data[type]['user_time'] += self.datum['user_time']
                    self.data[type]['newgen_kb_collected'] += self.datum['newgen_kb_before'] - self.datum['newgen_kb_after']
                    self.data[type]['total_kb_collected'] += self.datum['total_kb_before'] - self.datum['total_kb_after']
                    self.data[type]['count'] += 1

                elif type == 'promotion_failure':
                    self.data[type]['real_time'] += self.datum['real_time']
                    self.data[type]['sys_time'] += self.datum['sys_time']
                    self.data[type]['user_time'] += self.datum['user_time']
                    self.data[type]['newgen_kb_collected'] += self.datum['newgen_kb_before'] - self.datum['newgen_kb_after']
                    self.data[type]['oldgen_kb_collected'] += self.datum['oldgen_kb_before'] - self.datum['oldgen_kb_after']
                    self.data[type]['permgen_kb_collected'] += self.datum['permgen_kb_before'] - self.datum['permgen_kb_after']
                    self.data[type]['total_kb_collected'] += self.datum['total_kb_before'] - self.datum['total_kb_after']
                    self.data[type]['count'] += 1

                elif type in ['cms_initial_mark', 'cms_concurrent_mark', 'cms_concurrent_abortable_preclean', 
                              'cms_remark', 'cms_concurrent_sweep', 'cms_concurrent_reset']:
                    self.data[type]['real_time'] += self.datum['real_time']
                    self.data[type]['sys_time'] += self.datum['sys_time']
                    self.data[type]['user_time'] += self.datum['user_time']
                    self.data[type]['count'] += 1

                #print "data:", self.data
                #  Exit from critical section
                self.__lockObj.release()
                # Critical section end
        return

    def getMetrics(self):
        #print "ID Parser obj:", id(self), "- getMetrics method call"
        #print "ID datum:", id(self.datum), "- getMetrics method call"
        #print "data getMetrics:", self.data, id(self.data)
        return json.dumps(self.data)

    def clearDatum(self):
        #print "ID Parser obj:", id(self), "- cleardatum method call"
        #print "ID datum:", id(self.datum), "- cleardatum method call"
        self.datum.clear()
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

