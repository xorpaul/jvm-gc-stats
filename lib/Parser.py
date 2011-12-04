import re
import json

import Tailer

class Parser:
    def __init__(self):
        pass

    def parse(self, t):
        regex = re.compile(r"(.*): \d+\.\d+: \[GC \d+\.\d+: \[ParNew: (\d+)K\->(\d+)K\(\d+K\), \d+\.\d+ secs\] (\d+)K\->(\d+)K\(\d+K\), \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]\n")

        #string = "2011-12-02T22:53:42.273+0100: 6.649: [GC 6.649: [ParNew: 51254K->6082K(57344K), 0.0650120 secs] 51254K->6082K(516096K), 0.0651920 secs] [Times: user=0.07 sys=0.00, real=0.07 secs]"
        #string = "2011-12-02T22:54:14.955+0100: 39.331: [GC 39.331: [ParNew: 57344K->7619K(57344K), 0.4781460 secs] 63799K->21896K(516096K), 0.4905760 secs] [Times: user=0.38 sys=0.00, real=0.49 secs]"

        loglines = t.follow(t.fd)
        for line in loglines:
            #print line
            data = {}
            m = regex.match(line)
            #print m
            if m:
                data['type'] = 'ParNew'
                data['user_time'] = float(m.group(6))
                data['sys_time'] = float(m.group(7))
                data['real_time'] = float(m.group(8))
                data['timestamp'] = m.group(1)
                data['newgen_kb_before'] = int(m.group(2))
                data['newgen_kb_after'] = int(m.group(3))
                data['total_kb_before'] = int(m.group(4))
                data['total_kb_after'] = int(m.group(5))
                #print data

                print json.dumps(data)
            else:
                print Exception("couldn't parse line: %s" % line)
