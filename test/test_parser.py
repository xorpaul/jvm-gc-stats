#! /usr/bin/env python
import sys
sys.path.append("../")
import unittest
from lib import *

class TestParser(unittest.TestCase):
    def assert_parsed(self, line, values):
        p = Parser.Parser()
        p.parse(line)
        #print line
        #print id(p.data)
        try:
            #print "p.data:", p.data
            #print "values:", values
            self.assertEqual(values, p.data)
        finally:
            p.clearData()

    def testParserSingleton(self):
        p1 = Parser.Parser()
        p2 = Parser.Parser()

        d1 = p1.data
        d2 = p2.data
        
        self.assertEqual(id(p1), id(p2))
        self.assertEqual(id(d1), id(d2))

    def testParNew(self):
        line = "2011-05-16T19:01:54.600+0000: 12.340: [GC 12.340: [ParNew: 943744K->104832K(943744K), 0.4265660 secs] 1133140K->463127K(8283776K), 0.4266400 secs] [Times: user=1.93 sys=0.21, real=0.43 secs]"
        values = {'par_new': {'count': 1.0, 'newgen_kb_collected': 838912.0, 'total_kb_collected': 670013.0, 'sys_time': 0.20999999999999999, 'real_time': 0.42999999999999999, 'user_time': 1.9299999999999999}, 'errors': 0}
        self.assert_parsed(line, values)

    def testFull(self):
        line = "2011-05-16T19:01:49.148+0000: 6.888: [Full GC 6.906: [CMS: 22065K->39440K(7340032K), 0.3012410 secs] 240184K->39440K(8283776K), [CMS Perm : 35150K->35025K(35236K)], 0.3014270 secs] [Times: user=0.30 sys=0.01, real=0.32 secs]"
        values = {'errors': 0, 'full': {'count': 1.0, 'total_kb_collected': 401488.0, 'permgen_kb_collected': 125.0, 'sys_time': 0.01, 'real_time': 0.32000000000000001, 'oldgen_kb_collected': -17375.0, 'user_time': 0.29999999999999999}}
        self.assert_parsed(line, values)

    def testFulln(self):
        line = "2011-05-11T04:28:36.398+0000: 257.070: [Full GC [PSYoungGen: 3936K->0K(85760K)] [ParOldGen: 252218K->120734K(221056K)] 256154K->120734K(306816K) [PSPermGen: 12177K->12153K(24896K)], 0.3264320 secs] [Times: user=2.75 sys=0.21, real=0.33 secs]"
        values = {'errors': 0, 'full': {'count': 1.0, 'total_kb_collected': 270840.0, 'permgen_kb_collected': 24.0, 'sys_time': 0.20999999999999999, 'real_time': 0.33000000000000002, 'oldgen_kb_collected': 131484.0, 'user_time': 2.75}}
        self.assert_parsed(line, values)

    def testCMSc(self):
        line = "2011-05-12T15:18:32.227+0000: 53123.348: [CMS-concurrent-mark: 3.332/3.333 secs] [Times: user=13.02 sys=0.31, real=3.33 secs]"
        values = {'errors': 0, 'cms_concurrent_mark': {'count': 1.0, 'real_time': 3.3300000000000001, 'user_time': 13.02, 'sys_time': 0.31}}
        self.assert_parsed(line, values)

        line = "2011-02-26T06:22:39.421+0000: 1408.720: [CMS-concurrent-sweep: 20.008/20.126 secs] [Times: user=40.81 sys=7.39, real=20.13 secs]"
        values = {'cms_concurrent_sweep': {'count': 1.0, 'real_time': 20.129999999999999, 'user_time': 40.810000000000002, 'sys_time': 7.3899999999999997}, 'errors': 0}
        self.assert_parsed(line, values)

        line = "2011-05-12T15:18:32.265+0000: 53123.386: [CMS-concurrent-preclean: 0.038/0.039 secs] [Times: user=0.03 sys=0.00, real=0.04 secs]"
        values = {'errors': 0, 'cms_concurrent_preclean': {'count': 1.0, 'real_time': 0.040000000000000001, 'user_time': 0.029999999999999999, 'sys_time': 0.0}}
        self.assert_parsed(line, values)

    def testPSY(self):
        line = "2011-05-11T04:24:20.339+0000: 1.012: [GC [PSYoungGen: 96640K->640K(112704K)] 96640K->640K(370368K), 0.0123710 secs] [Times: user=0.07 sys=0.00, real=0.02 secs]"
        values = {'errors': 0, 'ps_young_gen': {'count': 1.0, 'newgen_kb_collected': 96000.0, 'total_kb_collected': 96000.0, 'sys_time': 0.0, 'real_time': 0.02, 'user_time': 0.070000000000000007}}
        self.assert_parsed(line, values)

    def testIgnore(self):
        lines = ["par new generation total 2831168K, used 2384921K [0x00007f32c0fc0000, 0x00007f3380fc0000, 0x00007f3380fc0000) ",
         "eden space 2516608K, 90% used [0x00007f32c0fc0000, 0x00007f334b60c350, 0x00007f335a960000) ",
         " from space 314560K, 37% used [0x00007f335a960000, 0x00007f3361c1a490, 0x00007f336dc90000) ",
         " to space 314560K, 0% used [0x00007f336dc90000, 0x00007f336dc90000, 0x00007f3380fc0000) ",
         "concurrent mark-sweep generation total 9437184K, used 3087239K [0x00007f3380fc0000, 0x00007f35c0fc0000, 0x00007f35c0fc0000)",
         "concurrent-mark-sweep perm gen total 41104K, used 24528K [0x00007f35c0fc0000, 0x00007f35c37e4000, 0x00007f35c63c0000) "]
        values = {'errors': 0}
        for line in lines:
            self.assert_parsed(line, values)

    def testMultipleTypes(self):
        linePSY = "2011-05-11T04:24:20.339+0000: 1.012: [GC [PSYoungGen: 96640K->640K(112704K)] 96640K->640K(370368K), 0.0123710 secs] [Times: user=0.07 sys=0.00, real=0.02 secs]"
        lineFull = "2011-05-16T19:01:49.148+0000: 6.888: [Full GC 6.906: [CMS: 22065K->39440K(7340032K), 0.3012410 secs] 240184K->39440K(8283776K), [CMS Perm : 35150K->35025K(35236K)], 0.3014270 secs] [Times: user=0.30 sys=0.01, real=0.32 secs]"
        values = {'errors': 0, 'ps_young_gen': {'count': 1.0, 'newgen_kb_collected': 96000.0, 'total_kb_collected': 96000.0, 'sys_time': 0.0, 'real_time': 0.02, 'user_time': 0.070000000000000007}, 'full': {'count': 1.0, 'total_kb_collected': 401488.0, 'permgen_kb_collected': 125.0, 'sys_time': 0.01, 'real_time': 0.32000000000000001, 'oldgen_kb_collected': -17375.0, 'user_time': 0.29999999999999999}}
        p = Parser.Parser()
        p.parse(linePSY)
        p.parse(lineFull)
        self.assertEqual(p.data, values)

    def testOptionalDateStamps(self):
        lineWith = "2011-02-26T18:01:07.838+0000: 43317.137: [GC 43317.137: [ParNew (promotion failed): 2658599K->2583089K(2831168K), 0.5888520 secs]43317.726: [CMS: 6913520K->591225K(9437184K), 4.3637290 secs] 9527815K->591225K(12268352K), [CMS Perm : 24617K->24383K(41104K)], 4.9529780 secs] [Times: user=5.85 sys=0.02, real=4.95 secs]"
        lineWithout = "43317.137: [GC 43317.137: [ParNew (promotion failed): 2658599K->2583089K(2831168K), 0.5888520 secs]43317.726: [CMS: 6913520K->591225K(9437184K), 4.3637290 secs] 9527815K->591225K(12268352K), [CMS Perm : 24617K->24383K(41104K)], 4.9529780 secs] [Times: user=5.85 sys=0.02, real=4.95 secs]"

        p = Parser.Parser()

        p.parse(lineWith)
        v1 = p.getData()

        p.parse(lineWithout)
        v2 = p.getData()

        self.assertEqual(v1, v2)



def suite():
    tests = ['testParserSingleton', 'testParNew',
            'testFull', 'testFulln', 'testCMSc',
            'testPSY', 'testIgnore', 'testMultipleTypes',
            'testOptionalDateStamps'
            ]

    return unittest.TestSuite(map(TestParser, tests))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
