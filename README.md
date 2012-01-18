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
$ curl http://YOURIP:5000
{"errors": 0}
# you can test it by using the example files
$ cat gc-example-without-timestamps >> gc.log && cat gc-example-with-timestamps >> gc.log.1
$ curl http://YOURIP:5000
{"test2": {"par_new": {"count": 28, "newgen_kb_collected": 728113, "avg_real_time": "0.01", "max_user_time": "0.05", "avg_newgen_kb_collected": 26004, "avg_total_kb_collected": 25373, "total_kb_collected": 710460, "max_real_time": "0.03", "avg_user_time": "0.01", "max_sys_time": "0.01", "real_time": "0.19", "sys_time": "0.02", "avg_sys_time": "0.00", "avg_time_between_collections": "0.00", "user_time": "0.35"}, "full": {"count": 2, "permgen_kb_collected": 17, "newgen_kb_collected": 0, "avg_real_time": "0.12", "max_user_time": "0.14", "avg_newgen_kb_collected": 0, "avg_oldgen_kb_collected": -3340, "total_kb_collected": 38180, "avg_time_between_collections": "0.00", "max_real_time": "0.14", "avg_user_time": "0.14", "max_sys_time": "0.01", "avg_permgen_kb_collected": 8, "real_time": "0.25", "sys_time": "0.02", "oldgen_kb_collected": -6679, "avg_total_kb_collected": 19090, "avg_sys_time": "0.01", "user_time": "0.28"}}, "test1": {"cms_remark": {"count": 1, "avg_time_between_collections": "0.00", "avg_real_time": "0.00", "max_user_time": 0, "max_real_time": 0, "avg_user_time": "0.00", "max_sys_time": 0, "real_time": "0.00", "sys_time": "0.00", "avg_sys_time": "0.00", "user_time": "0.00"}, "full": {"count": 43, "permgen_kb_collected": 173, "newgen_kb_collected": 0, "avg_real_time": "0.12", "max_user_time": "0.43", "avg_newgen_kb_collected": 0, "avg_oldgen_kb_collected": 5420, "total_kb_collected": 506049, "avg_time_between_collections": "0.00", "max_real_time": "0.43", "avg_user_time": "0.11", "max_sys_time": "0.01", "avg_permgen_kb_collected": 4, "real_time": "5.10", "sys_time": "0.02", "oldgen_kb_collected": 233067, "avg_total_kb_collected": 11768, "avg_sys_time": "0.00", "user_time": "4.87"}, "cms_initial_mark": {"count": 2, "avg_time_between_collections": "0.00", "avg_real_time": "0.00", "max_user_time": 0, "max_real_time": 0, "avg_user_time": "0.00", "max_sys_time": 0, "real_time": "0.00", "sys_time": "0.00", "avg_sys_time": "0.00", "user_time": "0.00"}, "promotion_failure": {"count": 2, "permgen_kb_collected": 0, "newgen_kb_collected": 22447, "avg_real_time": "1.86", "max_user_time": "3.18", "avg_newgen_kb_collected": 11223, "avg_oldgen_kb_collected": 162279, "total_kb_collected": 1507825, "avg_time_between_collections": "0.00", "max_real_time": "3.20", "avg_user_time": "1.87", "max_sys_time": "0.07", "avg_permgen_kb_collected": 0, "real_time": "3.72", "sys_time": "0.07", "oldgen_kb_collected": 324558, "avg_total_kb_collected": 753912, "avg_sys_time": "0.04", "user_time": "3.74"}, "cms_concurrent_sweep": {"count": 1, "avg_time_between_collections": "0.00", "avg_real_time": "0.01", "max_user_time": "0.02", "max_real_time": "0.01", "avg_user_time": "0.02", "max_sys_time": 0, "real_time": "0.01", "sys_time": "0.00", "avg_sys_time": "0.00", "user_time": "0.02"}, "cms_concurrent_reset": {"count": 1, "avg_time_between_collections": "0.00", "avg_real_time": "0.00", "max_user_time": 0, "max_real_time": 0, "avg_user_time": "0.00", "max_sys_time": 0, "real_time": "0.00", "sys_time": "0.00", "avg_sys_time": "0.00", "user_time": "0.00"}, "par_new": {"count": 8, "newgen_kb_collected": 372040, "avg_real_time": "0.02", "max_user_time": "0.14", "avg_newgen_kb_collected": 46505, "avg_total_kb_collected": 25883, "total_kb_collected": 207069, "max_real_time": "0.05", "avg_user_time": "0.05", "max_sys_time": 0, "real_time": "0.17", "sys_time": "0.00", "avg_sys_time": "0.00", "avg_time_between_collections": "0.00", "user_time": "0.39"}, "cms_concurrent_mark": {"count": 2, "avg_time_between_collections": "0.00", "avg_real_time": "0.14", "max_user_time": "0.26", "max_real_time": "0.16", "avg_user_time": "0.19", "max_sys_time": 0, "real_time": "0.29", "sys_time": "0.00", "avg_sys_time": "0.00", "user_time": "0.38"}, "cms_concurrent_preclean": {"count": 1, "avg_time_between_collections": "0.00", "avg_real_time": "0.01", "max_user_time": "0.01", "max_real_time": "0.01", "avg_user_time": "0.01", "max_sys_time": 0, "real_time": "0.01", "sys_time": "0.00", "avg_sys_time": "0.00", "user_time": "0.01"}}, "errors": 0, "seconds_since_last_reset": "11.25"}
# or using pretty print:
$ curl http://YOURIP:5000/pretty=1
{
    "errors": 0,
    "seconds_since_last_reset": "19.93",
    "test1": {
        "cms_concurrent_mark": {
            "avg_real_time": "0.14",
            "avg_sys_time": "0.00",
            "avg_time_between_collections": "0.00",
            "avg_user_time": "0.19",
            "count": 2,
            "max_real_time": "0.16",
            "max_sys_time": 0,
            "max_user_time": "0.26",
            "real_time": "0.29",
            "sys_time": "0.00",
            "user_time": "0.38"
        },
        "cms_concurrent_preclean": {
            "avg_real_time": "0.01",
            "avg_sys_time": "0.00",
            "avg_time_between_collections": "0.00",
            "avg_user_time": "0.01",
            "count": 1,
            "max_real_time": "0.01",
            "max_sys_time": 0,
            "max_user_time": "0.01",
            "real_time": "0.01",
            "sys_time": "0.00",
            "user_time": "0.01"
        },
        "cms_concurrent_reset": {
            "avg_real_time": "0.00",
            "avg_sys_time": "0.00",
            "avg_time_between_collections": "0.00",
            "avg_user_time": "0.00",
            "count": 1,
            "max_real_time": 0,
            "max_sys_time": 0,
            "max_user_time": 0,
            "real_time": "0.00",
            "sys_time": "0.00",
            "user_time": "0.00"
        },
        "cms_concurrent_sweep": {
            "avg_real_time": "0.01",
            "avg_sys_time": "0.00",
            "avg_time_between_collections": "0.00",
            "avg_user_time": "0.02",
            "count": 1,
            "max_real_time": "0.01",
            "max_sys_time": 0,
            "max_user_time": "0.02",
            "real_time": "0.01",
            "sys_time": "0.00",
            "user_time": "0.02"
        },
        "cms_initial_mark": {
            "avg_real_time": "0.00",
            "avg_sys_time": "0.00",
            "avg_time_between_collections": "0.00",
            "avg_user_time": "0.00",
            "count": 2,
            "max_real_time": 0,
            "max_sys_time": 0,
            "max_user_time": 0,
            "real_time": "0.00",
            "sys_time": "0.00",
            "user_time": "0.00"
        },
        "cms_remark": {
            "avg_real_time": "0.00",
            "avg_sys_time": "0.00",
            "avg_time_between_collections": "0.00",
            "avg_user_time": "0.00",
            "count": 1,
            "max_real_time": 0,
            "max_sys_time": 0,
            "max_user_time": 0,
            "real_time": "0.00",
            "sys_time": "0.00",
            "user_time": "0.00"
        },
        "full": {
            "avg_newgen_kb_collected": 0,
            "avg_oldgen_kb_collected": 5420,
            "avg_permgen_kb_collected": 4,
            "avg_real_time": "0.12",
            "avg_sys_time": "0.00",
            "avg_time_between_collections": "0.00",
            "avg_total_kb_collected": 11768,
            "avg_user_time": "0.11",
            "count": 43,
            "max_real_time": "0.43",
            "max_sys_time": "0.01",
            "max_user_time": "0.43",
            "newgen_kb_collected": 0,
            "oldgen_kb_collected": 233067,
            "permgen_kb_collected": 173,
            "real_time": "5.10",
            "sys_time": "0.02",
            "total_kb_collected": 506049,
            "user_time": "4.87"
        },
        "par_new": {
            "avg_newgen_kb_collected": 46505,
            "avg_real_time": "0.02",
            "avg_sys_time": "0.00",
            "avg_time_between_collections": "0.00",
            "avg_total_kb_collected": 25883,
            "avg_user_time": "0.05",
            "count": 8,
            "max_real_time": "0.05",
            "max_sys_time": 0,
            "max_user_time": "0.14",
            "newgen_kb_collected": 372040,
            "real_time": "0.17",
            "sys_time": "0.00",
            "total_kb_collected": 207069,
            "user_time": "0.39"
        },
        "promotion_failure": {
            "avg_newgen_kb_collected": 11223,
            "avg_oldgen_kb_collected": 162279,
            "avg_permgen_kb_collected": 0,
            "avg_real_time": "1.86",
            "avg_sys_time": "0.04",
            "avg_time_between_collections": "0.00",
            "avg_total_kb_collected": 753912,
            "avg_user_time": "1.87",
            "count": 2,
            "max_real_time": "3.20",
            "max_sys_time": "0.07",
            "max_user_time": "3.18",
            "newgen_kb_collected": 22447,
            "oldgen_kb_collected": 324558,
            "permgen_kb_collected": 0,
            "real_time": "3.72",
            "sys_time": "0.07",
            "total_kb_collected": 1507825,
            "user_time": "3.74"
        }
    },
    "test2": {
        "full": {
            "avg_newgen_kb_collected": 0,
            "avg_oldgen_kb_collected": -3340,
            "avg_permgen_kb_collected": 8,
            "avg_real_time": "0.12",
            "avg_sys_time": "0.01",
            "avg_time_between_collections": "0.00",
            "avg_total_kb_collected": 19090,
            "avg_user_time": "0.14",
            "count": 2,
            "max_real_time": "0.14",
            "max_sys_time": "0.01",
            "max_user_time": "0.14",
            "newgen_kb_collected": 0,
            "oldgen_kb_collected": -6679,
            "permgen_kb_collected": 17,
            "real_time": "0.25",
            "sys_time": "0.02",
            "total_kb_collected": 38180,
            "user_time": "0.28"
        },
        "par_new": {
            "avg_newgen_kb_collected": 26004,
            "avg_real_time": "0.01",
            "avg_sys_time": "0.00",
            "avg_time_between_collections": "0.00",
            "avg_total_kb_collected": 25373,
            "avg_user_time": "0.01",
            "count": 28,
            "max_real_time": "0.03",
            "max_sys_time": "0.01",
            "max_user_time": "0.05",
            "newgen_kb_collected": 728113,
            "real_time": "0.19",
            "sys_time": "0.02",
            "total_kb_collected": 710460,
            "user_time": "0.35"
        }
    }
}
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
