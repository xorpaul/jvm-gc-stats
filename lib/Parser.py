import re
import json
import copy
from string import maketrans

import Tailer

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class Parser:
    def __init__(self):
        #print "ID Parser obj:", id(self), "- Parser init"
        self.datum = {}
        self.data = {}

    def parse(self, t):
        #print "ID Parser obj:", id(self), "- parse method call"
        regex = re.compile(r"(.*): \d+\.\d+: \[GC \d+\.\d+: \[ParNew: (\d+)K\->(\d+)K\(\d+K\), \d+\.\d+ secs\] (\d+)K\->(\d+)K\(\d+K\), \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]\n")

        #string = "2011-12-02T22:53:42.273+0100: 6.649: [GC 6.649: [ParNew: 51254K->6082K(57344K), 0.0650120 secs] 51254K->6082K(516096K), 0.0651920 secs] [Times: user=0.07 sys=0.00, real=0.07 secs]"
        #string = "2011-12-02T22:54:14.955+0100: 39.331: [GC 39.331: [ParNew: 57344K->7619K(57344K), 0.4781460 secs] 63799K->21896K(516096K), 0.4905760 secs] [Times: user=0.38 sys=0.00, real=0.49 secs]"

        loglines = t.follow(t.fd)
        for line in loglines:
            #print line
            #m = regex.match(line)
            #print m
            if regex.match(line):
                self.datum['type'] = 'ParNew'
                self.datum['user_time'] = float(regex.match(line).group(6))
                self.datum['sys_time'] = float(regex.match(line).group(7))
                self.datum['real_time'] = float(regex.match(line).group(8))
                self.datum['timestamp'] = regex.match(line).group(1)
                self.datum['newgen_kb_before'] = int(regex.match(line).group(2))
                self.datum['newgen_kb_after'] = int(regex.match(line).group(3))
                self.datum['total_kb_before'] = int(regex.match(line).group(4))
                self.datum['total_kb_after'] = int(regex.match(line).group(5))
                #print self.datum

                #print "njeee:", self.result
                #yield json.dumps(self.datum)
                #print "ID datum:", id(self.datum), "- parse method call"
            else:
                print Exception("couldn't parse line: %s" % line)
        return

    def getMetrics(self):
        #print "ID Parser obj:", id(self), "- getMetrics method call"
        #print "ID datum:", id(self.datum), "- getMetrics method call"
        if self.datum:
            type = self.underscore(self.datum['type'])
            # TODO:
            #print type
            #if type == 'par_new':
            #    self.data = { type: {'real_time': self.datum['real_time'] + self.data[type]['real_time']}}
            #    print "data[type]['real_time']", self.data[type]['real_time']
            #    print "datum['real_time']", self.datum['real_time']
        #    [:real_time, :user_time, :sys_time].each do |t|
        #    end

        #    data[service][type][:newgen_kb_colllected] += datum[:newgen_kb_before] - datum[:newgen_kb_after]
        #    data[service][type][:total_kb_colllected] += datum[:total_kb_before] - datum[:total_kb_after]
        #    data[service][type][:count] += 1

        self.datum = self.data

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
        word =  word.translate(maketrans('-', '_'))
        return word.lower()
   #   word.gsub!(/::/, '/')
   #   word.gsub!(/([A-Z]+)([A-Z][a-z])/,'\1_\2')
   #   word.gsub!(/([a-z\d])([A-Z])/,'\1_\2')
   #   word.tr!("-", "_")
   #   word.downcase!
