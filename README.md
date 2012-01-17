JVM-GC-STATS
============

SUMMARY
-------
A python script to parse Java Virtual Machine (JVM) garbage collection
trace output, push the data into Ganglia and alert on anomolies.
The data and graphs produced are intended to support operational
monitoring and inform GC tuning decisions.

The JVM is assumed to be Java6 and invoked with the following flags:

    -XX:+UseConcMarkSweepGC
    -verbosegc
    -XX:+PrintGCDetails
    -XX:+PrintGCTimeStamps
    supports either
        -Xloggc:gc-`date +%F-%H-%M`.log
      or
        -Xloggc:gc.log

    optional: 
    -XX:+PrintGCDateStamps
    -XX:+PrintTenuringDistribution


DESCRIPTION
-------

    parse-gc.py -c CONFIGFILE

Will print GC metrics in JSON format for every line it can parse.
Collected data can be cleared if the URI in the GET requests contains reset=1


Example calls:

    parse-gc.py -c config/example.conf

Example config file:
<pre>
# [general]
# port at which the HTTP server will run
# port: 5000
# If no general config section is found the
# default values 5000 for port and 1 second sleeptime between logfile
# seeks will be used.

# [services]
# SERVICENAME: logfile
# GC logfile you want to follow and parse with fuzzy name support
# The script will use the file with the most recent ctime
# noticed logrotate from gc-2012-01-15-21-08.log to gc-2012-01-15-21-09.log
# noticed logrotate in gc-2012-01-15-21-09.log

[services]
test1: /var/log/jvm/gc-*.log
test2: gc.log
</pre>
USAGE
-------
<pre>
# start the parse script
$ ./parse-gc.py -c config/example.conf
# and call it from another server / shell
$ curl http://YOURHOSTNAME:5000
{"errors": 0}
# you can test it by using the example files
$ cat gc-example-without-timestamps >> gc.log && cat gc-example-with-timestamps >> gc.log.1
$ curl http://YOURHOSTNAME:5000
{"test2": {"par_new": {"count": 28, "newgen_kb_collected": 728113, "total_kb_collected": 710460, "sys_time": "0.02", "real_time": "0.19", "user_time": "0.35"}, "full": {"count": 2, "total_kb_collected": 76360, "permgen_kb_collected": 17, "sys_time": "0.02", "real_time": "0.25", "oldgen_kb_collected": -6679, "user_time": "0.28"}}, "test1": {"cms_remark": {"count": 1, "real_time": "0.00", "user_time": "0.00", "sys_time": "0.00"}, "full": {"count": 43, "total_kb_collected": 1012098, "permgen_kb_collected": 173, "sys_time": "0.02", "real_time": "5.10", "oldgen_kb_collected": 233067, "user_time": "4.87"}, "cms_initial_mark": {"count": 2, "real_time": "0.00", "user_time": "0.00", "sys_time": "0.00"}, "promotion_failure": {"count": 2, "newgen_kb_collected": 22447, "total_kb_collected": 1507825, "permgen_kb_collected": 0, "sys_time": "0.07", "real_time": "3.72", "oldgen_kb_collected": 324558, "user_time": "3.74"}, "cms_concurrent_sweep": {"count": 1, "real_time": "0.01", "user_time": "0.02", "sys_time": "0.00"}, "cms_concurrent_reset": {"count": 1, "real_time": "0.00", "user_time": "0.00", "sys_time": "0.00"}, "par_new": {"count": 8, "newgen_kb_collected": 372040, "total_kb_collected": 207069, "sys_time": "0.00", "real_time": "0.17", "user_time": "0.39"}, "cms_concurrent_mark": {"count": 2, "real_time": "0.29", "user_time": "0.38", "sys_time": "0.00"}, "cms_concurrent_preclean": {"count": 1, "real_time": "0.01", "user_time": "0.01", "sys_time": "0.00"}}, "errors": 0}
</pre>
Fork from:
<pre>
jkalucki https://github.com/jkalucki/jvm-gc-stats
|_________ ryanking https://github.com/ryanking/jvm-gc-stats
                |_________ this here
</pre>
LICENSE
-------
Apache 2.0 License. See included license file.
