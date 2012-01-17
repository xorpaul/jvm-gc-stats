#! /usr/bin/env python
"""
 Filename: json_stats_fetcher.py
 Version: 0.9
 Requires: sys, urilib2, base64, optparse, time, socket, logging
 Date: 2012-01-17 14:49
 Author: Andreas Paul
"""

desc = """Fetch JSON formated website and push metrics to ganglia"""

epilog = """
Example call:
%prog -H foobar.enbw.net -p 12345 -u /pretty=1 -a 'foo:bar'"""

import sys
import urllib2
import base64
import socket
import logging
import time
from optparse import OptionParser

try:
    import json
except ImportError:
    import simplejson as json

def main():
    """ Sends HTTP-Request and parses the JSON response to call gmetric

    """
    usage = 'usage: %prog [options]'
    parser = OptionParser(usage, version="%prog 0.9",
                                description=desc)

    parser.add_option('-H', '--Host', dest='host',
                      help='host to send the SOAP request to')
    parser.add_option('-p', '--port', dest='port', type='int',
                      default=5000,
                      help='port to use on the target host')
    parser.add_option('-P', '--prefix', dest='prefix', type='string',
                      default='',
                      help='optional prefix for ganglia names')
    parser.add_option('-u', '--uri', dest='uri', type='string',
                      default='/',
                      help='URI. which will be called')
    parser.add_option('-a', '--auth', dest='credentials',
                      help='username and password in \''
                      '\' and seperated with :')
    parser.add_option('-t', '--timeout', dest='timeout', type='int',
                      default=15,
                      help='seconds to expect a result from the server '
                                                '(default: %default)')
    parser.add_option('-d', '--dmax', dest='stat_timeout', type='int',
                    default=5*60, help='The lifetime in seconds of this metric')
    parser.add_option('-v', '--verbose', dest='debug', action='store_true',
                    default=False, help='print additional debug information')

    # read parameters
    (options, args) = parser.parse_args()

    # Making sure all mandatory options appeared.
    mandatories = {'host': 'H'}

    for m in mandatories:
        if not options.__dict__[m]:
            return sys.exit(
                    'mandatory option -%s for %s is missing! Try --help' % (
                                    mandatories[m], m))

    # Format der Credentials checken
    if options.credentials and ':' not in options.credentials:
        return retNagios('u',
             'Credentials given in invalid format! Expecting foo:bar')

    # additional debug information
    # create logger
    logger = logging.getLogger()
    if options.debug:
        from pprint import pprint
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.ERROR)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

    logger.info('sys.args: n %s' % str(sys.argv))
    logger.info('using for host: %s' % (options.host))
    logger.info('using for port: %s' % (options.port))
    logger.info('using for uri: %s' % (options.uri))
    logger.info('using for prefix: %s' % (options.prefix))
    logger.info('using for credentials: %s' % (options.credentials))
    logger.info('using for timeout threshold: %s' % (options.timeout))
    logger.info('using for stat_timeout: %s' % (options.stat_timeout))

    # send the GET request
    try:
        socket.setdefaulttimeout(options.timeout)
        start = time.time()
        feed = urllib2.urlopen(createRequest(options.host, options.port,
                      options.credentials, options.uri))
        end = time.time()

    # Exception handeling v1.3
    except IOError, e:
        if hasattr(e, 'code'):
            if e.code == 401:
                return sys.exit('Wrong username/password! %s' % (e))
            elif e.code == 404:     # Site not found
                return sys.exit('Page \'%s\' not found! %s' % (e, options.uri))
            elif e.code == 500:
                return  sys.exit(
                        'Server Error! Check destination URI! %s' % (e))
            elif e.code == 503:     # Service Unavailable
                return sys.exit('Server Error!: %s' % (e))
            else:
                return sys.exit('Unexpected error: %s' % (e))
        elif e.reason:     # timeout, unreachable and wildcard
            if e.reason.args[0] == 'timed out':
                return sys.exit(
                            'Server response timed out! >%is %s' % (
                                options.timeout, e))
            elif e.reason[1] == 'Name or service not known':
                return sys.exit('Server not reachable! %s' % (e))
            else:
                return sys.exit('Error %s - %s' % (e.reason[1], e))
        else:
            return sys.exit('Error: %s' % (e))
    except:
            return sys.exit('Unexpected error: %s' % sys.exc_info()[0])

    output = feed.read()     # Read server response
    logger.info('server response: %s' % (output))



    # Check for correct type
    try:
        resultDict = json.loads(output)
    except TypeError, e:
        print "ERROR %s: %s" % (TypeError, e)
        print "received '%s' of type %s" % (output, type(output))
        sys.exit(1)


    #if options.debug:
    #    pprint(resultDict)
    #    print "key: %s - values: %s" % (k, v)

    for k, v in resultDict.iteritems():
        #xor
        if k == 'errors':
            print "gmetric -t int16 -n \"%s%s\" -v \"%s\" -u \"Errors\" -d %i" % (options.prefix, k, v, options.stat_timeout)
        else:
            for k1, v1 in resultDict[k].iteritems():
                for k2, v2 in resultDict[k][k1].iteritems():
                    if k2.endswith('_time'):
                        print "gmetric -t float -n \"%s%s\" -v \"%s\" -u \"Seconds\" -d %i" % (options.prefix, k+'.'+k1+'.'+k2, v2, options.stat_timeout)
                    elif k2.endswith('_collected'):
                        print "gmetric -t int16 -n \"%s%s\" -v \"%s\" -u \"Kilobytes\" -d %i" % (options.prefix, k+'.'+k1+'.'+k2, v2, options.stat_timeout)


def createRequest(host, port, credentials, uri):
    """ Creates the HTTP-Request with optional Basic-Auth Header

    Prepares the HTTP-Request by using the target host and port of the endpoint.

    Args:
        host: taget host
        port: port on which the target host listens
        credentials: username and password as one string and separated with a :
        uri: target uri, which will be appended to the URL

    Returns:
        req: Prepared HTTP Request with target host, port and 
            optional Basic-Auth Header
    """
    url = ('http://%s:%i/%s') % (host, port, uri)

    logging.info('sending GET-Request to %s' % (url))

    request = urllib2.Request(url)

    if credentials:
        base64string = base64.encodestring('%s' % (credentials))[:-1]
        authheader = 'Basic %s' % base64string
        request.add_header('Authorization', authheader)

    return request

if __name__ == '__main__' or __name__ == sys.argv[0]:
    sys.exit(main())
