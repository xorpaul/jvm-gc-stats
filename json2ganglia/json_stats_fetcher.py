#! /usr/bin/env python
"""
 Filename: json_stats_fetcher.py
 Version: 0.9
 Requires: sys, urilib2, base64, optparse, time, socket, logging
 Date: 2012-01-17 14:49
 Author: Andreas Paul
"""

desc = """Fetch JSON formated website and push metrics to ganglia via gmetric"""

epilog = """
Example call:
%prog -H foobar
or
%prog -H foobar -p 12345 -u /pretty=1 -a 'foo:bar'"""

import os
import sys
import urllib2
import base64
import socket
import logging
import time
import thread
import ConfigParser
from optparse import OptionParser

try:
    import json
except ImportError:
    import simplejson as json

from gmetric import Gmetric, gmetric_write

GMETRIC = '/usr/bin/gmetric'


def main():
    """ Sends HTTP-Request and parses the JSON response to call gmetric with it
    """
    usage = 'usage: %prog -c CONFIGFILE'
    parser = OptionParser(usage, version="%prog 0.9",
                                description=desc)

    parser.add_option('-c', '--configfile', dest='configfile',
                      help='configfile with server IP and port')
    parser.add_option('-t', '--timeout', dest='timeout', type='int',
                      default=5,
                      help='seconds to expect a result from the server '
                                                '(default: %default)')
    parser.add_option('-n', '--dryrun', dest='dryrun', action='store_true',
                    default=False, help='only print the gmetric calls, don\'t execute them')
    parser.add_option('-v', '--verbose', dest='debug', action='store_true',
                    default=False, help='print additional debug information')

    # read parameters
    (options, args) = parser.parse_args()

    # Making sure all mandatory options appeared.
    mandatories = {'configfile': 'c'}

    for m in mandatories:
        if not options.__dict__[m]:
            return sys.exit(
                    'mandatory option -%s for %s is missing! Try --help' % (
                                    mandatories[m], m))

    if not os.path.exists(options.configfile):
        print 'config file %s not found!' % options.configfile
        sys.exit(1)

    config = ConfigParser.ConfigParser()
    config.read(options.configfile)

    servers = []
    for server in config.sections():
        # port and dmax default values
        host, port, spoof, dmax = None, 50000, None, 65
        if config.has_option(server, 'host'):
            host = config.get(server, 'host')
        else:
            print 'Didn\'t find \'host\' attribute in config section %s, but it is mandatory!' % server
            sys.exit(1)
        if config.has_option(server, 'port'):
            port = config.get(server, 'port')
        if config.has_option(server, 'dmax'):
            dmax = config.get(server, 'dmax')
        else:
            dmax = 65
        if config.has_option(server, 'spoof'):
            spoof = config.get(server, 'spoof')
        else:
            spoof = '%s:%s' % (host, server)
        servers.append({'host': host, 'port': port, 'spoof': spoof, 'dmax': dmax})


    #print servers
    #sys.exit(1)

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
    logger.info('using for configfile: %s' % (options.configfile))
    logger.info('using for timeout threshold: %s' % (options.timeout))

    for server in servers:
        options.uri = '/'
        options.host = server['host']
        options.port = int(server['port'])
        options.spoof = server['spoof']
        options.dmax = server['dmax']

        # send the GET request
        try:
            socket.setdefaulttimeout(options.timeout)
            start = time.time()
            feed = urllib2.urlopen(createRequest(options.host, options.port,
                          options.uri))
            end = time.time()

        # Exception handeling v1.3
        except IOError, e:
            print "failed with http://%s:%i%s" % (options.host, options.port, options.uri)
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

        output = feed.read()     # Read server response
        logger.info('server response: %s' % (output))
        logger.info('server response time: %i' % (end - start))

        # Check for correct type
        try:
            resultDict = json.loads(output)
        except TypeError, e:
            print "ERROR %s: %s" % (TypeError, e)
            print "received '%s' of type %s" % (output, type(output))
            sys.exit(1)

        #print "server response time: %i" % (end - start)
        parseResponse(resultDict, options)

def parseResponse(resultDict, options):
    #if options.debug:
    #    pprint(resultDict)
    #    print "key: %s - values: %s" % (k, v)

    for service, v in resultDict.iteritems():
        #xor
        if service == 'errors':
            callGmetric(options.spoof, 'general', service, v,
                'int16', 'Errors', options.dmax, options.dryrun)
        elif service == 'seconds_since_last_reset':
            callGmetric(options.spoof, 'general', service, v,
                'float', 'Seconds', options.dmax, options.dryrun)
        else:
            for gctype, service_metric_value in resultDict[service].iteritems():
                if gctype == 'count':
                    callGmetric(options.spoof, service, service+'.'+gctype, service_metric_value,
                        'int16', 'count', options.dmax, options.dryrun)
                elif gctype == 'avg_time_between_any_type_collections':
                    callGmetric(options.spoof, service, service+'.'+gctype, service_metric_value,
                        'float', 'Seconds', options.dmax, options.dryrun)
                elif ('allocated') in gctype:
                    callGmetric(options.spoof, service, service+'.'+gctype, service_metric_value,
                        'int16', 'Kilobytes', options.dmax, options.dryrun)
                else:
                    for metric, value in resultDict[service][gctype].iteritems():
                        if ('time') in metric:
                            callGmetric(options.spoof, service, service+'.'+gctype+'.'+metric, value,
                                'float', 'Seconds', options.dmax, options.dryrun)
                        elif metric.endswith('_collected'):
                            callGmetric(options.spoof, service, service+'.'+gctype+'.'+metric, value,
                                'int16', 'Kilobytes', options.dmax, options.dryrun)
                        elif metric == 'count':
                            callGmetric(options.spoof, service, service+'.'+gctype+'.'+metric, value,
                                'int16', 'count', options.dmax, options.dryrun)
                        else:
                            print "undefinded metric:", metric


def callGmetric(spoof, group, name, value, type, unit, dmax, dryrun):
    logger = logging.getLogger()
    logger.info('%s --group=%s --spoof=%s --name=%s --value=%s --type=%s --units=\'%s\' '
        '--dmax=%i' % (GMETRIC, group, spoof, name, value, type, unit, dmax))

    if dryrun:
        print ('%s --group=%s --spoof=%s --name=%s --value=%s --type=%s --units=\'%s\' '
            '--dmax=%i' % (GMETRIC, group, spoof, name, value, type, unit, dmax))

    else:
        os.spawnl(os.P_NOWAIT, GMETRIC, 'gmetric',
            '--group=%s' % group,
            '--spoof=%s' % spoof,
            '--name=%s' % name,
            '--value=%s' % value,
            '--type=%s' % type,
            '--units=\'%s\'' % unit,
            '--dmax=%i' % dmax)


def createRequest(host, port, uri):
    """ Creates the HTTP-Request with optional Basic-Auth Header

    Prepares the HTTP-Request by using the target host and port of the endpoint.

    Args:
        host: taget host
        port: port on which the target host listens
        uri: target uri, which will be appended to the URL

    Returns:
        req: Prepared HTTP Request with target host, port and 
            optional Basic-Auth Header
    """
    url = ('http://%s:%i%s') % (host, int(port), uri)

    logging.info('sending GET-Request to %s' % (url))

    request = urllib2.Request(url)

    return request

if __name__ == '__main__' or __name__ == sys.argv[0]:
    sys.exit(main())
