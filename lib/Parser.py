import re
import copy
import time
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
        if not self.__init:
            self.pid = None
            # also initializes the data dict
            self.hidden_data = DefaultDict((DefaultDict(DefaultDict(0), **DefaultDict(0))), **DefaultDict(0))
            self.clearData()
            self.__init = True

        return

    def follow(self, t, service):
        loglines = t.tail()
        for line in loglines:
            self.parse(line, service)

    def parse(self, line, service):
        # made Java 7 compliant when LC_NUMERIC isn't en_US 
        # with :'<,'>s/\\\.\\/[\\.,]\\/ vi ftw :)
        regexParNew = re.compile(r"(.*: )?\d+[\.,]\d+: \[GC \d+[\.,]\d+: \[ParNew: (\d+)K\->(\d+)K\(\d+K\), \d+[\.,]\d+ secs\] (\d+)K\->(\d+)K\(\d+K\)(?: icms_dc=\d+ )?, \d+[\.,]\d+ secs\] \[Times: user=(\d+[\.,]\d+) sys=(\d+[\.,]\d+), real=(\d+[\.,]\d+) secs\]")
        regexDefNew = re.compile(r"(.*: )?\d+[\.,]\d+: \[GC \d+[\.,]\d+: \[DefNew: (\d+)K\->(\d+)K\(\d+K\), \d+[\.,]\d+ secs\] (\d+)K\->(\d+)K\(\d+K\), \d+[\.,]\d+ secs\] \[Times: user=(\d+[\.,]\d+) sys=(\d+[\.,]\d+), real=(\d+[\.,]\d+) secs\]")
        regexProFail = re.compile(r"(.*: )?\d+[\.,]\d+: \[GC \d+[\.,]\d+: \[(?:Par|Def)New \(promotion failed\)\s*: (\d+)K->(\d+)K\(\d+K\), \d+[\.,]\d+ secs\]\d+[\.,]\d+: \[(?:CMS|Tenured): (\d+)K->(\d+)K\(\d+K\), \d+[\.,]\d+ secs\] (\d+)K->(\d+)K\(\d+K\), \[(?:CMS )?Perm : (\d+)K->(\d+)K\(\d+K\)\], \d+[\.,]\d+ secs\] \[Times: user=(\d+[\.,]\d+) sys=(\d+[\.,]\d+), real=(\d+[\.,]\d+) secs\]")
        regexPSY = re.compile(r"(.*: )?\d+[\.,]\d+: \[GC(?:--)? \[PSYoungGen: (\d+)K->(\d+)K\(\d+K\)\] (\d+)K->(\d+)K\(\d+K\), \d+[\.,]\d+ secs\] \[Times: user=(\d+[\.,]\d+) sys=(\d+[\.,]\d+), real=(\d+[\.,]\d+) secs\]")
        regexCMSr = re.compile(r"(.*: )?\d+[\.,]\d+: \[GC\[YG occupancy: \d+ K \(\d+ K\)\]\d+[\.,]\d+: \[Rescan \(parallel\) , \d+[\.,]\d+ secs\]\d+[\.,]\d+: \[weak refs processing, \d+[\.,]\d+ secs\](?:\d+[\.,]\d+: \[class unloading, \d+[\.,]\d+ secs\])?(?:\d+[\.,]\d+: \[scrub symbol & string tables, \d+[\.,]\d+ secs\])? \[1 CMS-remark: \d+K\(\d+K\)\] \d+K\(\d+K\), \d+[\.,]\d+ secs\] \[Times: user=(\d+[\.,]\d+) sys=(\d+[\.,]\d+), real=(\d+[\.,]\d+) secs\]")
        regexCMSi = re.compile(r"(.*: )?\d+[\.,]\d+: \[GC \[1 CMS\-initial\-mark: \d+K\(\d+K\)\] \d+K\(\d+K\), \d+[\.,]\d+ secs\] \[Times: user=(\d+[\.,]\d+) sys=(\d+[\.,]\d+), real=(\d+[\.,]\d+) secs\]")
        regexCMSc = re.compile(r"(.*: )?\[(CMS-concurrent-abortable-preclean|CMS-concurrent-preclean|CMS-concurrent-mark): \d+[\.,]\d+\/\d+[\.,]\d+ secs\] \[Times: user=(\d+[\.,]\d+) sys=(\d+[\.,]\d+), real=(\d+[\.,]\d+) secs\]")
        regexCMScs = re.compile(r"(.*: )?\d+[\.,]\d+: \[(CMS-concurrent-reset|CMS-concurrent-sweep): \d+[\.,]\d+\/\d+[\.,]\d+ secs\] \[Times: user=(\d+[\.,]\d+) sys=(\d+[\.,]\d+), real=(\d+[\.,]\d+) secs\]")
        regexFull = re.compile(r"(.*: )?\d+[\.,]\d+: \[Full GC(?: \(System\))? \d+[\.,]\d+: \[(?:CMS|Tenured): (\d+)K->(\d+)K\(\d+K\), \d+[\.,]\d+ secs\] (\d+)K->(\d+)K\(\d+K\), \[(?:CMS )?Perm : (\d+)K->(\d+)K\(\d+K\)\], \d+[\.,]\d+ secs\] \[Times: user=(\d+[\.,]\d+) sys=(\d+[\.,]\d+), real=(\d+[\.,]\d+) secs\]")
        regexFulln = re.compile(r"(.*: )?\d+[\.,]\d+: \[Full GC(?: \(System\))? \[PSYoungGen: (\d+)K->(\d+)K\(\d+K\)\] \[(?:ParOldGen|PSOldGen): (\d+)K->(\d+)K\(\d+K\)\] (\d+)K->(\d+)K\(\d+K\) \[PSPermGen: (\d+)K->(\d+)K\(\d+K\)\], \d+[\.,]\d+ secs\] \[Times: user=(\d+[\.,]\d+) sys=(\d+[\.,]\d+), real=(\d+[\.,]\d+) secs\]")
        regexFullc = re.compile(r"(.*: )?\d+[\.,]\d+: \[Full GC \d+[\.,]\d+: \[CMS \(concurrent mode failure\)\[YG occupancy: \d+ K \(\d+ K\)\]\d+[\.,]\d+: \[weak refs processing, \d+[\.,]\d+ secs\]: (\d+)K->(\d+)K\(\d+K\), \d+[\.,]\d+ secs\] (\d+)K->(\d+)K\(\d+K\), \[CMS Perm : (\d+)K->(\d+)K\(\d+K\)\], \d+[\.,]\d+ secs\] \[Times: user=(\d+[\.,]\d+) sys=(\d+[\.,]\d+), real=(\d+[\.,]\d+) secs\]")
        regexFullf = re.compile(r".*\(concurrent mode failure\): (\d+)K->(\d+)K\(\d+K\), \d+[\.,]\d+ secs\] (\d+)K->(\d+)K\(\d+K\), \[CMS Perm : (\d+)K->(\d+)K\(\d+K\)\](?: icms_dc=\d+ )?, \d+[\.,]\d+ secs\] \[Times: user=(\d+[\.,]\d+) sys=(\d+[\.,]\d+), real=(\d+[\.,]\d+) secs\]")
        regexFullg = re.compile(r"(.*: )?\d+[\.,]\d+: \[GC(?: \(System\))? \d+[\.,]\d+: \[(?:Def|Par)New: (\d+)K\->(\d+)K\(\d+K\), \d+[\.,]\d+ secs\]\d+[\.,]\d+: \[(?:CMS|Tenured): (\d+)K->(\d+)K\(\d+K\), \d+[\.,]\d+ secs\] (\d+)K->(\d+)K\(\d+K\), \[(?:CMS )?Perm\s*:\s*(\d+)K->(\d+)K\(\d+K\)\], \d+[\.,]\d+ secs\] \[Times: user=(\d+[\.,]\d+) sys=(\d+[\.,]\d+), real=(\d+[\.,]\d+) secs\]")

        # need to initialize with newgen values, because some full GC lines
        # contain newgen values and some do not
        datum = {'newgen_kb_before': 0, 'newgen_kb_after': 0}
        if regexParNew.match(line):
            datum['type'] = 'par_new'
            datum['timestamp'] = regexParNew.match(line).group(1)
            datum['newgen_kb_before'] = int(regexParNew.match(line).group(2))
            datum['newgen_kb_after'] = int(regexParNew.match(line).group(3))
            datum['total_kb_before'] = int(regexParNew.match(line).group(4))
            datum['total_kb_after'] = int(regexParNew.match(line).group(5))
            datum['user_time'] = float(regexParNew.match(line).group(6).replace(",","."))
            datum['sys_time'] = float(regexParNew.match(line).group(7).replace(",","."))
            datum['real_time'] = float(regexParNew.match(line).group(8).replace(",","."))
            # STW 
            datum['stw'] = float(regexParNew.match(line).group(8).replace(",","."))

        elif regexDefNew.match(line):
            datum['type'] = 'def_new'
            datum['timestamp'] = regexDefNew.match(line).group(1)
            datum['newgen_kb_before'] = int(regexDefNew.match(line).group(2))
            datum['newgen_kb_after'] = int(regexDefNew.match(line).group(3))
            datum['total_kb_before'] = int(regexDefNew.match(line).group(4))
            datum['total_kb_after'] = int(regexDefNew.match(line).group(5))
            datum['user_time'] = float(regexDefNew.match(line).group(6).replace(",","."))
            datum['sys_time'] = float(regexDefNew.match(line).group(7).replace(",","."))
            datum['real_time'] = float(regexDefNew.match(line).group(8).replace(",","."))
            # STW 
            datum['stw'] = float(regexDefNew.match(line).group(8).replace(",","."))

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
            datum['user_time'] = float(regexProFail.match(line).group(10).replace(",","."))
            datum['sys_time'] = float(regexProFail.match(line).group(11).replace(",","."))
            datum['real_time'] = float(regexProFail.match(line).group(12).replace(",","."))
            # STW 
            datum['stw'] = float(regexProFail.match(line).group(12).replace(",","."))

        elif regexPSY.match(line):
            datum['type'] = 'ps_young_gen'
            datum['timestamp'] = regexPSY.match(line).group(1)
            datum['newgen_kb_before'] = int(regexPSY.match(line).group(2))
            datum['newgen_kb_after'] = int(regexPSY.match(line).group(3))
            datum['total_kb_before'] = int(regexPSY.match(line).group(4))
            datum['total_kb_after'] = int(regexPSY.match(line).group(5))
            datum['user_time'] = float(regexPSY.match(line).group(6).replace(",","."))
            datum['sys_time'] = float(regexPSY.match(line).group(7).replace(",","."))
            datum['real_time'] = float(regexPSY.match(line).group(8).replace(",","."))
            # STW 
            datum['stw'] = float(regexPSY.match(line).group(8).replace(",","."))

        elif regexCMSr.match(line):
            datum['type'] = 'cms_remark'
            datum['timestamp'] = regexCMSr.match(line).group(1)
            datum['user_time'] = float(regexCMSr.match(line).group(2).replace(",","."))
            datum['sys_time'] = float(regexCMSr.match(line).group(3).replace(",","."))
            datum['real_time'] = float(regexCMSr.match(line).group(4).replace(",","."))
            # STW 
            datum['stw'] = float(regexCMSr.match(line).group(4).replace(",","."))

        elif regexCMSi.match(line):
            datum['type'] = 'cms_initial_mark'
            datum['timestamp'] = regexCMSi.match(line).group(1)
            datum['user_time'] = float(regexCMSi.match(line).group(2).replace(",","."))
            datum['sys_time'] = float(regexCMSi.match(line).group(3).replace(",","."))
            datum['real_time'] = float(regexCMSi.match(line).group(4).replace(",","."))
            # STW 
            datum['stw'] = float(regexCMSi.match(line).group(4).replace(",","."))

        elif regexCMSc.match(line):
            datum['timestamp'] = regexCMSc.match(line).group(1)
            datum['type'] = self.underscore(regexCMSc.match(line).group(2))
            datum['user_time'] = float(regexCMSc.match(line).group(3).replace(",","."))
            datum['sys_time'] = float(regexCMSc.match(line).group(4).replace(",","."))
            datum['real_time'] = float(regexCMSc.match(line).group(5).replace(",","."))

        elif regexCMScs.match(line):
            datum['timestamp'] = regexCMScs.match(line).group(1)
            datum['type'] = self.underscore(regexCMScs.match(line).group(2))
            datum['user_time'] = float(regexCMScs.match(line).group(3).replace(",","."))
            datum['sys_time'] = float(regexCMScs.match(line).group(4).replace(",","."))
            datum['real_time'] = float(regexCMScs.match(line).group(5).replace(",","."))

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
            datum['user_time'] = float(regexFull.match(line).group(8).replace(",","."))
            datum['sys_time'] = float(regexFull.match(line).group(9).replace(",","."))
            datum['real_time'] = float(regexFull.match(line).group(10).replace(",","."))
            # STW 
            datum['stw'] = float(regexFull.match(line).group(10).replace(",","."))

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
            datum['user_time'] = float(regexFulln.match(line).group(10).replace(",","."))
            datum['sys_time'] = float(regexFulln.match(line).group(11).replace(",","."))
            datum['real_time'] = float(regexFulln.match(line).group(12).replace(",","."))
            # STW 
            datum['stw'] = float(regexFulln.match(line).group(12).replace(",","."))

        elif regexFullc.match(line):
            datum['type'] = 'full'
            datum['cmf'] = 1    # concurrent mode failure
            datum['timestamp'] = regexFullc.match(line).group(1)
            datum['oldgen_kb_before'] = int(regexFullc.match(line).group(2))
            datum['oldgen_kb_after'] = int(regexFullc.match(line).group(3))
            datum['total_kb_before'] = int(regexFullc.match(line).group(4))
            datum['total_kb_after'] = int(regexFullc.match(line).group(5))
            datum['permgen_kb_before'] = int(regexFullc.match(line).group(6))
            datum['permgen_kb_after'] = int(regexFullc.match(line).group(7))
            datum['user_time'] = float(regexFullc.match(line).group(8).replace(",","."))
            datum['sys_time'] = float(regexFullc.match(line).group(9).replace(",","."))
            datum['real_time'] = float(regexFullc.match(line).group(10).replace(",","."))
            # STW 
            datum['stw'] = float(regexCMSi.match(line).group(10).replace(",","."))

        elif regexFullf.match(line):
            datum['type'] = 'full'
            datum['cmf'] = 1    # concurrent mode failure
            datum['oldgen_kb_before'] = int(regexFullf.match(line).group(1))
            datum['oldgen_kb_after'] = int(regexFullf.match(line).group(2))
            datum['total_kb_before'] = int(regexFullf.match(line).group(3))
            datum['total_kb_after'] = int(regexFullf.match(line).group(4))
            datum['permgen_kb_before'] = int(regexFullf.match(line).group(5))
            datum['permgen_kb_after'] = int(regexFullf.match(line).group(6))
            datum['user_time'] = float(regexFullf.match(line).group(7).replace(",","."))
            datum['sys_time'] = float(regexFullf.match(line).group(8).replace(",","."))
            datum['real_time'] = float(regexFullf.match(line).group(9).replace(",","."))
            # STW 
            datum['stw'] = float(regexFullf.match(line).group(9).replace(",","."))

        elif regexFullg.match(line):
            datum['type'] = 'full'
            datum['newgen_kb_before'] = int(regexFullg.match(line).group(2))
            datum['newgen_kb_after'] = int(regexFullg.match(line).group(3))
            datum['oldgen_kb_before'] = int(regexFullg.match(line).group(4))
            datum['oldgen_kb_after'] = int(regexFullg.match(line).group(5))
            datum['total_kb_before'] = int(regexFullg.match(line).group(6))
            datum['total_kb_after'] = int(regexFullg.match(line).group(7))
            datum['permgen_kb_before'] = int(regexFullg.match(line).group(8))
            datum['permgen_kb_after'] = int(regexFullg.match(line).group(9))
            datum['user_time'] = float(regexFullg.match(line).group(10).replace(",","."))
            datum['sys_time'] = float(regexFullg.match(line).group(11).replace(",","."))
            datum['real_time'] = float(regexFullg.match(line).group(12).replace(",","."))
            # STW 
            datum['stw'] = float(regexFullg.match(line).group(12).replace(",","."))

        else:
            self.data['errors'] += 1
            print Exception("[%s]: couldn't parse line: %s" % (service, repr(line)))

        #print "datum:", datum
        if 'type' in datum:      # check if a regex did match
            # Critical section start
            self.__lockObj.acquire()
            type = datum['type']

            # metrics regardless of type
            timeSinceStart = time.time() - self.startTime
            self.data['seconds_since_last_reset'] = '%.2f' % timeSinceStart
            if not self.data[service]['count']:
                self.data[service]['count'] = 0
                self.data[service]['avg_time_between_any_type_collections'] = 0
                self.data[service]['stw_overall'] = 0
            self.data[service]['count'] += 1
            self.data[service]['avg_time_between_any_type_collections'] = '%.2f' % float(float(self.data['seconds_since_last_reset']) / self.data[service]['count'])
            if 'stw' in datum:
                self.data[service]['stw_overall'] = '%.2f' % float(float(self.data[service]['stw_overall']) + datum['stw'])
                if float(self.data['seconds_since_last_reset']) > 0:
                    self.data[service]['stw_percentage'] = '%.2f' % float(100 * float(self.data[service]['stw_overall']) / float(self.data['seconds_since_last_reset']))
            if 'cmf' in datum:
                if not self.data[service]['cmf_overall']:
                    self.data[service]['cmf_overall'] = 0
                self.data[service]['cmf_overall'] += 1

            # metrics that get collected with every GC type
            # total number of collections
            self.data[service][type]['count'] += 1
            # frequency of collections
            self.data[service][type]['avg_time_between_collections'] = '%.2f' % float(float(self.data['seconds_since_last_reset']) / self.data[service][type]['count'])

            # longest time spent in collection
            if float(datum['real_time']) > float(self.data[service][type]['max_real_time']):
                self.data[service][type]['max_real_time'] = '%.2f' % datum['real_time']
            if float(datum['user_time']) > float(self.data[service][type]['max_user_time']):
                self.data[service][type]['max_user_time'] = '%.2f' % datum['user_time']
            if float(datum['sys_time']) > float(self.data[service][type]['max_sys_time']):
                self.data[service][type]['max_sys_time'] = '%.2f' % datum['sys_time']
            # total time spent in collection
            self.data[service][type]['real_time'] = '%.2f' % float(float(self.data[service][type]['real_time']) + datum['real_time'])
            self.data[service][type]['sys_time'] = '%.2f' % float(float(self.data[service][type]['sys_time']) + datum['sys_time'])
            self.data[service][type]['user_time'] = '%.2f' % float(float(self.data[service][type]['user_time']) + datum['user_time'])
            # total stw time
            if 'stw' in datum:
                self.data[service][type]['stw'] = '%.2f' % float(float(self.data[service][type]['stw']) + datum['stw'])
            # average time spent in collection
            self.data[service][type]['avg_real_time'] = '%.3f' % float(float(self.data[service][type]['real_time']) / self.data[service][type]['count'])
            self.data[service][type]['avg_sys_time'] = '%.3f' % float(float(self.data[service][type]['sys_time']) / self.data[service][type]['count'])
            self.data[service][type]['avg_user_time'] = '%.3f' % float(float(self.data[service][type]['user_time']) / self.data[service][type]['count'])


            #print "type:", type
            if type in ('par_new', 'def_new', 'ps_young_gen'):
                # number of bytes currently allocated
                self.data[service]['cur_newgen_kb_allocated'] = datum['newgen_kb_after']
                self.data[service]['cur_total_kb_allocated'] = datum['total_kb_after']

                newDelta = datum['newgen_kb_before'] - datum['newgen_kb_after']
                totalDelta = datum['total_kb_before'] - datum['total_kb_after']
                if newDelta > self.data[service][type]['max_newgen_kb_collected']:
                    self.data[service][type]['max_newgen_kb_collected'] = newDelta
                if totalDelta > self.data[service][type]['max_total_kb_collected']:
                    self.data[service][type]['max_total_kb_collected'] = totalDelta
                # total number of bytes recovered
                self.data[service][type]['newgen_kb_collected'] += newDelta
                self.data[service][type]['total_kb_collected'] += totalDelta
                # average number of bytes recovered per collection
                self.data[service][type]['avg_newgen_kb_collected'] = self.data[service][type]['newgen_kb_collected'] / self.data[service][type]['count']
                self.data[service][type]['avg_total_kb_collected'] = self.data[service][type]['total_kb_collected'] / self.data[service][type]['count']

            elif type in ('promotion_failure', 'full'):
                # number of bytes currently allocated
                self.data[service]['cur_newgen_kb_allocated'] = datum['newgen_kb_after']
                self.data[service]['cur_oldgen_kb_allocated'] = datum['oldgen_kb_after']
                self.data[service]['cur_total_kb_allocated'] = datum['total_kb_after']
                self.data[service]['cur_permgen_kb_allocated'] = datum['permgen_kb_after']

                newDelta = datum['newgen_kb_before'] - datum['newgen_kb_after']
                oldDelta = datum['oldgen_kb_before'] - datum['oldgen_kb_after']
                totalDelta = datum['total_kb_before'] - datum['total_kb_after']
                permDelta = datum['permgen_kb_before'] - datum['permgen_kb_after']
                if newDelta > self.data[service][type]['max_newgen_kb_collected']:
                    self.data[service][type]['max_newgen_kb_collected'] = newDelta
                if oldDelta > self.data[service][type]['max_oldgen_kb_collected']:
                    self.data[service][type]['max_oldgen_kb_collected'] = oldDelta
                if totalDelta > self.data[service][type]['max_total_kb_collected']:
                    self.data[service][type]['max_total_kb_collected'] = totalDelta
                if permDelta > self.data[service][type]['max_oldgen_kb_collected']:
                    self.data[service][type]['max_permgen_kb_collected'] = oldDelta
                # total number of bytes recovered
                self.data[service][type]['newgen_kb_collected'] += newDelta
                self.data[service][type]['total_kb_collected'] += totalDelta
                self.data[service][type]['oldgen_kb_collected'] += oldDelta
                self.data[service][type]['permgen_kb_collected'] += permDelta
                # average number of bytes recovered per collection
                self.data[service][type]['avg_newgen_kb_collected'] = self.data[service][type]['newgen_kb_collected'] / self.data[service][type]['count']
                self.data[service][type]['avg_oldgen_kb_collected'] = self.data[service][type]['oldgen_kb_collected'] / self.data[service][type]['count']
                self.data[service][type]['avg_total_kb_collected'] = self.data[service][type]['total_kb_collected'] / self.data[service][type]['count']
                self.data[service][type]['avg_permgen_kb_collected'] = self.data[service][type]['permgen_kb_collected'] / self.data[service][type]['count']

            datum.clear()
            #print "data:", self.data
            #  Exit from critical section
            self.__lockObj.release()
            # Critical section end
        return

    def getMetrics(self, pretty=False):
        """ Returns the current data in JSON format.

        Gets called from every GET HTTP request.
        """
        currentTime = time.time()
        self.data['seconds_since_last_reset'] = '%.2f' % (currentTime - self.startTime)
        for service in self.data:
          if not service in ('errors', 'seconds_since_last_reset'):
            if self.hidden_data[service]['stw_overall']:
              self.data[service]['stw_since_last_call'] = '%.2f' %  float(float(self.data[service]['stw_overall']) - self.hidden_data[service]['stw_overall'])
            
            if self.data[service]['stw_overall']:
              self.hidden_data[service]['stw_overall'] = float(self.data[service]['stw_overall'])
              self.hidden_data[service]['timestamp'] = currentTime

        if pretty:
            return json.dumps(self.data, sort_keys=True, indent=4)
        else:
            return json.dumps(self.data)

    def getData(self):
        """ Returns the current data from the Parse object.

        Gets only used for the unittest.
        """
        return self.data

    def clearData(self):
        self.data = DefaultDict((DefaultDict(DefaultDict(0), **DefaultDict(0))), **DefaultDict(0))
        self.data['errors'] = 0
        self.startTime = time.time()
        self.data['seconds_since_last_reset'] = 0
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
    """Dictionary with a default value for unknown keys

       http://stackoverflow.com/a/39858/682847

       Needed to set default values for dictionary,
       otherwise I would get KeyErrors when trying to
       sum up numbers"""
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
