#! /usr/bin/env python
import sys
sys.path.append("../")
import unittest
from lib import *

class TestParser(unittest.TestCase):
    def assert_parsed(self, line, values):
        p = Parser.Parser()
        p.parse(line, 'test')
        try:
            self.assertEqual(values, p.getData())
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
        values = {'test': {'par_new': {'count': 1, 'newgen_kb_collected': 838912, 'avg_real_time': '0.43', 'max_user_time': '1.93', 'avg_newgen_kb_collected': 838912, 'avg_total_kb_collected': 670013, 'total_kb_collected': 670013, 'max_real_time': '0.43', 'avg_user_time': '1.93', 'max_sys_time': '0.21', 'real_time': '0.43', 'sys_time': '0.21', 'avg_sys_time': '0.21', 'avg_time_between_collections': '0.00', 'user_time': '1.93'}}, 'errors': 0, 'seconds_since_last_reset': 0}
        self.assert_parsed(line, values)

    def testFull(self):
        line = "2011-05-16T19:01:49.148+0000: 6.888: [Full GC 6.906: [CMS: 22065K->39440K(7340032K), 0.3012410 secs] 240184K->39440K(8283776K), [CMS Perm : 35150K->35025K(35236K)], 0.3014270 secs] [Times: user=0.30 sys=0.01, real=0.32 secs]"
        values = {'test': {'full': {'count': 1, 'permgen_kb_collected': 125, 'newgen_kb_collected': 0, 'avg_real_time': '0.32', 'max_user_time': '0.30', 'avg_newgen_kb_collected': 0, 'avg_oldgen_kb_collected': -17375, 'total_kb_collected': 200744, 'avg_time_between_collections': '0.00', 'max_real_time': '0.32', 'avg_user_time': '0.30', 'max_sys_time': '0.01', 'avg_permgen_kb_collected': 125, 'real_time': '0.32', 'sys_time': '0.01', 'oldgen_kb_collected': -17375, 'avg_total_kb_collected': 200744, 'avg_sys_time': '0.01', 'user_time': '0.30'}}, 'errors': 0, 'seconds_since_last_reset': 0}
        self.assert_parsed(line, values)

    def testFulln(self):
        line = "2011-05-11T04:28:36.398+0000: 257.070: [Full GC [PSYoungGen: 3936K->0K(85760K)] [ParOldGen: 252218K->120734K(221056K)] 256154K->120734K(306816K) [PSPermGen: 12177K->12153K(24896K)], 0.3264320 secs] [Times: user=2.75 sys=0.21, real=0.33 secs]"
        values = {'test': {'full': {'count': 1, 'permgen_kb_collected': 24, 'newgen_kb_collected': 3936, 'avg_real_time': '0.33', 'max_user_time': '2.75', 'avg_newgen_kb_collected': 3936, 'avg_oldgen_kb_collected': 131484, 'total_kb_collected': 135420, 'avg_time_between_collections': '0.00', 'max_real_time': '0.33', 'avg_user_time': '2.75', 'max_sys_time': '0.21', 'avg_permgen_kb_collected': 24, 'real_time': '0.33', 'sys_time': '0.21', 'oldgen_kb_collected': 131484, 'avg_total_kb_collected': 135420, 'avg_sys_time': '0.21', 'user_time': '2.75'}}, 'errors': 0, 'seconds_since_last_reset': 0}
        self.assert_parsed(line, values)

    def testCMSc(self):
        line = "2011-05-12T15:18:32.227+0000: 53123.348: [CMS-concurrent-mark: 3.332/3.333 secs] [Times: user=13.02 sys=0.31, real=3.33 secs]"
        values = {'test': {'cms_concurrent_mark': {'count': 1, 'avg_time_between_collections': '0.00', 'avg_real_time': '3.33', 'max_user_time': '13.02', 'max_real_time': '3.33', 'avg_user_time': '13.02', 'max_sys_time': '0.31', 'real_time': '3.33', 'sys_time': '0.31', 'avg_sys_time': '0.31', 'user_time': '13.02'}}, 'errors': 0, 'seconds_since_last_reset': 0}
        self.assert_parsed(line, values)

        line = "2011-02-26T06:22:39.421+0000: 1408.720: [CMS-concurrent-sweep: 20.008/20.126 secs] [Times: user=40.81 sys=7.39, real=20.13 secs]"
        values = {'test': {'cms_concurrent_sweep': {'count': 1, 'avg_time_between_collections': '0.00', 'avg_real_time': '20.13', 'max_user_time': '40.81', 'max_real_time': '20.13', 'avg_user_time': '40.81', 'max_sys_time': '7.39', 'real_time': '20.13', 'sys_time': '7.39', 'avg_sys_time': '7.39', 'user_time': '40.81'}}, 'errors': 0, 'seconds_since_last_reset': 0}
        self.assert_parsed(line, values)

        line = "2011-05-12T15:18:32.265+0000: 53123.386: [CMS-concurrent-preclean: 0.038/0.039 secs] [Times: user=0.03 sys=0.00, real=0.04 secs]"
        values = {'test': {'cms_concurrent_preclean': {'count': 1, 'avg_time_between_collections': '0.00', 'avg_real_time': '0.04', 'max_user_time': '0.03', 'max_real_time': '0.04', 'avg_user_time': '0.03', 'max_sys_time': 0, 'real_time': '0.04', 'sys_time': '0.00', 'avg_sys_time': '0.00', 'user_time': '0.03'}}, 'errors': 0, 'seconds_since_last_reset': 0}
        self.assert_parsed(line, values)

    def testPSY(self):
        line = "2011-05-11T04:24:20.339+0000: 1.012: [GC [PSYoungGen: 96640K->640K(112704K)] 96640K->640K(370368K), 0.0123710 secs] [Times: user=0.07 sys=0.00, real=0.02 secs]"
        values = {'test': {'ps_young_gen': {'count': 1, 'newgen_kb_collected': 96000, 'avg_real_time': '0.02', 'max_user_time': '0.07', 'avg_newgen_kb_collected': 96000, 'avg_total_kb_collected': 96000, 'total_kb_collected': 96000, 'max_real_time': '0.02', 'avg_user_time': '0.07', 'max_sys_time': 0, 'real_time': '0.02', 'sys_time': '0.00', 'avg_sys_time': '0.00', 'avg_time_between_collections': '0.00', 'user_time': '0.07'}}, 'errors': 0, 'seconds_since_last_reset': 0}
        self.assert_parsed(line, values)

    def testProFail(self):
        line = "1427148.896: [GC 1427148.896: [DefNew (promotion failed) : 1173076K->1150629K(1228800K), 0.5152270 secs]1427149.411: [Tenured: 1310719K->1031593K(1310720K), 2.6800290 secs] 2474868K->1031593K(2539520K), [Perm : 185208K->185208K(185344K)], 3.1954800 secs] [Times: user=3.18 sys=0.00, real=3.20 secs] \n"
        values = {'test': {'promotion_failure': {'count': 1, 'permgen_kb_collected': 0, 'newgen_kb_collected': 22447, 'avg_real_time': '3.20', 'max_user_time': '3.18', 'avg_newgen_kb_collected': 22447, 'avg_oldgen_kb_collected': 279126, 'total_kb_collected': 1443275, 'avg_time_between_collections': '0.00', 'max_real_time': '3.20', 'avg_user_time': '3.18', 'max_sys_time': 0, 'avg_permgen_kb_collected': 0, 'real_time': '3.20', 'sys_time': '0.00', 'oldgen_kb_collected': 279126, 'avg_total_kb_collected': 1443275, 'avg_sys_time': '0.00', 'user_time': '3.18'}}, 'errors': 0, 'seconds_since_last_reset': 0}
        self.assert_parsed(line, values)

    def testMultipleTypes(self):
        linePSY = "2011-05-11T04:24:20.339+0000: 1.012: [GC [PSYoungGen: 96640K->640K(112704K)] 96640K->640K(370368K), 0.0123710 secs] [Times: user=0.07 sys=0.00, real=0.02 secs]"
        lineFull = "2011-05-16T19:01:49.148+0000: 6.888: [Full GC 6.906: [CMS: 22065K->39440K(7340032K), 0.3012410 secs] 240184K->39440K(8283776K), [CMS Perm : 35150K->35025K(35236K)], 0.3014270 secs] [Times: user=0.30 sys=0.01, real=0.32 secs]"
        values = {'test': {'full': {'count': 1, 'permgen_kb_collected': 125, 'newgen_kb_collected': 0, 'avg_real_time': '0.32', 'max_user_time': '0.30', 'avg_newgen_kb_collected': 0, 'avg_oldgen_kb_collected': -17375, 'total_kb_collected': 200744, 'avg_time_between_collections': '0.00', 'max_real_time': '0.32', 'avg_user_time': '0.30', 'max_sys_time': '0.01', 'avg_permgen_kb_collected': 125, 'real_time': '0.32', 'sys_time': '0.01', 'oldgen_kb_collected': -17375, 'avg_total_kb_collected': 200744, 'avg_sys_time': '0.01', 'user_time': '0.30'}, 'ps_young_gen': {'count': 1, 'newgen_kb_collected': 96000, 'avg_real_time': '0.02', 'max_user_time': '0.07', 'avg_newgen_kb_collected': 96000, 'avg_total_kb_collected': 96000, 'total_kb_collected': 96000, 'max_real_time': '0.02', 'avg_user_time': '0.07', 'max_sys_time': 0, 'real_time': '0.02', 'sys_time': '0.00', 'avg_sys_time': '0.00', 'avg_time_between_collections': '0.00', 'user_time': '0.07'}}, 'errors': 0, 'seconds_since_last_reset': 0}
        p = Parser.Parser()
        p.parse(linePSY, 'test')
        p.parse(lineFull, 'test')
        self.assertEqual(p.data, values)

    def testOptionalDateStamps(self):
        lineWith = "2011-02-26T18:01:07.838+0000: 43317.137: [GC 43317.137: [ParNew (promotion failed): 2658599K->2583089K(2831168K), 0.5888520 secs]43317.726: [CMS: 6913520K->591225K(9437184K), 4.3637290 secs] 9527815K->591225K(12268352K), [CMS Perm : 24617K->24383K(41104K)], 4.9529780 secs] [Times: user=5.85 sys=0.02, real=4.95 secs]"
        lineWithout = "43317.137: [GC 43317.137: [ParNew (promotion failed): 2658599K->2583089K(2831168K), 0.5888520 secs]43317.726: [CMS: 6913520K->591225K(9437184K), 4.3637290 secs] 9527815K->591225K(12268352K), [CMS Perm : 24617K->24383K(41104K)], 4.9529780 secs] [Times: user=5.85 sys=0.02, real=4.95 secs]"

        p = Parser.Parser()

        p.parse(lineWith, 'test')
        v1 = p.getData()

        p.parse(lineWithout, 'test')
        v2 = p.getData()

        self.assertEqual(v1, v2)



def suite():
    tests = ['testParserSingleton', 'testParNew',
            'testFull', 'testFulln', 'testCMSc',
            'testPSY', 'testProFail', 'testMultipleTypes',
            'testOptionalDateStamps'
            ]

    return unittest.TestSuite(map(TestParser, tests))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
