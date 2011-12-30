#! /usr/bin/env python
"""
 Version: 0.9
 Requires: sys, optparse
 Date: 2011-12-04 13:38
 Author: Andreas Paul
"""

desc = """Parse and record gc logs generated by the JVM"""

epilog = """Example call:
%prog -f /usr/share/tomcat7/logs/gc.log"""

import sys
from optparse import OptionParser

from lib import *

def main():
    """ Parse and record gc logs generated by the JVM

    Desc TODO:

    Args:
        None

    Returns:
        Will print GC metrics in JSON format for every line it can parse.
    """

    usage = 'usage: %prog [options]'
    parser = OptionParser(usage, version="%prog 0.9",
                                description=desc)

    parser.add_option('-f', '--logfile', dest='logfile',
                    help='GC logfile you want to follow and parse')
    parser.add_option('-p', '--port', dest='port', default='5000', type='int',
                    help='port at which the HTTP server will run')

    (options, args) = parser.parse_args()

    # Making sure all mandatory options appeared.
    mandatories = {'logfile': 'f'}

    for m in mandatories:
        if not options.__dict__[m]:
            print ('mandatory option -%s for %s is missing! Try --help' % (
                    mandatories[m], m))
            sys.exit(1)

    #logfile = "/var/log/tc7_test/gc.log"
    t = Tailer.Tailer(options.logfile)
    p = Parser.Parser()
    s = Server.Server(options.port, p, t)

    try:
        s.serve()
    except (KeyboardInterrupt, SystemExit):
        print "exiting main..."
        sys.excepthook(*sys.exc_info())

    return 0


if __name__ == '__main__' or __name__ == sys.argv[0]:
    sys.exit(main())    # call main subroutine

